from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime


from general_dj.choices import UserRoleType, UserGenderType
from general_dj.models import BaseModel
from general_dj.config import Tashkent_tz
from users.managers import CustomUserManager

# Create your models here.

class UsersTableModel(models.Model):
    class Meta:
        db_table = "users"
        managed=False

    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=36)
    last_name = models.CharField(max_length=36)
    phone_num = models.CharField(max_length=36, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=24)
    gender = models.CharField(max_length=24, choices=UserGenderType.choices,
        default=UserGenderType.male.value,null=True, blank=True )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.username



class User(AbstractUser, BaseModel):
    username = models.CharField(
        max_length=30, unique=False, blank=True, null=True)
    phone = models.CharField(max_length=13, unique=True,null=True, blank=True)
    role = models.CharField(
        max_length=24, choices=UserRoleType.choices,
        default=UserRoleType.user.value)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(max_length=24, choices=UserGenderType.choices,
        default=UserGenderType.male.value,null=True, blank=True )

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["username"]



    def __str__(self) -> str:
        return self.username