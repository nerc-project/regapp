"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django import forms
from django.conf import settings
from crispy_forms.helper import FormHelper
from .models import AccountAction

MSS_ORGANIZATIONS = [
    ('BU', 'Boston University'),
    ('MIT', 'Massachusetts Institute of Technology'),
    ('HU', 'Harvard University'),
    ('RH', 'Red Hat')
]


class WayfForm(forms.Form):
    mss_organization = forms.ChoiceField(
        choices=[('', '-----')] + MSS_ORGANIZATIONS,
        label="Organization"
    )

    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = 'wayf_%s'
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_id = "wayfform"


class ConfirmAccountForm(forms.Form):
    regcode = forms.CharField(
        max_length=100,
        label="Registration Code"
    )

    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = 'regconfirm_%s'
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_id = "confirmationform"


class ConfirmTermsForm(forms.Form):

    accept_privacy_statement = forms.BooleanField(
        label=f"I accept {settings.TERMS_NAME} {settings.TERMS_VER}"
    )

    accept_privacy_statement_version = forms.CharField(
        widget=forms.HiddenInput(),
        initial=f"{settings.TERMS_VER}"
    )

    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = 'regterms_%s'
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_id = "termsform"


class CreateAccountForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label="Preferred Username"
    )
    first_name = forms.CharField(
        max_length=100,
        label="First Name",
    )
    last_name = forms.CharField(
        max_length=100,
        label="Last Name",
    )
    email = forms.EmailField(
        max_length=100,
        label="Email",
    )

    # TODO: (JAC) I don't like this and there is
    # probably a better way!
    research_domain = forms.ChoiceField(
        choices=[('', '-----')] + list(AccountAction.RESEARCH_DOMAIN_CHOICES),
        label="Research Domain"
    )

    accept_privacy_statement = forms.BooleanField(
        label=f"I accept {settings.TERMS_NAME} {settings.TERMS_VER}"
    )

    accept_privacy_statement_version = forms.CharField(
        widget=forms.HiddenInput(),
        initial=f"{settings.TERMS_VER}"
    )

    def clean_research_domain(self):
        rd = self.cleaned_data['research_domain']
        if rd not in [x[0] for x in AccountAction.RESEARCH_DOMAIN_CHOICES]:
            raise forms.ValidationError(
                "Invalid research domain selected",
                code='invalid'
            )
        else:
            return rd

    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = 'regprofile_%s'
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_id = "registrationform"
