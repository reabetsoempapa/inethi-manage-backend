import os
import json

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from web3 import Web3
from web3.types import TxReceipt

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

contract_api_fp = os.path.join(settings.BASE_DIR, "wallet", "contract_abi.json")
with open(contract_api_fp, "r", encoding="utf-8") as abi_file:
    CONTRACT_ABI = json.load(abi_file)


def encrypt_private_key(private_key: str) -> str:
    """Fernet encrypt a private key."""
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY is not set in environment variables.")
    fernet = Fernet(ENCRYPTION_KEY)
    encrypted_key = fernet.encrypt(private_key.encode())
    return encrypted_key.decode()


def decrypt_private_key(encrypted_key: str) -> str:
    """Fernet decrypt a private key."""
    fernet = Fernet(ENCRYPTION_KEY)
    decrypted_key = fernet.decrypt(encrypted_key.encode())
    return decrypted_key.decode()


class Wallet(models.Model):
    """A users ETH wallet."""

    class CannotSendException(Exception):
        """Raise when an issue is encountered before currency is sent."""

    address = models.CharField(max_length=50, unique=True)
    private_key = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, default="default_name")
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    w3 = Web3(Web3.HTTPProvider("https://forno.celo.org"))
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    def estimate_gas_for_transfer(self, token_amount: int, recipient: "Wallet") -> int:
        """Estimate the amount of GAS a transfer will require."""
        transfer = self.contract.functions.transfer(recipient.address, token_amount)
        return transfer.estimate_gas({"from": self.address})

    def balance(self) -> float:
        """Check the balance on this wallet."""
        raw_balance = self.contract.functions.balanceOf(self.address).call()
        token_decimals = self.contract.functions.decimals().call()
        # Adjust the balance based on the token decimals
        adjusted_balance = raw_balance / (10**token_decimals)
        return adjusted_balance

    def send_to_address(self, amount: float, recipient_address: str) -> TxReceipt:
        """Send an amount to another user via their unique wallet address."""
        try:
            recipient_wallet = Wallet.objects.get(address=recipient_address)
        except Wallet.DoesNotExist as wdne:
            raise self.CannotSendException(
                f"Wallet {recipient_address} does not exist"
            ) from wdne
        return self.send_to_wallet(amount, recipient_wallet)

    def send_to_username(self, amount: float, recipient_name: str) -> TxReceipt:
        """Send an amount to another user via their unique username."""
        try:
            recipient = User.objects.get(username=recipient_name)
        except User.DoesNotExist as udne:
            raise self.CannotSendException(
                f"Recipient {recipient_name} does not have an account."
            ) from udne
        if not hasattr(recipient, "wallet"):
            raise self.CannotSendException(
                f"Recipient {recipient.username} does not have a wallet"
            )
        return self.send_to_wallet(amount, recipient.wallet)

    def send_to_wallet(self, amount: float, recipient: "Wallet") -> TxReceipt:
        """Send an amount to another wallet."""
        if self.balance() < amount:
            raise self.CannotSendException(f"Insufficient funds to send {amount}")
        private_key = decrypt_private_key(self.private_key)
        # Calculate the token amount adjusted for decimals
        decimals = self.contract.functions.decimals().call()
        token_amount = int(amount * (10**decimals))
        gas = self.estimate_gas_for_transfer(token_amount, recipient)
        # Fetch the current network gas price
        current_gas_price = self.w3.eth.gas_price
        # Prepare the transaction
        nonce = self.w3.eth.get_transaction_count(self.address)
        transfer = self.contract.functions.transfer(recipient.address, token_amount)
        tx = transfer.build_transaction(
            {
                "chainId": self.w3.eth.chain_id,  # Celo's chain ID
                "gas": gas,
                "gasPrice": current_gas_price,
                "nonce": nonce,
            }
        )
        # Sign the transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
        # Send the transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        # Wait for the transaction to be mined
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def contract_name(self) -> str:
        """Get this wallet's ABI contract name."""
        return self.contract.functions.name().call()

    def save(self, *args, **kwargs):
        """Encrypt the private key before saving."""
        if not self.pk:  # Only encrypt if it's a new object
            self.private_key = encrypt_private_key(self.private_key)
        return super().save(*args, **kwargs)
