# Generated by Django 5.0.2 on 2024-02-19 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_alter_companies_edrpou'),
    ]

    operations = [
        migrations.RenameField(
            model_name='company',
            old_name='is_startup',
            new_name='is_startup',
        ),
    ]
