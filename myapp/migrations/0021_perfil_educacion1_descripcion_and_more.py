# Generated by Django 5.0.6 on 2024-07-06 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_rename_fecha_notificacion_fecha_creacion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='educacion1_descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='educacion1_fecha',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='educacion1_institucion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='educacion2_descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='educacion2_fecha',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='educacion2_institucion',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='experiencia1_descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='experiencia1_fecha',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='experiencia1_titulo',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='experiencia2_descripcion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='experiencia2_fecha',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='perfil',
            name='experiencia2_titulo',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
