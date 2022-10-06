"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django import forms
from crispy_forms.helper import FormHelper
from .models import AccountAction


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
