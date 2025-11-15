"""
Django forms for web interface.
"""
from django import forms
from core.models import (
    User, FarmStatus, EggProduction, MortalityEvent,
    FeedItem, FeedInventory, FeedInventoryMovement, FeedMix, FeedMixItem, FeedConsumption,
    FinanceCategory, FinanceTransaction
)


class UserForm(forms.ModelForm):
    """Form for User model."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña',
        required=True
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        label='Confirmar Contraseña',
        required=True
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'rol', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'email': 'Correo Electrónico',
            'full_name': 'Nombre Completo',
            'rol': 'Rol',
            'is_active': 'Activo',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            from core.auth_utils import hash_password
            user.password_hash = hash_password(password)
        
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing User (without password)."""
    
    change_password = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Cambiar contraseña'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        }),
        label='Nueva Contraseña',
        required=False
    )
    
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label='Confirmar Nueva Contraseña',
        required=False
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'rol', 'is_active']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'email': 'Correo Electrónico',
            'full_name': 'Nombre Completo',
            'rol': 'Rol',
            'is_active': 'Activo',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        change_password = cleaned_data.get('change_password')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if change_password:
            if not password:
                raise forms.ValidationError('Debe ingresar una nueva contraseña')
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        change_password = self.cleaned_data.get('change_password')
        password = self.cleaned_data.get('password')
        
        if change_password and password:
            from core.auth_utils import hash_password
            user.password_hash = hash_password(password)
        
        if commit:
            user.save()
        return user


class FarmStatusForm(forms.ModelForm):
    """Form for FarmStatus model."""
    
    class Meta:
        model = FarmStatus
        fields = ['status_date', 'juveniles_count', 'males_count', 'hens_count']
        widgets = {
            'status_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'juveniles_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'males_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'hens_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
        labels = {
            'status_date': 'Fecha',
            'juveniles_count': 'Juveniles',
            'males_count': 'Machos',
            'hens_count': 'Gallinas',
        }


class EggProductionForm(forms.ModelForm):
    """Form for EggProduction model."""
    
    class Meta:
        model = EggProduction
        fields = ['production_date', 'size_code', 'quantity', 'source_method', 'is_validated']
        widgets = {
            'production_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'size_code': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'source_method': forms.Select(attrs={'class': 'form-select'}),
            'is_validated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'production_date': 'Fecha de Producción',
            'size_code': 'Tamaño',
            'quantity': 'Cantidad',
            'source_method': 'Método de Origen',
            'is_validated': 'Validado',
        }


class MortalityEventForm(forms.ModelForm):
    """Form for MortalityEvent model."""
    
    class Meta:
        model = MortalityEvent
        fields = ['event_date', 'bird_type', 'quantity', 'cause', 'notes']
        widgets = {
            'event_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'bird_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'cause': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '150'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'event_date': 'Fecha del Evento',
            'bird_type': 'Tipo de Ave',
            'quantity': 'Cantidad',
            'cause': 'Causa',
            'notes': 'Notas',
        }


class FeedItemForm(forms.ModelForm):
    """Form for FeedItem model."""
    
    class Meta:
        model = FeedItem
        fields = ['item_name', 'supplier_name', 'unit_cost_clp', 'unit_type']
        widgets = {
            'item_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
            'unit_cost_clp': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'unit_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'item_name': 'Nombre del Item',
            'supplier_name': 'Proveedor',
            'unit_cost_clp': 'Costo Unitario (CLP)',
            'unit_type': 'Unidad de Medida',
        }


class FeedInventoryMovementForm(forms.ModelForm):
    """Form for FeedInventoryMovement model - Registro de compras y movimientos."""
    
    class Meta:
        model = FeedInventoryMovement
        fields = ['feed_item', 'movement_type', 'quantity', 'movement_date', 'reference', 'notes', 'unit_cost_clp']
        widgets = {
            'feed_item': forms.Select(attrs={
                'class': 'form-select'
            }),
            'movement_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01'
            }),
            'movement_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Factura #123, Boleta #456'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
            'unit_cost_clp': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Solo para compras'
            }),
        }
        labels = {
            'feed_item': 'Item de Alimento',
            'movement_type': 'Tipo de Movimiento',
            'quantity': 'Cantidad',
            'movement_date': 'Fecha',
            'reference': 'Referencia',
            'notes': 'Notas',
            'unit_cost_clp': 'Costo Unitario (CLP)',
        }


class FeedMixForm(forms.ModelForm):
    """Form for FeedMix model."""
    
    class Meta:
        model = FeedMix
        fields = ['mix_date', 'description', 'total_weight_kg']
        widgets = {
            'mix_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '200'
            }),
            'total_weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
        }
        labels = {
            'mix_date': 'Fecha de Mezcla',
            'description': 'Descripción',
            'total_weight_kg': 'Peso Total (kg)',
        }


class FeedConsumptionForm(forms.ModelForm):
    """Form for FeedConsumption model."""
    
    class Meta:
        model = FeedConsumption
        fields = ['consumption_date', 'feed_mix', 'total_consumed_kg']
        widgets = {
            'consumption_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'feed_mix': forms.Select(attrs={'class': 'form-select'}),
            'total_consumed_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
        }
        labels = {
            'consumption_date': 'Fecha de Consumo',
            'feed_mix': 'Mezcla de Alimento',
            'total_consumed_kg': 'Total Consumido (kg)',
        }


class FinanceCategoryForm(forms.ModelForm):
    """Form for FinanceCategory model."""
    
    class Meta:
        model = FinanceCategory
        fields = ['category_name', 'type', 'description']
        widgets = {
            'category_name': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'category_name': 'Nombre de Categoría',
            'type': 'Tipo',
            'description': 'Descripción',
        }


class FinanceTransactionForm(forms.ModelForm):
    """Form for FinanceTransaction model."""
    
    # Opciones de métodos de pago
    PAYMENT_METHOD_CHOICES = [
        ('', '--- Seleccionar ---'),
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
        ('Tarjeta Débito', 'Tarjeta Débito'),
        ('Tarjeta Crédito', 'Tarjeta Crédito'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Método de Pago'
    )
    
    class Meta:
        model = FinanceTransaction
        fields = [
            'transaction_date', 'category', 'description',
            'amount_clp', 'payment_method', 'reference_doc'
        ]
        widgets = {
            'transaction_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'amount_clp': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'reference_doc': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100'
            }),
        }
        labels = {
            'transaction_date': 'Fecha',
            'category': 'Categoría',
            'description': 'Descripción',
            'amount_clp': 'Monto (CLP)',
            'reference_doc': 'Documento de Referencia',
        }
