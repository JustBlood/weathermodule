from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import (UserCreationForm as DjangoUserCreationForm,
AuthenticationForm as DjangoAuthenticationForm
)
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from weather.utils import send_email_verify

User = get_user_model()


class MyAuthenticationForm(DjangoAuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        print(username)
        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            print(self.user_cache)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
            if not self.user_cache.email_verify:
                send_email_verify(self.request, self.user_cache)
                raise ValidationError(
                    'Email not verify, check your email',
                    code='invalid_login',
                )
        return self.cleaned_data


class UserCreationForm(DjangoUserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta(DjangoUserCreationForm.Meta):
        model = User
        fields = ('username', 'email')