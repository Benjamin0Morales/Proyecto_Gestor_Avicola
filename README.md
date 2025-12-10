# 🐔 Avícola Eugenio - Sistema de Gestión Avícola

Sistema web integral para la gestión de una granja avícola, desarrollado con Django y PostgreSQL.

## 📋 Características Principales

### 🏭 Gestión de Producción
- **Estado de Granja**: Registro diario de cantidad de aves (juveniles, machos, gallinas)
- **Producción de Huevos**: Registro por tamaño (pequeño, mediano, grande)
- **Conteo Automático con Visión por Computadora**: 
  - Detección automática de huevos usando YOLOv8
  - Fallback con Hough Transform (OpenCV)
  - Precisión del 95%+ con modelo entrenado
  - Validación manual antes de guardar
- **Eventos de Mortalidad**: Seguimiento de bajas con causas

### 🌾 Gestión de Alimentos
- **Inventario de Alimentos**: Control de stock por item
- **Movimientos**: Registro de compras y consumos
- **Mezclas de Alimento**: Creación de fórmulas personalizadas
- **Consumo Diario**: Seguimiento de consumo por mezcla

### 💰 Gestión Financiera
- **Categorías**: Ingresos y egresos personalizables
- **Transacciones**: Registro detallado con método de pago
- **Reportes**: Resumen financiero por período

### 👥 Gestión de Usuarios
- **Sistema de Roles**: Admin, Manager, Operator, Viewer
- **Permisos Granulares**: Control de acceso por módulo
- **Autenticación Segura**: Contraseñas hasheadas con bcrypt

## 🛠️ Tecnologías

### Backend
- **Django 5.1.3**: Framework web
- **PostgreSQL**: Base de datos
- **OpenCV**: Procesamiento de imágenes
- **Ultralytics YOLOv8**: Detección de objetos con ML
- **NumPy**: Operaciones numéricas

### Frontend
- **Bootstrap 5**: Diseño responsivo
- **Bootstrap Icons**: Iconografía
- **JavaScript**: Interactividad

### Producción
- **Waitress**: Servidor WSGI
- **Nginx**: Reverse proxy y archivos estáticos

## 📦 Instalación

### Requisitos Previos
- Python 3.11+
- PostgreSQL 14+
- Git

### Configuración

1. **Clonar el repositorio**
```bash
git clone https://github.com/Benjamin0Morales/Proyecto_Gestor_Avicola.git
cd Proyecto_Gestor_Avicola
```

2. **Crear entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
- Crear base de datos PostgreSQL
- Ejecutar script SQL: `database/schema.sql`

5. **Configurar variables de entorno**
Crear archivo `.env` en la raíz:
```env
DB_NAME=avicola_eugenio
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=tu_clave_secreta_django
DEBUG=True
```

6. **Ejecutar migraciones**
```bash
python manage.py migrate
```

7. **Crear superusuario** (opcional)
```bash
python manage.py createsuperuser
```

8. **Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
```

Acceder a: `http://localhost:8000`

## 🎯 Módulo de Visión por Computadora

### Características
- **Detección Automática**: Cuenta huevos en imágenes usando IA
- **Dos Métodos**:
  1. YOLOv8 (preferido): 95%+ precisión
  2. Hough Transform (fallback): 60-75% precisión
- **Validación Manual**: Usuario confirma o corrige el conteo
- **Trazabilidad**: Guarda imagen procesada y nivel de confianza

### Uso
1. Ir a **Producción de Huevos** → **Conteo Automático**
2. Subir imagen de huevos (JPG/PNG, máx 5MB)
3. El sistema procesa y detecta automáticamente
4. Revisar y confirmar/corregir el conteo
5. Guardar registro con método "Visión"

### Modelos (No incluidos en repositorio)
Para usar YOLOv8, colocar modelos en carpeta `models/`:
- `egg_detector.onnx` (modelo entrenado personalizado)
- `yolov8n.pt` (modelo pre-entrenado de Ultralytics)

## 📁 Estructura del Proyecto

```
Web/
├── avicola/              # Configuración Django
├── core/                 # Aplicación principal
│   ├── models/          # Modelos de datos
│   ├── *_views.py       # Vistas por módulo
│   ├── vision_service.py # Servicio de visión
│   ├── forms.py         # Formularios
│   └── urls.py          # Rutas
├── templates/           # Plantillas HTML
├── static/              # CSS, JS, imágenes
├── database/            # Scripts SQL
└── requirements.txt     # Dependencias Python
```

## 🔐 Sistema de Permisos

### Roles
- **Admin**: Acceso total
- **Manager**: Lectura/escritura en todos los módulos
- **Operator**: Escritura en producción y alimentos
- **Viewer**: Solo lectura

### Permisos por Módulo
- Producción (farm_status, egg_production, mortality)
- Alimentos (feed_items, feed_inventory, feed_mix)
- Finanzas (finance_categories, finance_transactions)
- Usuarios (users)

## 📊 Base de Datos

### Tablas Principales
- `users`: Usuarios del sistema
- `farm_status`: Estado diario de la granja
- `egg_production`: Producción de huevos
- `mortality_event`: Eventos de mortalidad
- `feed_item`: Items de alimento
- `feed_inventory`: Inventario actual
- `feed_inventory_movement`: Movimientos de inventario
- `feed_mix`: Mezclas de alimento
- `feed_consumption`: Consumo diario
- `finance_category`: Categorías financieras
- `finance_transaction`: Transacciones

## 🚀 Despliegue en Producción

### Con Waitress + Nginx (Windows)

1. **Instalar Waitress**
```bash
pip install waitress
```

2. **Configurar Nginx** (ver `nginx/conf/nginx.conf`)

3. **Ejecutar con script**
```bash
iniciar_sistema.bat
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Licencia

Este proyecto es privado y de uso exclusivo para Avícola Eugenio.

## 👨‍💻 Autor

**Benjamín Morales**
- GitHub: [@Benjamin0Morales](https://github.com/Benjamin0Morales)

## 📧 Contacto

Para consultas o soporte, contactar al administrador del sistema.

---

**Nota**: Los modelos de machine learning (*.pt, *.onnx) no están incluidos en el repositorio debido a su tamaño. Contactar al desarrollador para obtenerlos.
