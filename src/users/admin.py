from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User  # Replace with your actual user model
from .forms import UserCreationForm, UserChangeForm

# Register your models here.

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('phone_num', 'username', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('phone_num', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_num', 'username', 'password1', 'password2')}
        ),
    )
    search_fields = ('phone_num', 'username')
    ordering = ('phone_num',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)