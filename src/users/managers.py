from django.contrib.auth.models import BaseUserManager

from general_dj.choices import UserRoleType

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_num, password=None, **extra_fields):
        if not phone_num:
            raise ValueError('The Phone field must be set')
        user = self.model(phone_num=phone_num, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_num, password=None, **extra_fields):
        print('super user is creating !')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRoleType.premium.value)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_num, password, **extra_fields)