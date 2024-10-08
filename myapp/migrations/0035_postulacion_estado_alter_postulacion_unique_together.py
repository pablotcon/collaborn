# Generated by Django 5.0.6 on 2024-07-19 00:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0034_alter_notificacion_mensaje_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='postulacion',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='postulacion',
            unique_together={('proyecto', 'usuario')},
        ),
    ]
