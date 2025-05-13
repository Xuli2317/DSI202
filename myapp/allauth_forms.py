# myapp/allauth_forms.py
from allauth.account.forms import SignupForm


import logging
from django import forms

logger = logging.getLogger(__name__)


class CustomSignupForm(SignupForm):
    role = forms.ChoiceField(
        choices=[('tenant', 'Tenant'), ('landlord', 'Landlord')],
        label='Role',
        widget=forms.RadioSelect,
        initial='tenant'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].required = False
        self.fields['role'].required = False
        if 'email' in self.fields:
            self.fields['email'].required = False
        logger.debug(f"SignupForm initialized with fields: {self.fields}")

    def save(self, request):
        logger.debug(f"Saving signup form with data: {self.cleaned_data}")
        user = super().save(request)
        user.role = self.cleaned_data.get('role', 'tenant')
        if not user.username and user.email:
            user.username = user.email.split('@')[0]
        user.save()
        logger.debug(f"User saved: {user.__dict__}")
        return user
