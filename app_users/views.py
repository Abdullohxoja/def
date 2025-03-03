from datetime import timedelta

from django.template.defaulttags import now
from rest_framework import status, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import data
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from tutorial.quickstart.serializers import UserSerializer

from app_users.models import FollowModel
from app_users.serializers import LoginSerializer, RegisterSerializer, VerifyEmailSerializer, User, \
    CustomTokenObtainPairSerializer, UpdatePasswordSerializer, ForgotPasswordSerializer


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer

    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        user.set_password(raw_password=serializer.validated_data['password1'])
        user.save()


def get_tokens_for_user(user):
    pass


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        tokens = get_tokens_for_user(user=user)
        return Response(data=tokens, status=status.HTTP_200_OK)




class VerifyEmailView(APIView):

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']

            try:
                user = User.objects.get(email=email)
                if user.verification_code == code:
                    user.email_verified = True
                    user.verification_code = None
                    user.save(update_fields=['email_verified', 'verification_code'])
                    return Response({"message": "Email muvaffaqiyatli tasdiqlandi!"}, status=200)
                return Response({"error": "Tasdiqlash kodi noto‘g‘ri"}, status=400)
            except User.DoesNotExist:
                return Response({"error": "Bunday foydalanuvchi topilmadi!"}, status=404)
        return Response(serializer.errors, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        try:
            user = User.objects.get(username=request.data.get("username") or request.data.get("email"))
            if not user.email_verified:
                return Response({"error": "Email tasdiqlanmagan!"}, status=400)
        except User.DoesNotExist:
            return Response({"error": "Bunday foydalanuvchi topilmadi!"}, status=404)
        return response


class CheckInactivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.last_activity and now() - user.last_activity > timedelta(minutes=10):
            return Response({"message": "Sizning sessiyangiz tugadi. Qayta login qiling."}, status=401)

        user.last_activity = now()
        user.save(update_fields=['last_activity'])
        return Response({"message": "Foydalanuvchi hali faol"}, status=200)


class UpdatePasswordAPIView(generics.UpdateAPIView):
    """
    Foydalanuvchining parolini yangilash API
    - Faqat autentifikatsiya qilingan foydalanuvchilar foydalanishi mumkin
    """
    serializer_class = UpdatePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Hozirgi foydalanuvchini qaytaradi"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        """Parolni tekshirib, yangilaydi"""

        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Parolni yangilash
            serializer.update_password()
            return Response({"message": "Parol muvaffaqiyatli yangilandi!"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(generics.GenericAPIView):
    """Emailga parolni tiklash kodini yuborish API"""
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.send_reset_code()
            return Response({"message": "Parolni tiklash kodi emailga yuborildi."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(generics.GenericAPIView):
    """Kod orqali parolni tiklash API"""
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.reset_password()
            return Response({"message": "Parol muvaffaqiyatli tiklandi!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUserSerializer:
    pass


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FollowUserSerializer

    def post(self, request, *args, **kwargs):
        response = dict()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        from_user = request.user
        to_user = serializer.validated_data['to_user']
        follow_status = FollowModel.objects.filter(from_user, to_user)
        if follow_status.exists():
            follow_status.first().delete()
            response["detail"] = "User unfollowed"
            response["status"] = "unfollowed"
            return Response(data=response, status=status.HTTP_204_NO_CONTENT)
        else:
            FollowModel.objects.create(from_user=from_user, to_user=to_user)
            response["detail"] = "User followed to this user"
            response["status"] = "followed"
            return Response(data=response, status=status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        return self.serializer_class(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        follow_type = request.query_params.get('type')
        if follow_type not in ["followers", "following"]:
            raise ValidationError("Invalid query params")

        if follow_type == "following":
            users = [user.to_user for user in request.user.following.all()]
        else:
            users = [user.from_user for user in request.user.followers.all()]

        serializer = UserSerializer(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

