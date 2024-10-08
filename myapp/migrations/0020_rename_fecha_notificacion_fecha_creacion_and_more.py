# Generated by Django 5.0.6 on 2024-07-06 08:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0019_alter_notificacion_receptor'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='notificacion',
            old_name='fecha',
            new_name='fecha_creacion',
        ),
        migrations.AddField(
            model_name='notificacion',
            name='url',
            field=models.CharField(default='/', max_length=200),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='mensaje',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='receptor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to=settings.AUTH_USER_MODEL),
        ),
    ]
