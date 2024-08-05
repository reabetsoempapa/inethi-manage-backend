from rest_framework.views import APIView, Response
from rest_framework import status
from web3 import Web3
from dotenv import load_dotenv
import os
from .models import Wallet, decrypt_private_key
from users.models import User
from jose import jwt, JWTError, ExpiredSignatureError
import logging
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile, File
import qrcode  # Import qrcode module

from django.shortcuts import render
from jwt.exceptions import InvalidAlgorithmError

import json
from jose import jwt, JWTError, ExpiredSignatureError
from io import BytesIO

load_dotenv()

# Get an instance of a logger
logger = logging.getLogger('general')
logger.info("qrcode module successfully imported")

def load_contract_abi(file_name):
    file_path = os.path.join(settings.BASE_DIR, 'wallet', file_name)
    with open(file_path, 'r') as abi_file:
        return json.load(abi_file)

def create_account(w3):
    account = w3.eth.account.create()
    return account.address, account._private_key.hex()

def estimate_gas_for_transfer(contract, from_address, to_address, amount):
    decimals = contract.functions.decimals().call()
    token_amount = int(amount * (10 ** decimals))
    gas_estimate = contract.functions.transfer(to_address, token_amount).estimate_gas({'from': from_address})
    return gas_estimate

def send_token(w3, chain_id, contract, from_address, to_address, amount, private_key):
    decimals = contract.functions.decimals().call()
    amount = float(amount)
    token_amount = int(amount * (10 ** decimals))
    gas = estimate_gas_for_transfer(contract, from_address, to_address, amount)
    current_gas_price = w3.eth.gas_price
    nonce = w3.eth.get_transaction_count(from_address)
    tx = contract.functions.transfer(to_address, token_amount).build_transaction({
        'chainId': chain_id,
        'gas': gas,
        'gasPrice': current_gas_price,
        'nonce': nonce,
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt

def check_balance_custom_contract(contract, address):
    raw_balance = contract.functions.balanceOf(address).call()
    token_decimals = contract.functions.decimals().call()
    adjusted_balance = raw_balance / (10 ** token_decimals)
    return adjusted_balance

class SendToken(APIView):
    def post(self, request):
        try:
            if 'Authorization' not in request.headers:
                return Response({"status": "error", 'message': 'Authentication credentials were not provided.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            auth = request.headers.get('Authorization')
            amount = request.data.get('amount')
            token = auth.split()[1]
            key = settings.KEYCLOAK_PUBLIC_KEY
            decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
            sender_alias = decoded_token.get('preferred_username')
            sender = User.objects.get(keycloak_username=sender_alias)
            if not User.objects.filter(keycloak_username=sender_alias).exists():
                return Response({"error": f"{sender_alias} does not have an account"}, status=status.HTTP_404_NOT_FOUND)
            if not sender.has_wallet:
                return Response({"error": f"{sender_alias} does not have a wallet"},
                                status=status.HTTP_417_EXPECTATION_FAILED)

            payment_method = request.data.get('payment_method')
            if payment_method == 'username':
                recipient_alias = request.data.get('recipient_alias')
                if not User.objects.filter(keycloak_username=recipient_alias).exists():
                    return Response({"error": f"{recipient_alias} does not have an account"},
                                    status=status.HTTP_404_NOT_FOUND)
                recipient = User.objects.get(keycloak_username=recipient_alias)
                if not recipient.has_wallet:
                    return Response({"error": f"{recipient_alias} does not have a wallet"},
                                    status=status.HTTP_406_NOT_ACCEPTABLE)
                recipient_wallet = recipient.wallet
                recipient_address = recipient_wallet.address
            else:
                recipient_address = request.data.get('recipient_address')

            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            contract_address = os.getenv('CONTRACT_ADDRESS')
            contract_abi = load_contract_abi('contract_abi.json')
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            chain_id = w3.eth.chain_id
            sender_wallet = sender.wallet
            sender_address = sender_wallet.address
            balance = check_balance_custom_contract(contract, sender_address)
            if balance < float(amount):
                logger.error(f"{sender_alias} has insufficient funds to send {amount}")
                return Response({"error": f"Insufficient funds to send {amount}"},
                                status=status.HTTP_412_PRECONDITION_FAILED)

            private_key = decrypt_private_key(sender_wallet.private_key)
            receipt = send_token(w3, chain_id, contract, sender_address, recipient_address, amount, private_key)
            return Response({"message": 'successfully sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Error sending token(s) as user does not exist")
            return Response({"error": f"Error sending token(s) as user does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error sending token(s): {e}")
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckBalance(APIView):
    def get(self, request):
        try:
            if 'Authorization' not in request.headers:
                return Response({"status": "error", 'message': 'Authentication credentials were not provided.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            auth = request.headers.get('Authorization', None)
            token = auth.split()[1]
            key = settings.KEYCLOAK_PUBLIC_KEY
            decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
            keycloak_username = decoded_token.get('preferred_username')
            user = User.objects.get(keycloak_username=keycloak_username)
            if not user.has_wallet:
                return Response({"error": f"Error checking balance user does not have a wallet"},
                                status=status.HTTP_417_EXPECTATION_FAILED)
            wallet_address = user.wallet.address
            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            contract_address = os.getenv('CONTRACT_ADDRESS')
            contract_abi = load_contract_abi('contract_abi.json')
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            balance = check_balance_custom_contract(contract, wallet_address)
            name = contract.functions.name().call()
            return Response({"balance": f'{balance} {name}'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Error checking balance as user does not exist")
            return Response({"error": f"Error retrieving balance as user does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e)
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckWallet(APIView):
    def get(self, request):
        try:
            if 'Authorization' not in request.headers:
                return Response({"status": "error", 'message': 'Authentication credentials were not provided.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            auth = request.headers.get('Authorization', None)
            token = auth.split()[1]
            key = settings.KEYCLOAK_PUBLIC_KEY
            decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
            keycloak_username = decoded_token.get('preferred_username')
            user = User.objects.get(keycloak_username=keycloak_username)
            if not user.has_wallet:
                return Response({"has_wallet": False},
                                status=status.HTTP_200_OK)
            else:
                return Response({"has_wallet": True},
                                status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Error checking wallet as user does not exist")
            return Response({"error": f"Error retrieving wallet as user does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e)
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CheckDetails(APIView):
    def get(self, request):
        try:
            if 'Authorization' not in request.headers:
                return Response({"status": "error", 'message': 'Authentication credentials were not provided.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            auth = request.headers.get('Authorization', None)
            token = auth.split()[1]
            key = settings.KEYCLOAK_PUBLIC_KEY
            decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
            keycloak_username = decoded_token.get('preferred_username')
            user = User.objects.get(keycloak_username=keycloak_username)
            if not user.has_wallet:
                return Response({"error": f"Error checking details user does not have a wallet"},
                                status=status.HTTP_417_EXPECTATION_FAILED)
            wallet_address = user.wallet.address
            w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
            contract_address = os.getenv('CONTRACT_ADDRESS')
            contract_abi = load_contract_abi('contract_abi.json')
            contract = w3.eth.contract(address=contract_address, abi=contract_abi)
            balance = check_balance_custom_contract(contract, wallet_address)
            name = contract.functions.name().call()
            return Response({"balance": f'{balance} {name}', "wallet_address": wallet_address}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"Error checking details as user does not exist")
            return Response({"error": f"Error retrieving details as user does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(e)
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

class CreateWallet(APIView):
    def post(self, request):
        logger.info("CreateWallet endpoint called")
        try:
            if 'Authorization' not in request.headers:
                logger.error("Authentication credentials were not provided")
                return Response({'error': 'Authentication credentials were not provided.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            auth = request.headers.get('Authorization', None)
            token = auth.split()[1]
            key = settings.KEYCLOAK_PUBLIC_KEY
            logger.info("Authorization header received")
            try:
                decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
                logger.info("Token successfully decoded")
            except InvalidAlgorithmError as e:
                logger.error(f"Invalid algorithm used to decode the token: {e}")
                return Response({'error': 'Invalid algorithm used to decode the token.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"Error decoding token: {e}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            keycloak_username = decoded_token.get('preferred_username')
            logger.info(f"Decoded token for user: {keycloak_username}")
            try:
                user = User.objects.get(keycloak_username=keycloak_username)
                logger.info(f"User {keycloak_username} found in the database")
            except User.DoesNotExist:
                user = User.objects.create(keycloak_username=keycloak_username)
                logger.info(f"User {keycloak_username} created in the database")
            if user.has_wallet:
                logger.warning(f"User {keycloak_username} already has a wallet")
                return Response({"error": "User already has a wallet."}, status=status.HTTP_409_CONFLICT)
            wallet_name = request.data.get('wallet_name')
            roles = decoded_token.get('realm_access', {}).get('roles', [])
            logger.info(f"User roles: {roles}")
            if 'create_wallet' in roles:
                w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
                address, private_key = create_account(w3)
                logger.info(f"Wallet created with address: {address}")
                qr_image = generate_qr_code(address)
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                qr_file = buffer.getvalue()
                wallet = Wallet.objects.create(address=address, private_key=private_key, name=wallet_name, qr_code=qr_file)
                user.has_wallet = True
                user.wallet = wallet
                user.save()
                logger.info(f"Wallet saved for user {keycloak_username} with address {address}")
                return Response({"address": wallet.address, 'name': wallet.name}, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"User {keycloak_username} does not have permission to create a wallet")
                return Response({"error": "User does not have permission to create a wallet."},
                                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_wallet_qr_code(request, wallet_id):
    try:
        wallet = Wallet.objects.get(id=wallet_id)
        qr_code_data = wallet.qr_code
        if qr_code_data:
            response = HttpResponse(qr_code_data, content_type="image/png")
            return response
        return HttpResponse("QR code not available", status=404)
    except Wallet.DoesNotExist:
        return HttpResponse("Wallet not found", status=404)