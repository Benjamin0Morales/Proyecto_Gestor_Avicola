"""
Serializers for all models in the Avícola Eugenio API.
"""

from rest_framework import serializers
from core.models import (
    User, FarmStatus, EggProduction, MortalityEvent,
    FeedItem, FeedMix, FeedMixItem, FeedConsumption,
    FinanceCategory, FinanceTransaction, FinanceSummary,
    ReportExport, VEggProductionDaily
)
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'rol', 'is_active',
            'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']


class FarmStatusSerializer(serializers.ModelSerializer):
    """Serializer for FarmStatus model."""
    
    total_birds = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = FarmStatus
        fields = [
            'id', 'status_date', 'juveniles_count', 'males_count',
            'hens_count', 'total_birds', 'created_at',
            'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'total_birds', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Excluir total_birds del insert (es columna generada)
        validated_data.pop('total_birds', None)
        return super().create(validated_data)
    
    def validate_status_date(self, value):
        """Ensure status_date is unique."""
        if self.instance is None:  # Creating new record
            if FarmStatus.objects.filter(status_date=value).exists():
                raise serializers.ValidationError(
                    f"Farm status for {value} already exists."
                )
        return value


class EggProductionSerializer(serializers.ModelSerializer):
    """Serializer for EggProduction model."""
    
    class Meta:
        model = EggProduction
        fields = [
            'id', 'production_date', 'size_code', 'quantity',
            'source_method', 'is_validated', 'validated_at',
            'validated_by', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate unique constraint on production_date and size_code."""
        production_date = data.get('production_date')
        size_code = data.get('size_code')
        
        if self.instance is None:  # Creating new record
            if EggProduction.objects.filter(
                production_date=production_date,
                size_code=size_code
            ).exists():
                raise serializers.ValidationError(
                    f"Egg production for {production_date} with size {size_code} already exists."
                )
        
        return data
    
    def validate_quantity(self, value):
        """Ensure quantity is positive."""
        if value < 0:
            raise serializers.ValidationError("Quantity must be positive.")
        return value


class VEggProductionDailySerializer(serializers.ModelSerializer):
    """Serializer for daily egg production view."""
    
    class Meta:
        model = VEggProductionDaily
        fields = [
            'production_date', 'total_eggs', 'small_count',
            'medium_count', 'large_count'
        ]


class MortalityEventSerializer(serializers.ModelSerializer):
    """Serializer for MortalityEvent model."""
    
    class Meta:
        model = MortalityEvent
        fields = [
            'id', 'event_date', 'bird_type', 'quantity', 'cause',
            'notes', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_quantity(self, value):
        """Ensure quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value


class FeedItemSerializer(serializers.ModelSerializer):
    """Serializer for FeedItem model."""
    
    class Meta:
        model = FeedItem
        fields = [
            'id', 'item_name', 'supplier_name', 'unit_cost_clp',
            'unit_type', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_unit_cost_clp(self, value):
        """Ensure unit cost is positive."""
        if value < 0:
            raise serializers.ValidationError("Unit cost must be positive.")
        return value


class FeedMixItemSerializer(serializers.ModelSerializer):
    """Serializer for FeedMixItem model."""
    
    feed_item_name = serializers.CharField(source='feed_item.item_name', read_only=True)
    
    class Meta:
        model = FeedMixItem
        fields = [
            'id', 'feed_mix', 'feed_item', 'feed_item_name',
            'proportion_pct', 'weight_kg', 'created_at',
            'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_proportion_pct(self, value):
        """Ensure proportion is between 0 and 100."""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Proportion must be between 0 and 100."
            )
        return value


class FeedMixSerializer(serializers.ModelSerializer):
    """Serializer for FeedMix model."""
    
    items = FeedMixItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = FeedMix
        fields = [
            'id', 'mix_date', 'description', 'total_weight_kg',
            'items', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_mix_date(self, value):
        """Ensure mix_date is unique."""
        if self.instance is None:  # Creating new record
            if FeedMix.objects.filter(mix_date=value).exists():
                raise serializers.ValidationError(
                    f"Feed mix for {value} already exists."
                )
        return value
    
    def validate_total_weight_kg(self, value):
        """Ensure total weight is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Total weight must be greater than 0."
            )
        return value


class FeedConsumptionSerializer(serializers.ModelSerializer):
    """Serializer for FeedConsumption model."""
    
    feed_mix_date = serializers.DateField(source='feed_mix.mix_date', read_only=True)
    
    class Meta:
        model = FeedConsumption
        fields = [
            'id', 'consumption_date', 'feed_mix', 'feed_mix_date',
            'total_consumed_kg', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_consumption_date(self, value):
        """Ensure consumption_date is unique."""
        if self.instance is None:  # Creating new record
            if FeedConsumption.objects.filter(consumption_date=value).exists():
                raise serializers.ValidationError(
                    f"Feed consumption for {value} already exists."
                )
        return value
    
    def validate_total_consumed_kg(self, value):
        """Ensure total consumed is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Total consumed must be greater than 0."
            )
        return value


class FinanceCategorySerializer(serializers.ModelSerializer):
    """Serializer for FinanceCategory model."""
    
    class Meta:
        model = FinanceCategory
        fields = [
            'id', 'category_name', 'type', 'description',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FinanceTransactionSerializer(serializers.ModelSerializer):
    """Serializer for FinanceTransaction model."""
    
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)
    
    class Meta:
        model = FinanceTransaction
        fields = [
            'id', 'transaction_date', 'category', 'category_name',
            'category_type', 'amount_clp', 'payment_method',
            'reference_doc', 'description', 'created_at',
            'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_amount_clp(self, value):
        """Ensure amount is non-negative."""
        if value < 0:
            raise serializers.ValidationError(
                "Amount must be non-negative."
            )
        return value


class FinanceSummarySerializer(serializers.ModelSerializer):
    """Serializer for FinanceSummary model."""
    
    class Meta:
        model = FinanceSummary
        fields = [
            'id', 'year_month', 'total_income_clp', 'total_expense_clp',
            'balance_clp', 'generated_at', 'generated_by',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = [
            'id', 'balance_clp', 'generated_at', 'created_at', 'updated_at'
        ]


class ReportExportSerializer(serializers.ModelSerializer):
    """Serializer for ReportExport model."""
    
    class Meta:
        model = ReportExport
        fields = [
            'id', 'report_type', 'period_start', 'period_end',
            'file_format', 'file_path', 'file_size_bytes',
            'deleted_at', 'deleted_by', 'created_at', 'updated_at',
            'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_file_format(self, value):
        """Ensure file format is valid."""
        valid_formats = ['pdf', 'xlsx', 'csv', 'png']
        if value not in valid_formats:
            raise serializers.ValidationError(
                f"File format must be one of: {', '.join(valid_formats)}"
            )
        return value
    
    def validate(self, data):
        """Validate period dates."""
        period_start = data.get('period_start')
        period_end = data.get('period_end')
        
        if period_start and period_end:
            if period_start > period_end:
                raise serializers.ValidationError(
                    "Period start must be before period end."
                )
        
        return data


class LoginSerializer(serializers.Serializer):
    """Serializer for login requests."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token responses."""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
