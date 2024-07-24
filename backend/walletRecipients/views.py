from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status
from .models import Recipient
from wallet.models import Wallet
from users.models import User

# from rest_framework.exceptions import ValidationError

class CreateRecipient(APIView):
    def post(self, request):
        try:
            name = request.data.get('name')
            wallet_address = request.data.get('wallet_address')
            wallet_name = request.data.get('wallet_name', None)
            wallet = Wallet.objects.filter(address=wallet_address).first()
            if not wallet:
                return Response({"error": "Wallet does not exist."}, status=status.HTTP_404_NOT_FOUND)

            recipient = Recipient.objects.create(
                name=name,
                wallet_address=wallet_address,
                wallet_name=wallet_name,
                wallet=wallet
            )
            return Response({"message": "Recipient created successfully."}, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating recipient: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecipientList(APIView):
    def get(self, request):
        recipients = Recipient.objects.all()
        recipient_list = [{"name": recipient.name, "wallet_address": recipient.wallet_address, "day_added": recipient.day_added, "wallet_name": recipient.wallet_name} for recipient in recipients]
        return Response(recipient_list, status=status.HTTP_200_OK)
