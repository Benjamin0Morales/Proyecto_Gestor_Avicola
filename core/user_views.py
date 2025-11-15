"""
Gestión de Usuarios - Solo accesible para administradores.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from core.models import User
from core.forms import UserForm, UserEditForm
from core.decorators import admin_required


@admin_required
def user_list(request):
    """Muestra la lista de todos los usuarios del sistema."""
    # Obtener todos los usuarios (activos e inactivos)
    users = User.objects.all().order_by('-created_at')
    
    # Paginar resultados
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'users/list.html', {'users': users})


@admin_required
def user_create(request):
    """Crear nuevo usuario en el sistema."""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.created_by = request.user.id
            user.save()
            messages.success(request, f'Usuario {user.full_name} creado exitosamente')
            return redirect('user_list')
    else:
        form = UserForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Usuario',
        'cancel_url': 'user_list',
        'icon': 'bi-person-plus'
    }
    return render(request, 'users/form.html', context)


@admin_required
def user_edit(request, pk):
    """Editar usuario existente."""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.updated_by = request.user.id
            user.save()
            messages.success(request, f'Usuario {user.full_name} actualizado exitosamente')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    
    context = {
        'form': form,
        'title': f'Editar Usuario: {user.full_name}',
        'cancel_url': 'user_list',
        'icon': 'bi-person-gear'
    }
    return render(request, 'users/form.html', context)


@admin_required
def user_delete(request, pk):
    """Desactivar usuario (no se elimina, solo se desactiva)."""
    user = get_object_or_404(User, pk=pk)
    
    if user.id == request.user.id:
        messages.error(request, 'No puedes desactivar tu propio usuario')
        return redirect('user_list')
    
    user.is_active = False
    user.updated_by = request.user.id
    user.save()
    messages.success(request, f'Usuario {user.full_name} desactivado exitosamente')
    return redirect('user_list')


@admin_required
def user_activate(request, pk):
    """Reactivar usuario previamente desactivado."""
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.updated_by = request.user.id
    user.save()
    messages.success(request, f'Usuario {user.full_name} activado exitosamente')
    return redirect('user_list')
