import logging

from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

from .serializers import WalletSerializer

# Get an instance of a logger
logger = logging.getLogger("general")


class WalletViewSet(ViewSet):
    """Viewset for endpoints related to the current user's wallet.

    List methods are not allowed (since we don't want the API to expose other users' wallets).
    """

    def create(self, request):
        """Create a wallet for a user via POST, assuming they don't have one already."""
        if hasattr(request.user, "wallet"):
            return Response(
                {"error": "Error creating wallet: User already has a wallet"},
                status=status.HTTP_417_EXPECTATION_FAILED,
            )
        serializer = WalletSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # This is actually not the list view - it's the detail view, but since the
    # wallet detail depends on the current user, not URL parameters, we define it here.
    def list(self, request):
        """Serialize the request user's wallet and return as JSON."""
        if not hasattr(request.user, "wallet"):
            return Response(
                {"error": "Error getting wallet: User does not have a wallet"},
                status=status.HTTP_417_EXPECTATION_FAILED,
            )
        serializer = WalletSerializer(request.user.wallet)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def send(self, request):
        """Endpoint to send currency to another wallet."""
        sender_has_wallet = hasattr(request.user, "wallet")
        if not sender_has_wallet:
            return Response(
                {"error": f"{request.user} does not have a wallet"},
                status=status.HTTP_417_EXPECTATION_FAILED,
            )
        sender_wallet = request.user.wallet
        amount = request.data.get("amount")
        payment_method = request.data.get("payment_method")
        if payment_method == "username":
            recipient_alias = request.data.get("recipient_alias")
            receipt = sender_wallet.send_to_username(amount, recipient_alias)
        else:
            recipient_address = request.data.get("recipient_address")
            receipt = sender_wallet.send_to_address(amount, recipient_address)
        return Response({"message": "successfully sent"})

    @action(detail=False)
    def balance(self, request):
        """Endpoint to check a wallet's balance."""
        if not hasattr(request.user, "wallet"):
            return Response(
                {"error": "Error checking balance user does not have a wallet"},
                status=status.HTTP_417_EXPECTATION_FAILED,
            )
        wallet = request.user.wallet
        balance = wallet.balance()
        name = wallet.contract_name()
        return Response({"balance": f"{balance} {name}"})

    @action(detail=False)
    def exists(self, request):
        """Endpoint to check whether the current user has a wallet."""
        return Response({"has_wallet": hasattr(request.user, "wallet")})
