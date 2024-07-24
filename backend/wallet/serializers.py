from rest_framework import serializers

from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    """Serializes wallet models to and from JSON data."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Wallet
        exclude = ("private_key",)
        read_only_fields = ("user", "private_key", "address")

    def create(self, validated_data):
        """Inject user from current request context."""
        account = Wallet.w3.eth.account.create()
        validated_data["user"] = self.context["request"].user
        validated_data["address"] = account.address
        validated_data["private_key"] = account._private_key.hex()
        return super().create(validated_data)
