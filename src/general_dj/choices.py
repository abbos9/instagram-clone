from django.db import models

class UserRoleType(models.TextChoices):
    user = 'user', 'User'
    premium = 'premium', 'Premium'


class UserGenderType(models.TextChoices):
    male = 'male', 'Male'
    female = 'female', 'female'