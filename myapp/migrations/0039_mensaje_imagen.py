# Generated by Django 5.0.6 on 2024-07-30 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0038_remove_mensaje_imagen'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensaje',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='mensajes/'),
        ),
    ]
