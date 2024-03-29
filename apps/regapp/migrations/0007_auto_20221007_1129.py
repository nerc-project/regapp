# Generated by Django 3.2.5 on 2022-10-07 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0006_auto_20221006_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountaction',
            name='accepted_terms_version',
            field=models.CharField(default=None, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='research_domain',
            field=models.CharField(choices=[('stats_math', 'Statistics/Math'), ('other', 'Other'), ('business_management', 'Business/Management'), ('engineering', 'Engineering'), ('physical_sciences', 'Physical Sciences'), ('social_sciences', 'Social Sciences'), ('public_health_medicine', 'Public Health/Medicine'), ('life_sciences', 'Life Sciences'), ('arts_humanities', 'Arts/Humanities')], default='other', max_length=128),
        ),
    ]
