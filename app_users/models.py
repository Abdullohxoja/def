from datetime import timezone, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import  AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from app_common.models import BaseModel


class CustomUserModel(AbstractUser):
    email = models.EmailField(unique=True)

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)
        # refresh.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=3))
        # refresh.access_token.set_exp(from_time=timezone.now(), lifetime=timedelta(minutes=1))

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name='profile')
    avatar = models.ImageField(upload_to='profiles' , null=True , validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    short_bio =models.CharField(max_length=160 , null=True)
    about = models.TextField()
    pronouns = models.TextField(max_length=255 , null=True)


    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'




#Confirmation code for user

class UserProfileConfirmation(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='codes')
    code = models.PositiveSmallIntegerField()
    code_expiration = models.DateTimeField()
    password = models.CharField(max_length=128)
    password2 = models.CharField(max_length=128)
    is_confirmed = models.BooleanField(default=False)













