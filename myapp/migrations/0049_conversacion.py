# Generated by Django 5.0.6 on 2024-08-08 13:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0048_remove_perfil_habilidades_perfil_habilidad_1_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.proyecto')),
                ('usuario1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_usuario1', to=settings.AUTH_USER_MODEL)),
                ('usuario2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversaciones_usuario2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]