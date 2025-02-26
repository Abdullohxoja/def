from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app_posts import serializers

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username

        return token

class RegisterSerializer(serializers.ModelSerializer):
    password1 =serializers.CharField(write_only=True)
    password2 =serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    las_name = serializers.CharField(required=False)


    class Meta :
        model = User
        fields = ['first_name' , 'last_name' , 'email' , 'username', 'password1', 'password2']

    def validate(self , attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')

        if password1 != password2:
            raise serializers.ValidationError("Password does npt match")

        validate_password(password=password1)
        return attrs

    def create(self, validated_date):
        password1 = validated_date.pop('password1')

        validated_date['is_active'] = False
        user = User.objects.create(**validated_date)
        user.set_password(raw_password=password1)
        user.save()
        return user

    def is_valid(self, raise_exception):
        pass

class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        user = None

        # Attempt to fetch user by email
        try:
            user = User.objects.get(email=email_or_username)
        except User.DoesNotExist:
            # If not found by email, attempt to fetch by username
            try:
                user = User.objects.get(username=email_or_username)
            except User.DoesNotExist:
                pass  # User remains None if both lookups fail

        if user is None:
            raise serializers.ValidationError({
                "success": False,
                "detail": "User not found"
            })

        # Authenticate the user
        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user is None:
            raise serializers.ValidationError({
                "success": False,
                "detail": "Username or password is invalid"
            })

        attrs["user"] = authenticated_user
        return attrs

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not hasattr(self, 'user') or not self.user.email_verified:
            raise serializers.ValidationError("Email tasdiqlanmagan!")

        return data


class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Eski parol noto‘g‘ri.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Parollar mos kelmadi."})
        return attrs

    def update_password(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email tizimda mavjud emas.")
        return value

    def send_reset_code(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)

        reset_code = generate_verification_code()
        user.verification_code = reset_code
        user.save(update_fields=['verification_code'])

        send_verification_email(user.email, reset_code)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "Bu email tizimda mavjud emas."})

        if user.verification_code != code:
            raise serializers.ValidationError({"code": "Kod noto‘g‘ri yoki eskirgan."})

        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Parollar mos kelmadi."})

        return attrs

    def reset_password(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.verification_code = None  # Kodni o‘chiramiz
        user.save()

