from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status
from web3 import Web3
from dotenv import load_dotenv
import os
from .models import Wallet, decrypt_private_key
from users.models import User
import json
from django.conf import settings

load_dotenv()


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

def user_has_wallet(user_alias):
    try:
        user = User.objects.get(keycloak_username=user_alias)
        wallet = Wallet.objects.get(user=user)
        return True
    except (User.DoesNotExist, Wallet.DoesNotExist):
        return False


class CreateWallet(APIView):
    def post(self, request):

        keycloak_username = request.data.get('alias')
        try:
            user = User.objects.get(keycloak_username=keycloak_username)
        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if Wallet.objects.filter(user=user).exists():
            return Response({"error": "User already has a wallet."}, status=status.HTTP_400_BAD_REQUEST)

        wallet_name = request.data.get('wallet_name')
        w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
        address, private_key = create_account(w3)

        wallet = Wallet.objects.create(address=address, private_key=private_key, user=user, name=wallet_name)
        return Response({"address": wallet.address, 'name': wallet.name}, status=status.HTTP_201_CREATED)


class SendToken(APIView):
    def post(self, request):
        sender_alias = request.data.get('sender_alias')
        recipient_alias = request.data.get('recipient_alias')
        amount = request.data.get('amount')

        sender_has_wallet = user_has_wallet(sender_alias)
        recipient_has_wallet = user_has_wallet(sender_alias)
        if not sender_has_wallet:
            return Response({"error": f"{sender_alias} does not have a wallet or account"}, status=status.HTTP_400_BAD_REQUEST)

        if not recipient_has_wallet:
            return Response({"error": f"{recipient_alias} does not have a wallet or account"}, status=status.HTTP_400_BAD_REQUEST)

        w3 = Web3(Web3.HTTPProvider('https://forno.celo.org'))
        contract_address = os.getenv('CONTRACT_ADDRESS')
        contract_abi = load_contract_abi('contract_abi.json')
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        chain_id = w3.eth.chain_id

        recipient = User.objects.get(keycloak_username=recipient_alias)
        recipient_wallet = Wallet.objects.get(user=recipient)
        recipient_address = recipient_wallet.address

        sender = User.objects.get(keycloak_username=sender_alias)
        sender_wallet = Wallet.objects.get(user=sender)
        sender_address = sender_wallet.address
        private_key = decrypt_private_key(sender_wallet.private_key)

        receipt = send_token(w3, chain_id, contract, sender_address, recipient_address, amount, private_key)
        print(receipt)
        return Response({"message": 'successfully sent'}, status=status.HTTP_200_OK)
