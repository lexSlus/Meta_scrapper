from django.urls import path

from app_auth.views.register import registerUser
from app_auth.views.login import loginUser

urlpatterns = [
    path('register/', registerUser, name='register'),
    path('login/', loginUser, name='login'),
]
