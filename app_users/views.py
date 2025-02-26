from rest_framework import status
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import data
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from app_users.serializers import LoginSerializer, RegisterSerializer


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.set_password(raw_password=serializer.validated_data['password1'])
        user.save()



class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        tokens = get_tokens_for_user(user=user)
        return Response(data=tokens, status=status.HTTP_200_OK)
