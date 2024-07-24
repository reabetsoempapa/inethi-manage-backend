from django.urls import path
from .views import CreateRecipient, RecipientList

urlpatterns = [
    path('create/', CreateRecipient.as_view(), name='create_recipient'),
    path('list/', RecipientList.as_view(), name='recipient_list'),
]
