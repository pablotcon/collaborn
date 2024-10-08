from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def get_default_user():
    return User.objects.first().id if User.objects.exists() else None

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
class Chat(models.Model):
    participantes = models.ManyToManyField(User)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat entre {', '.join(participante.username for participante in self.participantes.all())}"
class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    imagen = models.ImageField(upload_to='proyectos/', blank=True, null=True)
    categoria = models.CharField(max_length=100, choices=[
        ('tecnologia', 'Tecnología'),
        ('educacion', 'Educación'),
        ('salud', 'Salud'),
        ('finanzas', 'Finanzas'),
        ('energia', 'Energía'),
        ('animales', 'Animales'),
    ], default='tecnologia')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos_creados')
    colaboradores = models.ManyToManyField(User, related_name='proyectos_colaborados')
    def __str__(self):
        return self.nombre

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin <= self.fecha_inicio:
                raise ValidationError('La fecha de fin debe ser posterior a la fecha de inicio.')
            
class Tarea(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='tareas', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    completada = models.BooleanField(default=False)
    fecha_limite = models.DateField(blank=True, null=True)
    asignada_a = models.ForeignKey(User, related_name='tareas_asignadas', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Subtarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='subtareas')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_limite = models.DateTimeField()
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class SeguimientoTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='seguimientos')
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

class ComentarioTarea(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.texto[:20]

class Actividad(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion}"

class Comentario(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='comentarios', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comentario por {self.autor} en {self.proyecto}'



# models.py
class Postulacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    fecha_postulacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('proyecto', 'usuario')

 
# Modelo Notificaciones
class Notificacion(models.Model):
    receptor = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    url = models.CharField(max_length=200, default='/mensajes/')  # Provee un valor por defecto
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notificación para {self.receptor.username}: {self.mensaje}'
    
class Conversacion(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    usuario1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones_usuario1')
    usuario2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversaciones_usuario2')

    def __str__(self):
        return f'Conversacion entre {self.usuario1.username} y {self.usuario2.username} sobre {self.proyecto.nombre}'
        
class Mensaje(models.Model):
    emisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='mensajes/', null=True, blank=True)  # Añadido campo imagen
    leido = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Mensaje de {self.emisor.username} a {self.receptor.username}'

class Recurso(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='recursos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=30, blank=True, null=True)
    apellido = models.CharField(max_length=30, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    habilidad_1 = models.CharField(max_length=100, blank=True, null=True)
    habilidad_2 = models.CharField(max_length=100, blank=True, null=True)
    habilidad_3 = models.CharField(max_length=100, blank=True, null=True)
    experiencia = models.TextField(blank=True, null=True)
    especialidad = models.CharField(max_length=200, blank=True, null=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    disponibilidad = models.BooleanField(blank=True, null=True)
    def __str__(self):
        return f'{self.nombre} {self.apellido or ""}'


class ExperienciaLaboral(models.Model):
    perfil = models.ForeignKey(Perfil, related_name='experiencias', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.titulo

class Educacion(models.Model):
    perfil = models.ForeignKey(Perfil, related_name='educaciones', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, blank=True, null=True)
    institucion = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.titulo
    

class Valoracion(models.Model):
    especialista = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='valoraciones')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comentario = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.puntuacion} - {self.especialista.nombre}'


class ConversacionOculta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    usuario_oculto = models.ForeignKey(User, related_name='ocultado_por', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'usuario_oculto')

    def __str__(self):
        return f"{self.usuario.username} oculta {self.usuario_oculto.username}"
    