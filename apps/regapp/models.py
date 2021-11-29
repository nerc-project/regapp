"""
Author: Jim Culbert
Copyright (c) 2021 MGHPCC
All rights reserved. No warranty, explicit or implicit, provided.
"""

from django.db import models


# Create your models here.
class TimeStampedModel(models.Model):
    """
    Not a table. Acts as a base to add fields
    create/update timestamps at no cost
    """
    created_on = models.DateTimeField(auto_now_add=True)  # stored UTC
    updated_on = models.DateTimeField(auto_now=True)  # stored UTC

    class Meta:
        abstract = True

    def update(self, **kwargs):
        """
        Helper method to update objects while automatically
        refreshing the updated_on timestamp
        """
        update_fields = {"updated_on"}
        for k, v in kwargs.items():
            setattr(self, k, v)
            update_fields.add(k)
        self.save(update_fields=update_fields)


class AccountAction(TimeStampedModel):
    OPERATION_CHOICES = {
        ('create', 'create'),
        ('update', 'update'),
        ('update_verify_new_email', 'update with email change'),
        ('update_display_only', 'update display only')
    }

    RESEARCH_DOMAIN_CHOICES = {
        ('life_sciences', 'Life Sciences'),
        ('physical_sciences', 'Physical Sciences'),
        ('stats_math', 'Statistics/Math'),
        ('social_sciences', 'Social Sciences'),
        ('arts_humanities', 'Arts/Humanities'),
        ('public_health_medicine', 'Public Health/Medicine'),
        ('engineering', 'Engineering'),
        ('business_management', 'Business/Management'),
        ('other', 'Other'),
    }

    @staticmethod
    def _rd_name_from_id(research_domain_id):
        rd_name = "Other"
        for rd in AccountAction.RESEARCH_DOMAIN_CHOICES:
            if rd[0] == research_domain_id:
                rd_name = rd[1]

        return rd_name

    """Holds state while email is being verified"""
    regcode = models.CharField(max_length=128, unique=True, default="")
    opcode = models.CharField(
        max_length=32,
        choices=OPERATION_CHOICES,
        default='create'
    )
    sub = models.CharField(max_length=128, unique=True, null=True)
    linked_sub = models.CharField(max_length=128, unique=True, default="")
    linked_iss = models.CharField(max_length=128, default="")
    linked_idp_name = models.CharField(max_length=128, default="")
    firstName = models.CharField(max_length=128)
    lastName = models.CharField(max_length=128)
    email = models.EmailField(max_length=128, unique=True)
    username = models.CharField(max_length=128)
    research_domain = models.CharField(
        max_length=128,
        choices=RESEARCH_DOMAIN_CHOICES,
        default='other'
    )

    @property
    def research_domain_name(self):
        return AccountAction._rd_name_from_id(self.research_domain)
