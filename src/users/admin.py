from django.contrib import admin
from users.models import User, UsersTableModel
# Register your models here.


admin.site.register(UsersTableModel)
admin.site.register(User)