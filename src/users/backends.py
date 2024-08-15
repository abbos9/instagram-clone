from django.contrib.auth.backends import BaseBackend
from .models import User  # Replace with your actual user model
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CustomBackend(BaseBackend):
    def authenticate(self, request, phone_num=None, password=None, **kwargs):
        try:
            user = User.objects.get(phone_num=phone_num)
            if bcrypt_context.verify(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
