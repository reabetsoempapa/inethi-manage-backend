from django.shortcuts import render
from jwt.exceptions import InvalidAlgorithmError
from rest_framework.views import APIView, Response
from rest_framework import status
from web3 import Web3
from dotenv import load_dotenv
import os
from .models import Wallet, decrypt_private_key
from users.models import User
from jose import jwt, JWTError, ExpiredSignatureError
import json
from django.conf import settings

load_dotenv()
import logging

# Get an instance of a logger
logger = logging.getLogger('general')


def load_contract_abi(file_name):
    file_path = os.path.join(settings.BASE_DIR, 'wallet', file_name)
    with open(file_path, 'r') as abi_file:
        return json.load(abi_file)


def create_account(w3):
    account = w3.eth.account.create()
    return account.address, account._private_key.hex()


def estimate_gas_for_transfer(contract, from_address, to_address, amount):
    # Prepare the transaction for gas estimation
    decimals = contract.functions.decimals().call()
    token_amount = int(amount * (10 ** decimals))

    # Estimating gas
    gas_estimate = contract.functions.transfer(to_address, token_amount).estimate_gas({
        'from': from_address  # Sender's address
    })
    print(f"Estimated gas for transfer: {gas_estimate}")
    return gas_estimate


def send_token(w3, chain_id, contract, from_address, to_address, amount, private_key):
    # Calculate the token amount adjusted for decimals
    decimals = contract.functions.decimals().call()
    amount = int(amount)
    token_amount = int(amount * (10 ** decimals))

    gas = estimate_gas_for_transfer(contract, from_address, to_address, amount)

    # Fetch the current network gas price
    current_gas_price = w3.eth.gas_price
    print(f"Current network gas price: {current_gas_price} wei")

    # Prepare the transaction
    nonce = w3.eth.get_transaction_count(from_address)
    tx = contract.functions.transfer(to_address, token_amount).build_transaction({
        'chainId': chain_id,  # Celo's chain ID
        'gas': gas,
        'gasPrice': current_gas_price,
        'nonce': nonce,
    })

    # Sign the transaction
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("Transaction sent! Hash:", tx_hash.hex())

    # Wait for the transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt


def check_balance_custom_contract(contract, address):
    raw_balance = contract.functions.balanceOf(address).call()
    token_decimals = contract.functions.decimals().call()
    # Adjust the balance based on the token decimals
    adjusted_balance = raw_balance / (10 ** token_decimals)
    return adjusted_balance


class CreateWallet(APIView):
    def post(self, request):
        try:
            if 'Authorization' not in request.headers:
                return Response({'error': 'Authentication credentials were not provided.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            auth = request.headers.get('Authorization', None)
            token = auth.split()[1]
            key = settings.KEYCLOAK_PUBLIC_KEY

            try:
                decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience='account')
            except InvalidAlgorithmError as e:
                return Response({'error': 'Invalid algorithm used to decode the token.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            keycloak_username = decoded_token.get('preferred_username')
            try:
                user = User.objects.get(keycloak_username=keycloak_username)
            except User.DoesNotExist:
                user = User.objects.create(keycloak_username=keycloak_username)

            if user.has_wallet:
                return Response({"error": "User already has a wallet."}, status=status.HTTP_409_CONFLICT)

            wallet_name = request.data.get('wallet_name')
            roles = decoded_token.get('realm_access', {}).get('roles', [])
            if 'create_wallet' in roles:
                w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
                address, private_key = create_account(w3)
                user = User.objects.get(keycloak_username=keycloak_username)
                wallet = Wallet.objects.create(address=address, private_key=private_key, name=wallet_name)
                user.has_wallet = True
                user.wallet = wallet
                user.save()
                return Response({"address": wallet.address, 'name': wallet.name}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "User does not have permission to create a wallet."},
                                status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            return Response({"error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            sender_has_wallet = sender.has_wallet
            if not sender_has_wallet:
                return Response({"error": f"{sender_alias} does not have a wallet"},
                                status=status.HTTP_417_EXPECTATION_FAILED)

            payment_method = request.data.get('payment_method')
            if payment_method == 'username':
                recipient_alias = request.data.get('recipient_alias')
                if not User.objects.filter(keycloak_username=recipient_alias).exists():
                    return Response({"error": f"{recipient_alias} does not have an account"},
                                    status=status.HTTP_404_NOT_FOUND)
                recipient = User.objects.get(keycloak_username=recipient_alias)
                recipient_has_wallet = recipient.has_wallet
                if not recipient_has_wallet:
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
