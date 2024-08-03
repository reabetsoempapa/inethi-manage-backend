from rest_framework.serializers import ModelSerializer, SerializerMethodField

from . import models


class RadacctSerializer(ModelSerializer):
    """Serializes Radacct objects from django model to JSON."""

    is_voucher = SerializerMethodField()

    class Meta:
        """UserSerializer metadata."""

        model = models.Radacct
        fields = "__all__"

    def get_is_voucher(self, radacct: models.Radacct) -> bool:
        """Test whether this account is associated with a voucher."""
        return models.Radcheck.objects.filter(
            username=radacct.username,
            attribute="Rd-User-Type",
            op=":=",
            value="voucher"
        ).exists()
