from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import User

class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ('username', 'email', 'password1', 'password2')
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['username'].widget = forms.TextInput(attrs={'placeholder': 'Username'})
        self.fields['email'].label = 'Email Address'
        self.fields['email'].widget = forms.TextInput(attrs={'placeholder': 'Email'})
        self.fields['password1'].widget = forms.TextInput(attrs={'placeholder': 'Password', 'type': 'password'})
        self.fields['password2'].widget = forms.TextInput(attrs={'placeholder': 'Confirm Password', 'type': 'password'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        
        raise forms.ValidationError('This email address is already in use')
class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'})
    )

class AuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("You must activate your email before logging in."),
    }

    def get_invalid_login_error(self):
        if self.user_cache and not self.user_cache.is_active:
            return ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'username': self.username_field.verbose_name},
        )