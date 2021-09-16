"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django import forms
from crispy_forms.helper import FormHelper


class CreateAccountForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label="Preferred Userame",
        initial="zoobert"
    )
    first_name = forms.CharField(
        max_length=100,
        label="First Name",
        initial="Valerie"
    )
    last_name = forms.CharField(
        max_length=100,
        label="Last Name",
        initial="Culbert"
    )
    email = forms.EmailField(
        max_length=100,
        label="Email",
        initial="clambake@mghpcc.org"
    )

    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = 'regprofile_%s'
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_id = "registrationform"
