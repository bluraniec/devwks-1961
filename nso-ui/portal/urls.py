"""portal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.show_devices, name='show_devices'),
    path('delete_ACLs/', views.delete_ACLs, name='delete_ACLs'),
    path('get_ACLs/', views.get_ACLs, name='get_ACLs'),
    path('set_ACLs/', views.set_ACLs, name='set_ACLs'),
    path('set_ACLs_submit/', views.set_ACLs_submit, name='set_ACLs_submit')
]
