# Generated by Django 3.2.5 on 2022-10-06 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0005_auto_20211123_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountaction',
            name='linked_sub',
            field=models.CharField(default=None, max_length=128, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='opcode',
            field=models.CharField(choices=[('update', 'update'), ('update_display_only', 'update display only'), ('update_verify_new_email', 'update with email change'), ('create', 'create')], default='create', max_length=32),
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='research_domain',
            field=models.CharField(choices=[('business_management', 'Business/Management'), ('physical_sciences', 'Physical Sciences'), ('arts_humanities', 'Arts/Humanities'), ('life_sciences', 'Life Sciences'), ('stats_math', 'Statistics/Math'), ('engineering', 'Engineering'), ('public_health_medicine', 'Public Health/Medicine'), ('other', 'Other'), ('social_sciences', 'Social Sciences')], default='other', max_length=128),
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='sub',
            field=models.CharField(default=None, max_length=128, null=True, unique=True),
        ),
    ]
