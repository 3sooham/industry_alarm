# Generated by Django 3.2.5 on 2021-11-09 03:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_alter_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='EveAccessToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.TextField()),
                ('expires_in', models.DateTimeField(default=django.utils.timezone.now)),
                ('token_type', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='eve_token', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]