# Generated by Django 3.2.5 on 2021-11-09 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0003_accountaction_research_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountaction',
            name='opcode',
            field=models.CharField(choices=[('update_verify_new_email', 'update with email change'), ('update_display_only', 'update display only'), ('update', 'update'), ('create', 'create')], default='create', max_length=32),
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='research_domain',
            field=models.CharField(choices=[('life_sciences', 'Life Sciences'), ('business_management', 'Business/Management'), ('stats_math', 'Statistics/Math'), ('engineering', 'Engineering'), ('public_health_medicine', 'Public Health/Medicine'), ('other', 'Other'), ('arts_humanities', 'Arts/Humanities'), ('social_sciences', 'Social Sciences'), ('physical_sciences', 'Physical Sciences')], default='other', max_length=128),
        ),
    ]