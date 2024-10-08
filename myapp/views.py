import datetime
from django.forms import ModelForm, modelform_factory
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.db.models import Q , Count
from django.contrib import messages
from .models import Proyecto, Postulacion, User, Notificacion, Mensaje, Recurso, Perfil, Comentario, Tarea, Actividad, SeguimientoTarea, Subtarea, Educacion, ExperienciaLaboral
from .forms import RecursoForm, PerfilForm, ComentarioForm, UserForm, MensajeForm, ProyectoForm, TareaForm, SeguimientoTareaForm,EducacionFormSet, ExperienciaLaboralFormSet, EducacionForm, SubtareaForm, ComentarioTareaForm, ExperienciaLaboralForm,ValoracionForm, BusquedaEspecialistaForm,DisponibilidadForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from channels.layers import get_channel_layer
from django.urls import reverse
import json
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.forms import modelformset_factory
from django.core.paginator import Paginator



@login_required
def actualizar_disponibilidad(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        form = DisponibilidadForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('ver_mi_perfil')
    else:
        form = DisponibilidadForm(instance=perfil)
    
    return render(request, 'actualizar_disponibilidad.html', {'form': form})



def listar_especialistas(request):
    habilidad = request.GET.get('habilidad', '')

    especialistas = User.objects.exclude(id=request.user.id)  # Excluir al usuario logueado

    if habilidad:
        especialistas = especialistas.filter(
            perfil__habilidad_1__icontains=habilidad
        ) | especialistas.filter(
            perfil__habilidad_2__icontains=habilidad
        ) | especialistas.filter(
            perfil__habilidad_3__icontains=habilidad
        )

    paginator = Paginator(especialistas, 10)  # Mostrar 10 especialistas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'habilidad': habilidad,
    }
    return render(request, 'myapp/listar_especialistas.html', context)





#Busqueda Especialista:
def buscar_especialistas(request):
    form = BusquedaEspecialistaForm(request.GET or None)
    resultados = Perfil.objects.all()
    
    if form.is_valid():
        especialidad = form.cleaned_data.get('especialidad')
        ubicacion = form.cleaned_data.get('ubicacion')
        disponibilidad = form.cleaned_data.get('disponibilidad')
        
        if especialidad:
            resultados = resultados.filter(especialidad__icontains=especialidad)
        if ubicacion:
            resultados = resultados.filter(ubicacion__icontains=ubicacion)
        if disponibilidad is not None:
            resultados = resultados.filter(disponibilidad=disponibilidad)
    
    context = {
        'form': form,
        'resultados': resultados,
    }
    return render(request, 'buscar_especialistas.html', context)

# Functions related to Task Management
@login_required
def admin_panel_tareas(request):
    if not request.user.is_staff:
        return redirect('index')
    
    proyectos = Proyecto.objects.all()
    tareas_por_proyecto = {proyecto: Tarea.objects.filter(proyecto=proyecto) for proyecto in proyectos}
    
    return render(request, 'myapp/admin_panel_tareas.html', {'tareas_por_proyecto': tareas_por_proyecto})

@login_required
def actualizar_estado_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        tarea.completada = not tarea.completada
        tarea.save()
        messages.success(request, 'El estado de la tarea ha sido actualizado.')
    return redirect('detalle_tarea', tarea_id=tarea.id)

@login_required
def detalle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    subtareas = tarea.subtareas.all()
    seguimientos = SeguimientoTarea.objects.filter(tarea=tarea).order_by('-fecha')
    comentarios = tarea.comentarios.all().order_by('-fecha_creacion')

    if request.method == 'POST':
        if 'comentario' in request.POST:
            comentario_form = ComentarioTareaForm(request.POST)
            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.tarea = tarea
                comentario.autor = request.user
                comentario.save()
                return redirect('detalle_tarea', tarea_id=tarea.id)
        elif 'seguimiento' in request.POST:
            seguimiento_form = SeguimientoTareaForm(request.POST)
            if seguimiento_form.is_valid():
                seguimiento = seguimiento_form.save(commit=False)
                seguimiento.tarea = tarea
                seguimiento.autor = request.user
                seguimiento.save()
                return redirect('detalle_tarea', tarea_id=tarea.id)
        elif 'subtarea' in request.POST:
            subtarea_form = SubtareaForm(request.POST)
            if subtarea_form.is_valid():
                subtarea = subtarea_form.save(commit=False)
                subtarea.tarea = tarea
                subtarea.save()
                return redirect('detalle_tarea', tarea_id=tarea.id)
    else:
        comentario_form = ComentarioTareaForm()
        seguimiento_form = SeguimientoTareaForm()
        subtarea_form = SubtareaForm()

    return render(request, 'myapp/detalle_tarea.html', {
        'tarea': tarea,
        'subtareas': subtareas,
        'seguimientos': seguimientos,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
        'seguimiento_form': seguimiento_form,
        'subtarea_form': subtarea_form
    })

@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    next_url = request.GET.get('next', 'proyecto_lista')  # Por defecto redirige a 'proyecto_lista' si 'next' no está presente

    if request.method == 'POST':
        if 'confirm' in request.POST:
            tarea.delete()
            messages.success(request, 'Tarea eliminada exitosamente.')
            return redirect(next_url)
        elif 'cancel' in request.POST:
            messages.info(request, 'Eliminación cancelada.')
            return redirect(next_url)

    return render(request, 'myapp/eliminar_tarea.html', {'tarea': tarea, 'next': next_url})

@login_required
@permission_required('myapp.add_tarea', raise_exception=True)
def agregar_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.proyecto = proyecto
            tarea.save()

            # Crear una notificación para el usuario asignado a la tarea
            if tarea.asignada_a:
                Notificacion.objects.create(
                    receptor=tarea.asignada_a,
                    mensaje=f"Se te ha asignado una nueva tarea: {tarea.nombre}",
                    url=f"/tareas/{tarea.id}/"
                )

            messages.success(request, 'Tarea agregada exitosamente.')
            return redirect('listar_tareas', proyecto_id=proyecto.id)
        else:
            messages.error(request, 'Error al agregar la tarea.')
    else:
        form = TareaForm()
    return render(request, 'myapp/agregar_tarea.html', {'form': form, 'proyecto': proyecto})

@login_required

def agregar_subtarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = SubtareaForm(request.POST)
        if form.is_valid():
            subtarea = form.save(commit=False)
            subtarea.tarea = tarea
            subtarea.save()
            messages.success(request, 'Subtarea agregada exitosamente.')
            return redirect('detalle_tarea', tarea_id=tarea.id)
        else:
            messages.error(request, 'Error al agregar la subtarea.')
    else:
        form = SubtareaForm()
    return render(request, 'myapp/agregar_subtarea.html', {'form': form, 'tarea': tarea})


@login_required
def listar_tareas(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    tareas = Tarea.objects.filter(proyecto=proyecto)
    
    query = request.GET.get('q')
    if query:
        tareas = tareas.filter(nombre__icontains=query)
    
    return render(request, 'myapp/listar_tareas.html', {'proyecto': proyecto, 'tareas': tareas})

@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    proyecto_id = tarea.proyecto.id
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea editada exitosamente.')
            return redirect('listar_tareas', proyecto_id=proyecto_id)
        else:
            messages.error(request, 'Error al editar la tarea.')
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'myapp/editar_tarea.html', {'form': form, 'proyecto_id': proyecto_id})

@login_required
def confirmar_eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, 'Tarea eliminada exitosamente.')
        return redirect('admin_panel_tareas')
    return render(request, 'myapp/confirmar_eliminar_tarea.html', {'tarea': tarea})

@login_required
def seguir_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    seguimiento, created = SeguimientoTarea.objects.get_or_create(usuario=request.user, tarea=tarea)
    if created:
        messages.success(request, 'Ahora sigues esta tarea.')
    else:
        messages.info(request, 'Ya sigues esta tarea.')
    return redirect('detalle_tarea', tarea_id=tarea_id)

@login_required
def dejar_seguir_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    seguimiento = get_object_or_404(SeguimientoTarea, usuario=request.user, tarea=tarea)
    seguimiento.delete()
    messages.success(request, 'Has dejado de seguir esta tarea.')
    return redirect('detalle_tarea', tarea_id=tarea_id)

@login_required
def listar_seguimientos(request):
    seguimientos = request.user.seguimientos.all()
    return render(request, 'myapp/listar_seguimientos.html', {'seguimientos': seguimientos})

@login_required
def agregar_seguimiento(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = SeguimientoTareaForm(request.POST)
        if form.is_valid():
            seguimiento = form.save(commit=False)
            seguimiento.tarea = tarea
            seguimiento.usuario = request.user
            seguimiento.save()
            return redirect('detalle_tarea', tarea_id=tarea.id)
    else:
        form = SeguimientoTareaForm()
    return render(request, 'myapp/detalle_tarea.html', {'tarea': tarea, 'form': form})

@login_required
def actualizar_estado_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        tarea.completada = not tarea.completada
        tarea.save()
        messages.success(request, 'El estado de la tarea ha sido actualizado.')
    return redirect('detalle_tarea', tarea_id=tarea.id)

# Function to send notifications
def send_notification(user, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}", 
        {
            "type": "user_notification",
            "message": message,
        }
    )

def user_notification(event):
    message = event['message']
    # Note: 'self' is not defined in this function; this part needs to be adjusted
    self.send(text_data=json.dumps({
        'message': message
    }))




# Functions related to User Profile

@login_required
def editar_perfil(request):
    perfil = request.user.perfil

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil)
        experiencia_formset = ExperienciaLaboralFormSet(request.POST, request.FILES, instance=perfil)
        educacion_formset = EducacionFormSet(request.POST, request.FILES, instance=perfil)

        if user_form.is_valid() and perfil_form.is_valid() and experiencia_formset.is_valid() and educacion_formset.is_valid():
            user_form.save()
            perfil_form.save()
            experiencia_formset.save()
            educacion_formset.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('ver_perfil', user_id=request.user.id)
        else:
            print(user_form.errors)
            print(perfil_form.errors)
            print(experiencia_formset.errors)
            print(educacion_formset.errors)
    else:
        user_form = UserForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)
        experiencia_formset = ExperienciaLaboralFormSet(instance=perfil)
        educacion_formset = EducacionFormSet(instance=perfil)

    return render(request, 'myapp/editar_perfil.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'experiencia_formset': experiencia_formset,
        'educacion_formset': educacion_formset,
        'experiencias': perfil.experiencias.all(),
        'educaciones': perfil.educaciones.all(),
    })
@login_required
def editar_experiencia(request, pk):
    experiencia = get_object_or_404(ExperienciaLaboral, pk=pk)
    if request.method == 'POST':
        form = ExperienciaLaboralForm(request.POST, instance=experiencia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Experiencia actualizada exitosamente.')
            return redirect('editar_perfil')
    else:
        form = ExperienciaLaboralForm(instance=experiencia)
    return render(request, 'myapp/editar_experiencia.html', {'form': form})

@login_required
def eliminar_experiencia(request, pk):
    experiencia = get_object_or_404(ExperienciaLaboral, pk=pk)
    if request.method == 'POST':
        experiencia.delete()
        messages.success(request, 'Experiencia eliminada exitosamente.')
        return redirect('editar_perfil')
    return render(request, 'myapp/eliminar_experiencia.html', {'experiencia': experiencia})

@login_required
def editar_educacion(request, pk):
    educacion = get_object_or_404(Educacion, pk=pk)
    if request.method == 'POST':
        form = EducacionForm(request.POST, instance=educacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Educación actualizada exitosamente.')
            return redirect('editar_perfil')
    else:
        form = EducacionForm(instance=educacion)
    return render(request, 'myapp/editar_educacion.html', {'form': form})

@login_required
def eliminar_educacion(request, pk):
    educacion = get_object_or_404(Educacion, pk=pk)
    if request.method == 'POST':
        educacion.delete()
        messages.success(request, 'Educación eliminada exitosamente.')
        return redirect('editar_perfil')
    return render(request, 'myapp/eliminar_educacion.html', {'educacion': educacion})


@login_required
def ver_mi_perfil(request):
    return redirect('ver_perfil', user_id=request.user.id)


@login_required
def ver_perfil(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    perfil = usuario.perfil

    if request.method == 'POST':
        if 'toggle_disponibilidad' in request.POST:
            perfil.disponibilidad = not perfil.disponibilidad
            perfil.save()
        return redirect('ver_perfil', user_id=user_id)

    experiencias = ExperienciaLaboral.objects.filter(perfil=perfil).order_by('-fecha_inicio')
    educaciones = Educacion.objects.filter(perfil=perfil).order_by('-fecha_inicio')
    proyectos_creados = Proyecto.objects.filter(creador=usuario)
    proyectos_colaborados = Proyecto.objects.filter(colaboradores=usuario)

    context = {
        'usuario': usuario,
        'perfil': perfil,
        'experiencias': experiencias,
        'educaciones': educaciones,
        'proyectos_creados': proyectos_creados,
        'proyectos_colaborados': proyectos_colaborados,
    }
    return render(request, 'myapp/ver_perfil.html', context)
def filtrar_especialistas(request):
    query = request.GET.get('q', '')
    habilidades = request.GET.get('habilidades', '')
    ciudad = request.GET.get('ciudad', '')
    especialistas = Perfil.objects.all()

    if query:
        especialistas = especialistas.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )
    if habilidades:
        especialistas = especialistas.filter(habilidades__icontains=habilidades)
    if ciudad:
        especialistas = especialistas.filter(ciudad__icontains=ciudad)

    return render(request, 'myapp/filtrar_especialistas.html', {'especialistas': especialistas})


@login_required
def dashboard_especialista(request):
    perfil = request.user.perfil
    postulaciones = Postulacion.objects.filter(usuario=request.user)
    proyectos = Proyecto.objects.filter(creador=request.user)

    return render(request, 'myapp/dashboard_especialista.html', {
        'postulaciones': postulaciones,
        'proyectos': proyectos,
    })


@login_required
def valorar_especialista(request, especialista_id):
    especialista = Perfil.objects.get(id=especialista_id)
    if request.method == 'POST':
        form = ValoracionForm(request.POST)
        if form.is_valid():
            valoracion = form.save(commit=False)
            valoracion.especialista = especialista
            valoracion.autor = request.user
            valoracion.save()
            return redirect('ver_perfil', especialista.user.id)
    else:
        form = ValoracionForm()
    return render(request, 'myapp/valorar_especialista.html', {'form': form, 'especialista': especialista})


@login_required
def recomendar_especialistas(request, proyecto_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    habilidades_requeridas = proyecto.descripcion.split()  # Simplificación, se puede mejorar
    especialistas = Perfil.objects.filter(
        Q(habilidades__icontains=habilidades_requeridas[0]) | 
        Q(habilidades__icontains=habilidades_requeridas[1]) | 
        Q(habilidades__icontains=habilidades_requeridas[2])
    )
    return render(request, 'myapp/recomendar_especialistas.html', {'proyecto': proyecto, 'especialistas': especialistas})

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Su contraseña ha sido cambiada exitosamente.')
            return redirect('ver_perfil')
        else:
            messages.error(request, 'Por favor corrija los errores a continuación.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'myapp/cambiar_password.html', {'form': form})

# Funciones de 
@login_required
def notificaciones_ajax(request):
    notificaciones = request.user.notificacion_set.all().order_by('-fecha_creacion')[:5]  # Obtener las últimas 5 notificaciones
    notificaciones_no_leidas = request.user.notificacion_set.filter(leido=False).count()
    
    html = render_to_string('myapp/notificaciones_dropdown.html', {'notificaciones': notificaciones})
    
    return JsonResponse({
        'html': html,
        'count': notificaciones_no_leidas,
    })



@login_required
def listar_notificaciones(request):
    notificaciones = Notificacion.objects.filter(receptor=request.user).order_by('-fecha_creacion')
    return render(request, 'myapp/notificaciones.html', {'notificaciones': notificaciones})
from django.views.decorators.http import require_POST

@login_required
@require_POST
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, receptor=request.user)
    notificacion.leida = True
    notificacion.save()
    return JsonResponse({'success': True})
    
@login_required
def proyecto_lista(request):
    query = request.GET.get('q', '')
    categoria = request.GET.get('category', 'Todos')
    categories = Proyecto.objects.exclude(categoria__isnull=True).exclude(categoria__exact='').values_list('categoria', flat=True).distinct()

    # Filtrado de proyectos según la búsqueda y la categoría
    proyectos = Proyecto.objects.all()  # Obtener todos los proyectos

    if query:
        proyectos = proyectos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    if categoria != 'Todos':
        proyectos = proyectos.filter(categoria=categoria)

    # Implementación de la paginación
    paginator = Paginator(proyectos, 10)  # Mostrar 10 proyectos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/proyecto_lista.html', {
        'page_obj': page_obj,
        'categories': categories,
    })

@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            messages.success(request, 'Proyecto creado exitosamente.')
            return redirect('proyecto_detalle', proyecto_id=proyecto.id)
        else:
            messages.error(request, "Error al crear el proyecto. Por favor, revisa los campos resaltados.")
    else:
        form = ProyectoForm()
    return render(request, 'myapp/crear_proyecto.html', {'form': form})
    
@login_required
def proyecto_edit(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto editado exitosamente.')
            return redirect('proyecto_detalle', proyecto_id=proyecto.id)
        else:
            messages.error(request, 'Error al editar el proyecto.')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'myapp/editar_proyecto.html', {'form': form})

@login_required
def proyecto_detalle(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    comentarios = proyecto.comentarios.all()
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.proyecto = proyecto
            comentario.autor = request.user
            comentario.save()
            messages.success(request, 'Comentario agregado exitosamente.')
            return redirect('proyecto_detalle', proyecto_id=proyecto.id)
        else:
            messages.error(request, 'Error al agregar el comentario.')
    else:
        form = ComentarioForm()
    
    aceptados = proyecto.postulacion_set.filter(estado='aceptada')
    return render(request, 'myapp/proyecto_detalle.html', {
        'proyecto': proyecto, 
        'comentarios': comentarios, 
        'form': form,
        'aceptados': aceptados,
    })


@permission_required('myapp.delete_proyecto', raise_exception=True)
@login_required
def proyecto_delete(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        proyecto.delete()
        messages.success(request, 'Proyecto eliminado exitosamente.')
        return redirect('proyecto_lista')
    return render(request, 'myapp/confirmar_eliminar_proyecto.html', {'proyecto': proyecto})

@login_required
@permission_required('myapp.delete_proyecto', raise_exception=True)
def confirmar_eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    if request.method == 'POST':
        proyecto.delete()
        messages.success(request, 'Proyecto eliminado exitosamente.')
        return redirect('proyecto_lista')
    return render(request, 'myapp/confirmar_eliminar_proyecto.html', {'proyecto': proyecto})


## gestion proyecto ###
@login_required
@permission_required('myapp.change_proyecto', raise_exception=True)
def gestionar_postulaciones(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    postulaciones = proyecto.postulacion_set.all()

    if request.method == 'POST':
        accion = request.POST.get('accion')
        postulacion_id = request.POST.get('postulacion_id')
        postulacion = get_object_or_404(Postulacion, id=postulacion_id)

        if accion == 'aceptar':
            postulacion.estado = 'aceptada'
            postulacion.save()
            messages.success(request, 'La postulación ha sido aceptada.')
            Notificacion.objects.create(
                receptor=postulacion.usuario,
                mensaje=f'Tu postulación al proyecto "{postulacion.proyecto.nombre}" ha sido aceptada.'
            )
        elif accion == 'rechazar':
            postulacion.estado = 'rechazada'
            postulacion.save()
            messages.success(request, 'La postulación ha sido rechazada.')
            Notificacion.objects.create(
                receptor=postulacion.usuario,
                mensaje=f'Tu postulación al proyecto "{postulacion.proyecto.nombre}" ha sido rechazada.'
            )
        elif accion == 'eliminar':
            postulacion.delete()
            messages.success(request, 'El postulante ha sido eliminado del proyecto.')
    
    return render(request, 'myapp/gestionar_postulaciones.html', {
        'proyecto': proyecto,
        'postulaciones': postulaciones,
    })

### POSTULAR PROYECTO ###
from .models import Proyecto, Postulacion, Notificacion, Mensaje, Conversacion
@login_required
def postular_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        postulacion, created = Postulacion.objects.get_or_create(proyecto=proyecto, usuario=request.user)
        if not created:
            messages.error(request, 'Ya te has postulado a este proyecto.')
        else:
            # Crear notificación para el creador del proyecto
            Notificacion.objects.create(
                receptor=proyecto.creador,
                mensaje=f'El usuario {request.user.username} se ha postulado a tu proyecto "{proyecto.nombre}".',
                url=reverse('proyecto_detalle', kwargs={'proyecto_id': proyecto.id})
            )

            # Crear mensaje predeterminado en una instancia de chat
            Mensaje.objects.create(
                emisor=proyecto.creador,
                receptor=request.user,
                contenido=f"Gracias por generar interés en {proyecto.nombre}. Mientras te contactamos con el responsable del proyecto, nos gustaría saber de ti. ¡Cuéntanos por qué quieres ser parte del proyecto!"
            )

            messages.success(request, 'Te has postulado al proyecto exitosamente.')
        return redirect('proyecto_detalle', proyecto_id=proyecto_id)
    return render(request, 'myapp/proyecto_detalle.html', {'proyecto': proyecto})

### ACEPTAR POSTULACION ####
@login_required
@permission_required('myapp.change_postulacion', raise_exception=True)
def aceptar_postulacion(request, postulacion_id):
    postulacion = get_object_or_404(Postulacion, id=postulacion_id)
    if request.method == 'POST':
        postulacion.estado = 'aceptada'
        postulacion.save()
        messages.success(request, 'La postulación ha sido aceptada.')
        Notificacion.objects.create(
            receptor=postulacion.usuario,
            mensaje=f'Tu postulación al proyecto "{postulacion.proyecto.nombre}" ha sido aceptada.'
        )
    return redirect('proyecto_detalle', proyecto_id=postulacion.proyecto.id)

    
### RECHAZAR POSTULACION
@login_required
@permission_required('myapp.change_postulacion', raise_exception=True)
def rechazar_postulacion(request, postulacion_id):
    postulacion = get_object_or_404(Postulacion, id=postulacion_id)
    if request.method == 'POST':
        postulacion.estado = 'rechazada'
        postulacion.save()
        messages.success(request, 'La postulación ha sido rechazada.')
        Notificacion.objects.create(
            receptor=postulacion.usuario,
            mensaje=f'Tu postulación al proyecto "{postulacion.proyecto.nombre}" ha sido rechazada.'
        )
    return redirect('proyecto_detalle', proyecto_id=postulacion.proyecto.id)

@login_required
def mis_postulaciones(request):
    postulaciones = Postulacion.objects.filter(usuario=request.user)
    return render(request, 'myapp/mis_postulaciones.html', {'postulaciones': postulaciones})


### Funciones relacionadas a RECURSOS ###
@login_required
def recurso_detail(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk)
    return render(request, 'myapp/recurso_detail.html', {'recurso': recurso})

@permission_required('myapp.can_edit_recurso', raise_exception=True)
@login_required
def recurso_edit(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk)
    if request.method == 'POST':
        form = RecursoForm(request.POST, instance=recurso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recurso editado exitosamente.')
            return redirect('recurso_detail', pk=recurso.pk)
        else:
            messages.error(request, 'Error al editar el recurso.')
    else:
        form = RecursoForm(instance=recurso)
    return render(request, 'myapp/recurso_form.html', {'form': form})

@permission_required('myapp.can_delete_recurso', raise_exception=True)
@login_required
def recurso_delete(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk)
    if request.method == 'POST':
        recurso.delete()
        messages.success(request, 'Recurso eliminado exitosamente.')
        return redirect('listar_recursos')
    return render(request, 'myapp/recurso_confirm_delete.html', {'recurso': recurso})

@login_required
def subir_recurso(request):
    if request.method == 'POST':
        form = RecursoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_recursos')
    else:
        form = RecursoForm()
    return render(request, 'myapp/subir_recurso.html', {'form': form})

@login_required
def listar_recursos(request):
    query = request.GET.get('q')
    recursos = Recurso.objects.all()
    
    if query:
        recursos = recursos.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query)
        )

    return render(request, 'myapp/listar_recursos.html', {'recursos': recursos})

# Functions related to Messages
# views.py

@login_required
def listar_mensajes(request):
    query = request.GET.get('q')
    usuario_id = request.GET.get('usuario_id')
    ocultas = ConversacionOculta.objects.filter(usuario=request.user).values_list('usuario_oculto', flat=True)
    mensajes_recibidos = Mensaje.objects.filter(receptor=request.user).exclude(emisor__in=ocultas)
    mensajes_enviados = Mensaje.objects.filter(emisor=request.user).exclude(receptor__in=ocultas)

    if query:
        mensajes_recibidos = mensajes_recibidos.filter(contenido__icontains=query)
        mensajes_enviados = mensajes_enviados.filter(contenido__icontains=query)

    all_messages = mensajes_recibidos.union(mensajes_enviados).order_by('fecha_envio')

    usuarios = {}
    selected_user = None

    # Si se ha seleccionado un usuario (es decir, `usuario_id` está presente)
    if usuario_id:
        selected_user = get_object_or_404(User, id=usuario_id)
        mensajes = Mensaje.objects.filter(
            (Q(receptor=request.user) & Q(emisor=selected_user)) |
            (Q(emisor=request.user) & Q(receptor=selected_user))
        ).order_by('fecha_envio')

        usuarios[selected_user] = mensajes

    # Si no hay usuario seleccionado, manejar todos los mensajes
    else:
        for mensaje in all_messages:
            user = mensaje.emisor if mensaje.receptor == request.user else mensaje.receptor
            if user not in usuarios:
                usuarios[user] = []
            usuarios[user].append(mensaje)

    all_users = User.objects.exclude(id=request.user.id)

    return render(request, 'myapp/listar_mensajes.html', {
        'usuarios': usuarios,
        'all_users': all_users,
        'query': query,
        'selected_user_id': int(usuario_id) if usuario_id else None,
        'selected_user': selected_user,
    })
@login_required
def cargar_mensajes(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        try:
            user = User.objects.get(username=username)
            mensajes = Mensaje.objects.filter(
                (Q(receptor=request.user) & Q(emisor=user)) |
                (Q(emisor=request.user) & Q(receptor=user))
            ).order_by('fecha_envio')

            mensajes_data = []
            for mensaje in mensajes:
                mensajes_data.append({
                    'emisor': mensaje.emisor.username,
                    'contenido': mensaje.contenido,
                    'fecha_envio': mensaje.fecha_envio.strftime("%d-%m-%Y %H:%M"),
                    'imagen_url': mensaje.imagen.url if mensaje.imagen else None
                })

            return JsonResponse({'success': True, 'mensajes': mensajes_data})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)
    
from .models import Mensaje, Notificacion
import logging

logger = logging.getLogger(__name__)

@login_required
def enviar_mensaje(request):
    if request.method == 'POST':
        logger.info("Datos del formulario recibidos: %s", request.POST)
        logger.info("Archivos recibidos: %s", request.FILES)
        form = MensajeForm(request.POST, request.FILES)
        if form.is_valid():
            mensaje = form.save(commit=False)
            receptor_username = form.cleaned_data['receptor_username']
            try:
                receptor = User.objects.get(username=receptor_username)
                mensaje.receptor = receptor
                mensaje.emisor = request.user
                mensaje.save()
                # Crear notificación para el receptor
                chat_url = reverse('listar_mensajes') + f'?usuario_id={mensaje.emisor.id}'  # URL del chat con el emisor
                Notificacion.objects.create(
                    receptor=receptor,
                    mensaje=f"Mensaje de {request.user.username}",
                    url=chat_url
                )
                response_data = {
                    'id': mensaje.id,
                    'contenido': mensaje.contenido,
                    'fecha_envio': mensaje.fecha_envio.strftime("%d-%m-%Y %H:%M"),
                    'receptor_username': receptor.username,
                    'imagen_url': mensaje.imagen.url if mensaje.imagen else None
                }
                return JsonResponse(response_data, status=200)
            except User.DoesNotExist:
                return JsonResponse({'error': 'Usuario no encontrado.'}, status=400)
        else:
            logger.error("Error al enviar el mensaje: %s", form.errors)
            return JsonResponse({'error': 'Error al enviar el mensaje.', 'form_errors': form.errors}, status=400)
    return JsonResponse({'error': 'Método no permitido.'}, status=405)

def eliminar_mensaje(request, mensaje_id):
    if request.method == 'POST':
           
        try:
            mensaje = Mensaje.objects.get(id=mensaje_id, emisor=request.user)
            mensaje.delete()
            return redirect('listar_mensajes')  # Nombre correcto de la vista de redirección
        except Mensaje.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Mensaje no encontrado.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'})

def detalle_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(Mensaje, id=mensaje_id)

    # Marcar la notificación como leída
    notificacion = Notificacion.objects.filter(receptor=request.user, url=f"/mensajes/{mensaje_id}/").first()
    if notificacion:
        notificacion.leido = True
        notificacion.save()

    return render(request, 'myapp/detalle_mensaje.html', {'mensaje': mensaje})

from django.shortcuts import get_object_or_404





from django.db.models import Q

@login_required
def ocultar_conversacion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            usuario_oculto = User.objects.get(username=username)
            ConversacionOculta.objects.get_or_create(usuario=request.user, usuario_oculto=usuario_oculto)
            response_data = {
                'success': True,
                'user_id': usuario_oculto.id
            }
        except User.DoesNotExist:
            response_data = {
                'success': False,
                'error': 'Usuario no encontrado.'
            }
        return JsonResponse(response_data)
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)


from .models import ConversacionOculta
@login_required
def iniciar_nuevo_chat(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            ConversacionOculta.objects.filter(usuario=request.user, usuario_oculto=user).delete()
            response_data = {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }
        except User.DoesNotExist:
            response_data = {
                'success': False,
                'error': 'Usuario no encontrado.'
            }
        return JsonResponse(response_data)
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

@login_required
def cargar_mensajes(request):
    if request.method == 'GET':
        username = request.GET.get('username')
        try:
            user = User.objects.get(username=username)
            mensajes = Mensaje.objects.filter(
                (Q(receptor=request.user) & Q(emisor=user)) |
                (Q(emisor=request.user) & Q(receptor=user))
            ).order_by('fecha_envio')

            mensajes_data = []
            for mensaje in mensajes:
                mensajes_data.append({
                    'emisor': mensaje.emisor.username,
                    'contenido': mensaje.contenido,
                    'fecha_envio': mensaje.fecha_envio.strftime("%d-%m-%Y %H:%M"),
                    'imagen_url': mensaje.imagen.url if mensaje.imagen else None
                })

            return JsonResponse({'success': True, 'mensajes': mensajes_data})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})
    return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)
# Functions related to Activities

@login_required
def historial_actividades(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    actividades = Actividad.objects.filter(usuario=usuario).order_by('-fecha')
    proyectos_creados = Proyecto.objects.filter(creador=usuario)
    proyectos_colaborados = Proyecto.objects.filter(colaboradores=usuario)

    # Depuración
    print(f"Proyectos creados por {usuario.username}: {list(proyectos_creados)}")
    print(f"Proyectos colaborados por {usuario.username}: {list(proyectos_colaborados)}")

    return render(request, 'myapp/historial_actividades.html', {
        'usuario': usuario,
        'actividades': actividades,
        'proyectos_creados': proyectos_creados,
        'proyectos_colaborados': proyectos_colaborados,
    })
# User Authentication Functions
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Perfil.objects.get_or_create(user=user)
            login(request, user)
            return redirect('editar_perfil')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return render(request, 'myapp/logout.html')

@login_required
def index(request):
    # Seleccionar usuarios destacados basados en el número de proyectos en los que han colaborado.
    usuarios_destacados = User.objects.annotate(num_proyectos_colaborados=Count('proyectos_colaborados')).order_by('-num_proyectos_colaborados')[:5]
    
    # Seleccionar proyectos destacados basados en el número de colaboradores.
    proyectos_destacados = Proyecto.objects.annotate(num_colaboradores=Count('colaboradores')).order_by('-num_colaboradores')[:5]

    context = {
        'especialistas_destacados': usuarios_destacados,
        'proyectos_destacados': proyectos_destacados,
    }
    return render(request, 'myapp/index.html', context)

# Signal to save user profile upon user creation
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()


#ADMIN DASHBOARD
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    query = request.GET.get('q', '')
    filtro = request.GET.get('filtro', 'todos')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    usuario_id = request.GET.get('usuario', '')
    page = request.GET.get('page', 1)

    # Optimizar consultas usando select_related y prefetch_related
    proyectos = Proyecto.objects.all().select_related('creador').prefetch_related('tareas').order_by('fecha_inicio')
    tareas = Tarea.objects.all().select_related('asignada_a')

    # Filtrar proyectos y tareas según el término de búsqueda (query)
    if query:
        proyectos = proyectos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
        tareas = tareas.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    # Filtrar por estado (filtro)
    if filtro == 'activos':
        proyectos = proyectos.filter(fecha_fin__gt=timezone.now())
    elif filtro == 'completados':
        proyectos = proyectos.filter(fecha_fin__lte=timezone.now())

    # Filtrar por fecha de inicio y fin
    if fecha_inicio:
        proyectos = proyectos.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        proyectos = proyectos.filter(fecha_fin__lte=fecha_fin)

    # Filtrar por usuario asignado
    if usuario_id:
        tareas = tareas.filter(asignada_a_id=usuario_id)

    # Contar tareas por estado
    tareas_completadas = tareas.filter(completada=True).count()
    tareas_pendientes = tareas.filter(completada=False).count()

    # Obtener el número total de proyectos y tareas
    total_proyectos = proyectos.count()
    total_tareas = tareas.count()

    # Paginación de proyectos
    paginator = Paginator(proyectos, 10)  # 10 proyectos por página
    proyectos_page = paginator.get_page(page)

    # Obtener lista de usuarios para el filtro
    usuarios = User.objects.all()

    context = {
        'proyectos': proyectos_page,
        'tareas': tareas,
        'proyectos_activos': proyectos.filter(fecha_fin__gt=timezone.now()).count(),
        'proyectos_completados': proyectos.filter(fecha_fin__lte=timezone.now()).count(),
        'tareas_pendientes': tareas_pendientes,
        'tareas_completadas': tareas_completadas,
        'total_proyectos': total_proyectos,
        'total_tareas': total_tareas,
        'usuarios': usuarios,
        'query': query,
        'filtro': filtro,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'usuario_id': usuario_id,
        'page': page,
    }
    return render(request, 'myapp/admin_dashboard.html', context)


@login_required
def ver_chat(request, user_id):
    receptor = get_object_or_404(User, id=user_id)
    mensajes = Mensaje.objects.filter(
        (Q(emisor=request.user) & Q(receptor=receptor)) |
        (Q(emisor=receptor) & Q(receptor=request.user))
    ).order_by('fecha_envio')

    context = {
        'receptor': receptor,
        'mensajes': mensajes
    }

ogger = logging.getLogger(__name__)

@receiver(post_save, sender=Mensaje)
def notificar_mensaje(sender, instance, created, **kwargs):
    if created:
        receptor = instance.receptor
        logger.debug(f'Creando notificación para mensaje de {instance.emisor.username} a {receptor.username}')
        # Crear la URL correcta para la redirección
        url = reverse('listar_mensajes') + f'?usuario_id={instance.emisor.id}'
        if not Notificacion.objects.filter(
            receptor=receptor,
            mensaje=f'Tienes un nuevo mensaje de {instance.emisor.username}',
            url=url
        ).exists():
            Notificacion.objects.create(
                receptor=receptor,
                mensaje=f'Tienes un nuevo mensaje de {instance.emisor.username}',
                url=url
            )
            logger.debug(f'Notificación creada para mensaje de {instance.emisor.username} a {receptor.username}')

from django.http import HttpResponse

@login_required
def test_proyectos_colaborados(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    proyectos_colaborados = Proyecto.objects.filter(colaboradores=usuario)
    response = f"Proyectos colaborados por {usuario.username}:<br>"
    for proyecto in proyectos_colaborados:
        response += f"- {proyecto.nombre} (Descripción: {proyecto.descripcion})<br>"
    return HttpResponse(response)

from django.http import HttpResponse
from django.db import connection

@login_required
def verificar_relaciones(request):
    proyecto_nombre = 'Rescate animales'  # Cambia esto según el nombre del proyecto que quieras verificar
    query = """
        SELECT user.username
        FROM myapp_proyecto_colaboradores AS pc
        JOIN auth_user AS user ON pc.user_id = user.id
        JOIN myapp_proyecto AS proyecto ON pc.proyecto_id = proyecto.id
        WHERE proyecto.nombre = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [proyecto_nombre])
        rows = cursor.fetchall()

    response = f"Colaboradores del proyecto '{proyecto_nombre}':<br>"
    for row in rows:
        response += f"- {row[0]}<br>"

    return HttpResponse(response)

from django.shortcuts import redirect, get_object_or_404
from .models import Chat, User
def iniciar_chat(request, user_id):
    receptor = get_object_or_404(User, pk=user_id)
    
    # Verifica si ya existe un chat entre estos dos usuarios
    chat = Chat.objects.filter(participantes__in=[request.user, receptor]).distinct()

    if not chat.exists():
        # Si no existe un chat, lo crea
        chat = Chat.objects.create()
        chat.participantes.add(request.user, receptor)
        chat.save()

    # Redirige a la vista listar_mensajes con el usuario_id del receptor
    return redirect(f"{reverse('listar_mensajes')}?usuario_id={receptor.id}")