# forms.py
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from .models import Recurso, Perfil, Comentario, Mensaje, Proyecto, Tarea, ExperienciaLaboral, Educacion, SeguimientoTarea, Subtarea, ComentarioTarea, Categoria, Valoracion
from django.utils import timezone
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class PerfilForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )

    class Meta:
        model = Perfil
        fields = ['nombre', 'apellido', 'telefono', 'fecha_nacimiento', 'avatar', 'website', 'twitter', 'facebook', 'linkedin', 'habilidades', 'experiencia']
        widgets = {
            'habilidades': forms.Textarea(attrs={'rows': 3}),
            'experiencia': forms.Textarea(attrs={'rows': 5}),
        }


class ExperienciaLaboralForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )
    fecha_fin = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )

    
    class Meta:
        model = ExperienciaLaboral
        fields = ['titulo', 'fecha_inicio', 'fecha_fin', 'descripcion']

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        if fecha_inicio > timezone.now().date():
            raise ValidationError("La fecha de inicio no puede ser una fecha futura.")
        return fecha_inicio


class EducacionForm(forms.ModelForm):
    fecha_inicio = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )
    fecha_fin = forms.DateField(
        required=False,
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )

    class Meta:
        model = Educacion
        fields = ['titulo', 'institucion', 'fecha_inicio', 'fecha_fin']

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        if fecha_inicio > timezone.now().date():
            raise ValidationError("La fecha de inicio no puede ser una fecha futura.")
        return fecha_inicio

ExperienciaLaboralFormSet = inlineformset_factory(Perfil, ExperienciaLaboral, form=ExperienciaLaboralForm, extra=0, can_delete=True)
EducacionFormSet = inlineformset_factory(Perfil, Educacion, form=EducacionForm, extra=0, can_delete=True)

class ValoracionForm(forms.ModelForm):
    class Meta:
        model = Valoracion
        fields = ['puntuacion', 'comentario']
        widgets = {
            'puntuacion': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu comentario aquí...'}),
        }

class MensajeForm(forms.ModelForm):
    receptor_username = forms.CharField(
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario del destinatario'})
    )
    imagen = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}))

    class Meta:
        model = Mensaje
        fields = ['receptor_username', 'contenido', 'imagen']

    def clean(self):
        cleaned_data = super().clean()
        contenido = cleaned_data.get("contenido")
        imagen = cleaned_data.get("imagen")

        if not contenido and not imagen:
            raise forms.ValidationError("Debe proporcionar al menos un mensaje o una imagen.")
        
class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ['titulo', 'descripcion', 'archivo']

class ProyectoForm(forms.ModelForm):
    CIUDADES_CHOICES = [
        ('santiago', 'Santiago'),
        ('valparaiso', 'Valparaíso'),
        ('concepcion', 'Concepción'),
        ('la_serena', 'La Serena'),
        ('antofagasta', 'Antofagasta'),
        ('temuco', 'Temuco'),
        ('rancagua', 'Rancagua'),
        ('iquique', 'Iquique'),
        ('puerto_montt', 'Puerto Montt'),
    ]

    CATEGORIAS_CHOICES = [
        ('tecnologia', 'Tecnología'),
        ('educacion', 'Educación'),
        ('salud', 'Salud'),
        ('finanzas', 'Finanzas'),
        ('energia', 'Energía'),
        ('animales', 'Animales'),
    ]

    fecha_inicio = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'id': 'id_fecha_inicio', 'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'}),
        label='Fecha de inicio de postulaciones'
    )
    fecha_fin = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'id': 'id_fecha_fin', 'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'}),
        label='Fecha de cierre de postulaciones'
    )
    ciudad = forms.ChoiceField(
        choices=CIUDADES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Ciudad'
    )
    imagen = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Imagen del proyecto'
    )
    categoria = forms.ChoiceField(
        choices=CATEGORIAS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Categoría'
    )

    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'ciudad', 'imagen', 'categoria']

class TareaForm(forms.ModelForm):
    fecha_limite = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )

    class Meta:
        model = Tarea
        fields = ['nombre', 'descripcion', 'fecha_limite', 'asignada_a']

class SubtareaForm(forms.ModelForm):
    fecha_limite = forms.DateField(
        input_formats=['%d-%m-%Y'],
        widget=forms.DateInput(format='%d-%m-%Y', attrs={'class': 'form-control datepicker', 'placeholder': 'DD-MM-YYYY'})
    )

    class Meta:
        model = Subtarea
        fields = ['nombre', 'descripcion', 'fecha_limite', 'completada']

class SeguimientoTareaForm(forms.ModelForm):
    class Meta:
        model = SeguimientoTarea
        fields = ['comentario']

class ComentarioTareaForm(forms.ModelForm):
    class Meta:
        model = ComentarioTarea
        fields = ['texto']
