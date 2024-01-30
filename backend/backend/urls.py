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
from ap_monitor.views import ListDevices, DeleteDevice, UpdateDevices, AddDevice, TestAuthView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('devices/', ListDevices.as_view()),
    path('delete/', DeleteDevice.as_view()),
    path('update/', UpdateDevices.as_view()),
    path('add/', AddDevice.as_view()),
    path('test-auth/', TestAuthView.as_view(), name='test-auth'),
]
