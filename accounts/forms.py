import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,20}$")


class RegisterForm(forms.Form):
    username = forms.CharField(label="Kullanıcı adı", max_length=20)
    email = forms.EmailField(label="E-posta")
    password = forms.CharField(label="Parola", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Parola (tekrar)", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not USERNAME_RE.match(username):
            raise forms.ValidationError(
                "Kullanıcı adı 3-20 karakter olmalı; yalnızca harf, rakam, alt çizgi ve nokta içerebilir."
            )
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten alınmış.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Parolalar eşleşmiyor.")
        return cleaned_data

    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
        )


class LoginForm(forms.Form):
    identifier = forms.CharField(label="E-posta veya kullanıcı adı")
    password = forms.CharField(label="Parola", widget=forms.PasswordInput)
