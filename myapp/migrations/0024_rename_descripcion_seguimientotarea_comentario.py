# Generated by Django 5.0.6 on 2024-07-07 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0023_seguimientotarea'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seguimientotarea',
            old_name='descripcion',
            new_name='comentario',
        ),
    ]