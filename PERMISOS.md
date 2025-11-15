# 🔒 Sistema de Permisos - Avícola Eugenio

## Matriz de Permisos por Rol

| Módulo | Admin | Worker | Accountant |
|--------|-------|--------|------------|
| **Producción** | ✅ Lectura/Escritura | ✅ Lectura/Escritura | 👁️ Solo Lectura |
| **Alimentación** | ✅ Lectura/Escritura | ✅ Lectura/Escritura | 👁️ Solo Lectura |
| **Finanzas** | ✅ Lectura/Escritura | 👁️ Solo Lectura | ✅ Lectura/Escritura |
| **Usuarios** | ✅ Lectura/Escritura | ❌ Sin Acceso | ❌ Sin Acceso |
| **Cambio de Vista** | ✅ Permitido | ❌ No Permitido | ❌ No Permitido |

---

## Archivos del Sistema de Permisos

### 1. `core/decorators.py`
**Archivo centralizado de permisos**

Contiene todos los decoradores de permisos:

```python
# Decoradores disponibles:
@admin_required              # Solo admin (rol real)
@finance_write_required      # Admin + Accountant
@production_write_required   # Admin + Worker
@role_required('admin', ...) # Roles específicos
```

### 2. `core/context_processors.py`
**Variables de permisos en templates**

Variables disponibles en todos los templates:
- `effective_role` - Rol actual (respeta vista temporal)
- `can_write_finance` - Puede modificar finanzas
- `can_write_production` - Puede modificar producción/alimentación
- `is_admin` - Es admin (rol real)

### 3. `avicola/middleware.py`
**Middleware de vista temporal**

- `ViewAsRoleMiddleware` - Permite a admin ver como otros roles

---

## Uso en Vistas

### Proteger vista de escritura en producción:
```python
from core.decorators import production_write_required

@login_required
@production_write_required
def farm_status_create(request):
    # Solo admin y worker pueden acceder
    ...
```

### Proteger vista de escritura en finanzas:
```python
from core.decorators import finance_write_required

@login_required
@finance_write_required
def finance_transaction_create(request):
    # Solo admin y accountant pueden acceder
    ...
```

### Proteger vista de administración:
```python
from core.decorators import admin_required

@admin_required
def user_list(request):
    # Solo admin (rol real) puede acceder
    ...
```

---

## Uso en Templates

### Ocultar botones según permisos:

```django
{% if can_write_production %}
    <a href="{% url 'farm_status_create' %}" class="btn btn-primary">
        Crear
    </a>
{% else %}
    <span class="badge bg-secondary">Solo lectura</span>
{% endif %}
```

### Mostrar/ocultar acciones en tablas:

```django
<td>
    {% if can_write_finance %}
        <a href="{% url 'transaction_edit' transaction.id %}">Editar</a>
        <a href="{% url 'transaction_delete' transaction.id %}">Eliminar</a>
    {% else %}
        <i class="bi bi-lock"></i>
    {% endif %}
</td>
```

---

## Vistas Protegidas

### Producción (Admin + Worker)
- `farm_status_create/edit/delete`
- `egg_production_create/edit/delete`
- `mortality_create/edit/delete`

### Alimentación (Admin + Worker)
- `feed_item_create/edit/delete`
- `feed_mix_create/edit/delete`
- `feed_consumption_create/edit/delete`

### Finanzas (Admin + Accountant)
- `finance_category_create/edit/delete`
- `finance_transaction_create/edit/delete`

### Administración (Solo Admin)
- `user_list/create/edit/delete`
- `switch_view_role`

---

## Cambio de Vista Temporal (Admin)

El admin puede ver el sistema como lo vería otro rol:

1. Click en nombre de usuario (navbar)
2. Seleccionar "Ver como: Worker" o "Ver como: Accountant"
3. El sistema oculta/muestra funciones según el rol seleccionado
4. Para volver: "Ver como: Admin (Normal)"

**Importante:** 
- El rol real NO cambia
- Los permisos críticos (gestión de usuarios) se mantienen bloqueados
- Solo afecta la UI, no los permisos de backend

---

## Flujo de Verificación de Permisos

```
1. Usuario hace request
   ↓
2. ViewAsRoleMiddleware determina rol efectivo
   ↓
3. Decorador verifica permisos
   ↓
4. Si no tiene permisos → Redirect + mensaje error
   ↓
5. Si tiene permisos → Ejecuta vista
   ↓
6. Template usa can_write_* para mostrar/ocultar UI
```

---

## Agregar Nuevos Permisos

### 1. Crear decorador en `core/decorators.py`:
```python
def new_permission_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        effective_role = get_effective_role(request)
        if effective_role not in ['admin', 'role1', 'role2']:
            messages.error(request, 'Sin permisos')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
```

### 2. Aplicar a vistas:
```python
@login_required
@new_permission_required
def my_view(request):
    ...
```

### 3. Agregar variable en `context_processors.py`:
```python
return {
    'can_do_something': role in ['admin', 'role1'],
}
```

### 4. Usar en templates:
```django
{% if can_do_something %}
    <!-- Mostrar funcionalidad -->
{% endif %}
```

---

## Testing de Permisos

### Como Admin:
1. Login como admin
2. Usar "Ver como: Worker"
3. Verificar que NO puedes modificar finanzas
4. Usar "Ver como: Accountant"
5. Verificar que NO puedes modificar producción

### Como Worker:
1. Login como worker
2. Verificar acceso a producción/alimentación
3. Verificar solo lectura en finanzas

### Como Accountant:
1. Login como accountant
2. Verificar acceso a finanzas
3. Verificar solo lectura en producción/alimentación

---

## Seguridad

✅ **Doble capa de protección:**
1. Backend: Decoradores bloquean acceso a vistas
2. Frontend: Templates ocultan botones/enlaces

✅ **Rol efectivo vs rol real:**
- Rol efectivo: Para UI y permisos normales
- Rol real: Para funciones críticas (gestión usuarios)

✅ **Mensajes claros:**
- Usuario sabe por qué no puede acceder
- Redirect apropiado según contexto

---

**Última actualización:** 09/11/2025
