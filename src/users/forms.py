from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from passlib.context import CryptContext
from .models import User  # Replace with your actual user model

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreationForm(forms.ModelForm):
    username = forms.CharField(label='Username', max_length=255)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('phone_num', 'username')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = bcrypt_context.hash(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('phone_num', 'password', 'is_active', 'is_staff')

    def clean_password(self):
        return self.initial["password"]
