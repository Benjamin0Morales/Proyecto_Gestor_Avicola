"""
Modelos de datos - Representan las tablas de la base de datos PostgreSQL.
Todos los modelos tienen managed=False para no modificar la BD existente.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Manejador personalizado para crear usuarios."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crear usuario normal."""
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            from core.auth_utils import hash_password
            user.password_hash = hash_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Crear usuario administrador."""
        extra_fields.setdefault('rol', 'admin')
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de Usuario - Tabla 'users' en la base de datos."""
    
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('worker', 'Trabajador'),
        ('accountant', 'Contador'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    password_hash = models.TextField()
    full_name = models.CharField(max_length=255)
    rol = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True, db_column='last_login_at')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    # Required for Django's auth system
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    objects = UserManager()
    
    class Meta:
        managed = False
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        """Required for Django admin."""
        return self.rol == 'admin'
    
    @property
    def is_superuser(self):
        """Required for Django admin."""
        return self.rol == 'admin'
    
    def has_perm(self, perm, obj=None):
        """Required for Django admin."""
        return self.rol == 'admin'
    
    def has_module_perms(self, app_label):
        """Required for Django admin."""
        return self.rol == 'admin'
    
    # Override password field to use password_hash
    password = property(lambda self: self.password_hash)
    
    def set_password(self, raw_password):
        """Set password using custom hash function."""
        from core.auth_utils import hash_password
        self.password_hash = hash_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password using custom verify function."""
        from core.auth_utils import verify_password
        return verify_password(raw_password, self.password_hash)


class FarmStatus(models.Model):
    """Estado de Granja - Registro diario de cantidad de aves."""
    
    id = models.BigAutoField(primary_key=True)
    status_date = models.DateField(unique=True)
    juveniles_count = models.IntegerField(default=0)
    males_count = models.IntegerField(default=0)
    hens_count = models.IntegerField(default=0)
    total_birds = models.GeneratedField(
        expression=models.F('juveniles_count') + models.F('males_count') + models.F('hens_count'),
        output_field=models.IntegerField(),
        db_persist=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'farm_status'
        ordering = ['-status_date']
    
    def __str__(self):
        return f"Farm Status - {self.status_date}"


class EggProduction(models.Model):
    """Producción de Huevos - Registro diario por tamaño."""
    
    SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]
    
    SOURCE_METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('vision', 'Vision'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    production_date = models.DateField()
    size_code = models.CharField(max_length=10, choices=SIZE_CHOICES)
    quantity = models.IntegerField(default=0)
    source_method = models.CharField(max_length=12, choices=SOURCE_METHOD_CHOICES, default='manual')
    is_validated = models.BooleanField(default=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    validated_by = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'egg_production'
        ordering = ['-production_date', 'size_code']
        unique_together = [['production_date', 'size_code']]
    
    def __str__(self):
        # Representación en cadena de la producción de huevos
        return f"{self.production_date} - {self.size_code}: {self.quantity}"


class MortalityEvent(models.Model):
    """Eventos de Mortalidad - Registro de muertes de aves."""
    
    BIRD_TYPE_CHOICES = [
        ('juvenile', 'Juvenile'),
        ('male', 'Male'),
        ('hen', 'Hen'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    event_date = models.DateField()
    bird_type = models.CharField(max_length=15, choices=BIRD_TYPE_CHOICES)
    quantity = models.IntegerField()
    cause = models.CharField(max_length=150)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'mortality_event'
        ordering = ['-event_date']
    
    def __str__(self):
        # Representación en cadena del evento de mortalidad
        return f"{self.event_date} - {self.bird_type}: {self.quantity}"


class FeedItem(models.Model):
    """Items de Alimento - Catálogo de ingredientes."""
    
    # Opciones de unidades de medida usadas en Chile
    UNIT_CHOICES = [
        ('kg', 'Kilogramo (kg)'),
        ('g', 'Gramo (g)'),
        ('ton', 'Tonelada (ton)'),
        ('lt', 'Litro (lt)'),
        ('ml', 'Mililitro (ml)'),
        ('saco', 'Saco (25 kg)'),
        ('unidad', 'Unidad'),
        ('caja', 'Caja'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    item_name = models.CharField(max_length=100)
    supplier_name = models.CharField(max_length=100, blank=True, null=True)
    unit_cost_clp = models.DecimalField(max_digits=12, decimal_places=2)
    unit_type = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'feed_item'
        ordering = ['item_name']
    
    def __str__(self):
        # Representación en cadena del item de alimento
        return self.item_name


class FeedInventory(models.Model):
    """Inventario de Alimentos - Stock actual de cada item."""
    
    id = models.BigAutoField(primary_key=True)
    feed_item = models.OneToOneField(FeedItem, on_delete=models.PROTECT, related_name='inventory')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_type = models.CharField(max_length=20)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'feed_inventory'
        ordering = ['feed_item__item_name']
    
    def __str__(self):
        return f"{self.feed_item.item_name}: {self.quantity} {self.unit_type}"


class FeedInventoryMovement(models.Model):
    """Movimientos de Inventario - Historial de entradas y salidas."""
    
    MOVEMENT_TYPES = [
        ('purchase', 'Compra'),
        ('usage', 'Uso/Consumo'),
        ('waste', 'Desperdicio'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    feed_item = models.ForeignKey(FeedItem, on_delete=models.PROTECT, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type = models.CharField(max_length=20)
    movement_date = models.DateField()
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    unit_cost_clp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'feed_inventory_movement'
        ordering = ['-movement_date', '-created_at']
    
    def __str__(self):
        sign = '+' if self.quantity > 0 else ''
        return f"{self.feed_item.item_name}: {sign}{self.quantity} {self.unit_type} ({self.get_movement_type_display()})"


class FeedMix(models.Model):
    """Mezclas de Alimento - Preparaciones de alimento."""
    
    id = models.BigAutoField(primary_key=True)
    mix_date = models.DateField()
    description = models.CharField(max_length=200, blank=True, null=True)
    total_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'feed_mix'
        ordering = ['-mix_date']
    
    def __str__(self):
        # Representación en cadena de la mezcla de alimento
        return f"Mix - {self.mix_date}"


class FeedMixItem(models.Model):
    """Items de Mezcla de Alimento - Detalle de las mezclas."""
    
    id = models.BigAutoField(primary_key=True)
    feed_mix = models.ForeignKey(FeedMix, on_delete=models.CASCADE, db_column='feed_mix_id')
    feed_item = models.ForeignKey(FeedItem, on_delete=models.PROTECT, db_column='feed_item_id')
    proportion_pct = models.DecimalField(max_digits=5, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'feed_mix_item'
        ordering = ['feed_mix', '-proportion_pct']
    
    def __str__(self):
        # Representación en cadena del item de la mezcla de alimento
        return f"{self.feed_mix} - {self.feed_item}: {self.proportion_pct}%"


class FeedConsumption(models.Model):
    """Consumo de Alimento - Registro diario de consumo."""
    
    id = models.BigAutoField(primary_key=True)
    consumption_date = models.DateField(unique=True)
    feed_mix = models.ForeignKey(FeedMix, on_delete=models.SET_NULL, null=True, blank=True, db_column='feed_mix_id')
    total_consumed_kg = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        managed = False
        db_table = 'feed_consumption'
        ordering = ['-consumption_date']
    
    def __str__(self):
        # Representación en cadena del consumo de alimento
        return f"{self.consumption_date}: {self.total_consumed_kg} kg"


class FinanceCategory(models.Model):
    """Categorías Financieras - Tipos de ingresos/gastos."""
    
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'finance_category'
        ordering = ['type', 'category_name']
    
    def __str__(self):
        # Representación en cadena de la categoría financiera
        return f"{self.category_name} ({self.type})"


class FinanceTransaction(models.Model):
    """Transacciones Financieras - Ingresos y gastos."""
    
    id = models.BigAutoField(primary_key=True)
    transaction_date = models.DateField()
    category = models.ForeignKey(FinanceCategory, on_delete=models.CASCADE)
    amount_clp = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    reference_doc = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'finance_transaction'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_date} - {self.category}: ${self.amount_clp}"


class FinanceSummary(models.Model):
    """Finance summary model mapped to 'finance_summary' table."""
    
    id = models.BigAutoField(primary_key=True)
    year_month = models.CharField(max_length=7, unique=True)  # Format: YYYY-MM
    total_income_clp = models.DecimalField(max_digits=15, decimal_places=2)
    total_expense_clp = models.DecimalField(max_digits=15, decimal_places=2)
    balance_clp = models.DecimalField(max_digits=15, decimal_places=2)  # Generated column in DB
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'finance_summary'
        ordering = ['-year_month']
    
    def __str__(self):
        return f"Summary {self.year_month}"


class ReportExport(models.Model):
    """Report export model mapped to 'report_export' table."""
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('xlsx', 'Excel'),
        ('csv', 'CSV'),
        ('png', 'PNG'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    report_type = models.CharField(max_length=100)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    file_format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        managed = False
        db_table = 'report_export'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_type} - {self.file_format}"


class VEggProductionDaily(models.Model):
    """View for daily egg production aggregation."""
    
    production_date = models.DateField(primary_key=True)
    total_eggs = models.IntegerField()
    small_count = models.IntegerField()
    medium_count = models.IntegerField()
    large_count = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'v_egg_production_daily'
        ordering = ['-production_date']
    
    def __str__(self):
        return f"{self.production_date}: {self.total_eggs} eggs"
