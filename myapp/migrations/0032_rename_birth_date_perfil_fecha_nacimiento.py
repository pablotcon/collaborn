# Generated by Django 5.0.6 on 2024-07-08 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0031_educacion_titulo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='perfil',
            old_name='birth_date',
            new_name='fecha_nacimiento',
        ),
    ]
