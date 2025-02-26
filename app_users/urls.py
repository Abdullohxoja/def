from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from app_users.views import LoginAPIView, RegisterAPIView

app_name = 'users'


urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path ('login/', LoginAPIView.as_view(), name='login'),
    path ('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('verify/email', LoginAPIView.as_view(), name='login'),
    path('resend/code', LoginAPIView.as_view(), name='login'),
    path('me/', LoginAPIView.as_view(), name='login'),
    path('update/password', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]



