from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime


from general_dj.choices import UserRoleType, UserGenderType
from general_dj.models import BaseModel
from general_dj.config import Tashkent_tz
from users.managers import CustomUserManager

# Create your models here.


class User(AbstractUser):
    username = models.CharField(
        max_length=30, unique=False, blank=True, null=True)
    phone_num = models.CharField(max_length=20, unique=True,null=True, blank=True)
    role = models.CharField(
        max_length=24, choices=UserRoleType.choices,
        default=UserRoleType.user.value)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=24, choices=UserGenderType.choices,
        default=UserGenderType.male.value,null=True, blank=True )

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_num"
    REQUIRED_FIELDS = ["username"]



    def __str__(self) -> str:
        return self.username