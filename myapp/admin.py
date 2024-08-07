from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from .models import Proyecto, Comentario, Mensaje, Notificacion, Recurso, Perfil, Tarea
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Crear grupo de administradores
    admin_group, created = Group.objects.get_or_create(name='Administradores')
    if created:
        admin_perms = Permission.objects.filter(content_type__model__in=['proyecto', 'tarea'])
        admin_group.permissions.set(admin_perms)

    # Crear grupo de colaboradores
    collaborator_group, created = Group.objects.get_or_create(name='Colaboradores')
    if created:
        collaborator_perms = Permission.objects.filter(content_type__model__in=['proyecto', 'tarea'])
        collaborator_group.permissions.set(collaborator_perms)

    # Crear grupo de visitantes
    visitor_group, created = Group.objects.get_or_create(name='Visitantes')
    if created:
        visitor_perms = Permission.objects.filter(content_type__model='proyecto')
        visitor_group.permissions.set(visitor_perms)

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_inicio', 'fecha_fin')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('proyecto', 'autor', 'fecha_creacion')
    search_fields = ('texto',)
    list_filter = ('fecha_creacion', 'autor')

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('emisor', 'receptor', 'fecha_envio')
    search_fields = ('contenido',)
    list_filter = ('fecha_envio', 'emisor', 'receptor')

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('receptor_username', 'mensaje', 'fecha_creacion', 'leido')
    list_filter = ('leido', 'fecha_creacion', 'receptor__username')

    def receptor_username(self, obj):
        return obj.receptor.username
    receptor_username.admin_order_field = 'receptor'
    receptor_username.short_description = 'Receptor Username'

@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'proyecto', 'completada', 'fecha_limite', 'asignada_a')
    list_filter = ('proyecto', 'completada', 'fecha_limite', 'asignada_a')
    search_fields = ('nombre', 'descripcion')

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_subida')
    search_fields = ('titulo',)
    list_filter = ('fecha_subida',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'fecha_nacimiento', 'website', 'twitter', 'facebook', 'linkedin')
    list_filter = ('fecha_nacimiento', 'user')
    search_fields = ('user__username', 'telefono')
