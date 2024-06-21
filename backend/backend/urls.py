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
from django.urls import path
from ap_monitor.views import ListDevices, DeleteDevice, UpdateDevices, AddDevice
from service_monitor.views import ListServices, AddService, DeleteService, EditService, ListServicesByType
from wallet.views import CreateWallet, SendToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('devices/', ListDevices.as_view()),
    path('delete/', DeleteDevice.as_view()),
    path('update/', UpdateDevices.as_view()),
    path('add/', AddDevice.as_view()),
    path('service/list/', ListServices.as_view()),
    path('service/add/', AddService.as_view()),
    path('service/delete/<str:service_name>/', DeleteService.as_view(), name='delete_service'),
    path('service/edit/<str:service_name>/', EditService.as_view(), name='edit_service'),
    path('service/list-by-type/', ListServicesByType.as_view(), name='list-services-by-type'),
    path('wallet/create/', CreateWallet.as_view(), name='create-wallet'),
    path('wallet/send_token/', SendToken.as_view(), name='send-token'),
]
