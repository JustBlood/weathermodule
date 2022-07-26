from django.urls import path, include
from django.views.generic import TemplateView
from .views import *

urlpatterns = [

    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('weather/post_indicators/', add_indicators, name='add_indicators'),

    path('weather/my_stations/', MyStations.as_view(), name='my_stations'),

    path('weather/my_stations/add', AddStation.as_view(), name='add_station'),

    path('users/login/', MyLoginView.as_view(), name='login'),

    path('users/', include('django.contrib.auth.urls')),

    path('confirm_email/',
         TemplateView.as_view(template_name='registration/confirm_email.html'),
         name='confirm_email',
        ),

    path(
        'verify_email/<uidb64>/<token>/',
        EmailVerify.as_view(),
        name='verify_email',
    ),

    path(
        'invalid_verify/',
        TemplateView.as_view(template_name='registration/invalid_verify.html'),
        name='invalid_verify'
    ),

    path('register/', Register.as_view(), name='register'),
]