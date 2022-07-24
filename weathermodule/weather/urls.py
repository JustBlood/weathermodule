from django.urls import path, include
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('users/', include('django.contrib.auth.urls')),
    path('register/', Register.as_view(), name='register'),
    # path('weather/', weather, name='weather'),
    # path('about/', about, name='about'),
]