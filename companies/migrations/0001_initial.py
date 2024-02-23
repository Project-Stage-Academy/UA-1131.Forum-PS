from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Companies',
            fields=[
                ('company_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank=True, max_length=255)),
                ('is_registered', models.BooleanField(default=False)),
                ('common_info', models.TextField(blank=True)),
                ('contact_phone', models.CharField(blank=True, max_length=255)),
                ('contact_email', models.CharField(blank=True, max_length=255)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('edrpou', models.IntegerField(blank=True)),
                ('address', models.TextField(blank=True, max_length=255)),
                ('product_info', models.TextField(blank=True)),
                ('startup_idea', models.TextField(blank=True)),
                ('tags', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CompaniesAndUsersRelations',
            fields=[
                ('relation_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('position', models.IntegerField()),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.companies')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
