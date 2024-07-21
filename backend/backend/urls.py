"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from service_monitor.views import ListServices, AddService, DeleteService, EditService, ListServicesByType
from wallet.views import CreateWallet, SendToken, CheckBalance, CheckWallet, CheckDetails
from users.views import UserKeycloakAttributes, RegisterKeycloakUser

urlpatterns = [
    path("admin/", include("django_keycloak.urls")),
    path("admin/", admin.site.urls),

    path("monitoring/", include("monitoring.urls")),
    path("metrics/", include("metrics.urls")),

    # services
    path('service/list/', ListServices.as_view()),
    path('service/add/', AddService.as_view()),
    path('service/delete/<str:service_name>/', DeleteService.as_view()),
    path('service/edit/<str:service_name>/', EditService.as_view()),
    path('service/list-by-type/', ListServicesByType.as_view()),

    # wallets
    path('wallet/create/', CreateWallet.as_view()),
    path('wallet/send-token/', SendToken.as_view()),
    path('wallet/balance/', CheckBalance.as_view()),
    path('wallet/ownership/', CheckWallet.as_view()),
    path('wallet/details/', CheckDetails.as_view()),

    # user
    path('user/keycloak/attributes/', UserKeycloakAttributes.as_view()),
    path('user/keycloak/register/', RegisterKeycloakUser.as_view())
]
