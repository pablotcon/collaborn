# Generated by Django 5.0.6 on 2024-07-04 22:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_remove_perfil_avatar_perfil_birth_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comentario',
            name='proyecto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comentarios', to='myapp.proyecto'),
        ),
    ]
