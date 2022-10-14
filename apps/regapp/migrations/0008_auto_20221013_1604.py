# Generated by Django 3.2.5 on 2022-10-13 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regapp', '0007_auto_20221007_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('sub', models.CharField(default=None, max_length=128, null=True, unique=True)),
                ('firstName', models.CharField(max_length=128)),
                ('lastName', models.CharField(max_length=128)),
                ('email', models.EmailField(max_length=128)),
                ('username', models.CharField(max_length=128)),
                ('notification_date', models.DateTimeField()),
                ('notification_type', models.CharField(choices=[('terms', 'Terms agreement is out of date')], default='terms', max_length=32)),
                ('notification_data', models.JSONField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='opcode',
            field=models.CharField(choices=[('update_display_only', 'update display only'), ('create', 'create'), ('update_verify_new_email', 'update with email change'), ('update', 'update')], default='create', max_length=32),
        ),
        migrations.AlterField(
            model_name='accountaction',
            name='research_domain',
            field=models.CharField(choices=[('public_health_medicine', 'Public Health/Medicine'), ('arts_humanities', 'Arts/Humanities'), ('life_sciences', 'Life Sciences'), ('social_sciences', 'Social Sciences'), ('other', 'Other'), ('stats_math', 'Statistics/Math'), ('engineering', 'Engineering'), ('business_management', 'Business/Management'), ('physical_sciences', 'Physical Sciences')], default='other', max_length=128),
        ),
    ]
