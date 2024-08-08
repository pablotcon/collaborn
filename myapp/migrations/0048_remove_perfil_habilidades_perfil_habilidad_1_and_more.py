# Generated by Django 5.0.6 on 2024-08-08 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0047_alter_perfil_habilidades_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfil',
            name='habilidades',
        ),
        migrations.AddField(
            model_name='perfil',
            name='habilidad_1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='habilidad_2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='habilidad_3',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
