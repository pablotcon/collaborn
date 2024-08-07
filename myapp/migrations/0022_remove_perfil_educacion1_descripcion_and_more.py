# Generated by Django 5.0.6 on 2024-07-06 22:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0021_perfil_educacion1_descripcion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='perfil',
            name='educacion1_descripcion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='educacion1_fecha',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='educacion1_institucion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='educacion2_descripcion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='educacion2_fecha',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='educacion2_institucion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='experiencia1_descripcion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='experiencia1_fecha',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='experiencia1_titulo',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='experiencia2_descripcion',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='experiencia2_fecha',
        ),
        migrations.RemoveField(
            model_name='perfil',
            name='experiencia2_titulo',
        ),
        migrations.CreateModel(
            name='Educacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institucion', models.CharField(max_length=200)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educaciones', to='myapp.perfil')),
            ],
        ),
        migrations.CreateModel(
            name='ExperienciaLaboral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('perfil', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiencias', to='myapp.perfil')),
            ],
        ),
    ]
