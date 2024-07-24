import logging

from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import status

from .models import Wallet
from .serializers import WalletSerializer
from .permissions import IsMyWalletOrReadOnly

# Get an instance of a logger
logger = logging.getLogger("general")


class WalletViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    GenericViewSet):
    """Viewset for endpoints related to the current user's wallet.
    
    This viewset can create, retrieve and update wallets for the current user.
    Note that it explicitly cannot list other users' wallets (for obvious security reasons!)
    """

    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer

    lookup_value_regex = '[0-9]*|current'
    permission_classes = [IsMyWalletOrReadOnly]

    def perform_authentication(self, request):
        """Replace 'current' pk with the request user's wallet's pk."""
        super().perform_authentication(request)
        if self.kwargs.get("pk") == "current":
            if hasattr(request.user, "wallet"):
                self.kwargs["pk"] = request.user.wallet.pk
            else:
                self.kwargs["pk"] = None

    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
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

    @action(detail=True)
    def balance(self, request, pk=None):
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

    @action(detail=True)
    def exists(self, request, pk=None):
        """Endpoint to check whether the current user has a wallet."""
        return Response({"has_wallet": hasattr(request.user, "wallet")})
