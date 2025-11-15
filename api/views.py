"""
API REST - Endpoints para acceso externo al sistema.
Todos los endpoints requieren autenticación JWT excepto login.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
from drf_spectacular.utils import extend_schema, OpenApiResponse

from core.models import (
    User, FarmStatus, EggProduction, MortalityEvent,
    FeedItem, FeedMix, FeedMixItem, FeedConsumption,
    FinanceCategory, FinanceTransaction, FinanceSummary,
    ReportExport, VEggProductionDaily
)
from core.auth_utils import verify_password
from api.serializers import (
    UserSerializer, FarmStatusSerializer, EggProductionSerializer,
    MortalityEventSerializer, FeedItemSerializer, FeedMixSerializer,
    FeedMixItemSerializer, FeedConsumptionSerializer,
    FinanceCategorySerializer, FinanceTransactionSerializer,
    FinanceSummarySerializer, ReportExportSerializer,
    VEggProductionDailySerializer, LoginSerializer, TokenResponseSerializer
)
from api.permissions import (
    ProductionPermission, FinancePermission, ReportPermission
)


@extend_schema(
    request=LoginSerializer,
    responses={
        200: TokenResponseSerializer,
        401: OpenApiResponse(description='Invalid credentials'),
    },
    description='Login endpoint that returns JWT tokens. Provide email and password to receive access and refresh tokens.',
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint that returns JWT tokens.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate tokens
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['email'] = user.email
    refresh['rol'] = user.rol
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


class FarmStatusViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FarmStatus model.
    Provides CRUD operations for farm status records.
    """
    queryset = FarmStatus.objects.filter(is_active=True)
    serializer_class = FarmStatusSerializer
    permission_classes = [ProductionPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['status_date', 'created_at']
    ordering = ['-status_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(status_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(status_date__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class EggProductionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for EggProduction model.
    Provides CRUD operations for egg production records.
    """
    queryset = EggProduction.objects.filter(is_active=True)
    serializer_class = EggProductionSerializer
    permission_classes = [ProductionPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['production_date', 'size_code', 'created_at']
    ordering = ['-production_date', 'size_code']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        size_code = self.request.query_params.get('size_code')
        is_validated = self.request.query_params.get('is_validated')
        
        if date_from:
            queryset = queryset.filter(production_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(production_date__lte=date_to)
        if size_code:
            queryset = queryset.filter(size_code=size_code)
        if is_validated is not None:
            queryset = queryset.filter(is_validated=is_validated.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def daily(self, request):
        """
        Get daily egg production summary from view.
        """
        queryset = VEggProductionDaily.objects.all()
        
        # Filter by date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(production_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(production_date__lte=date_to)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = VEggProductionDailySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = VEggProductionDailySerializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class MortalityEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MortalityEvent model.
    Provides CRUD operations for mortality event records.
    """
    queryset = MortalityEvent.objects.filter(is_active=True)
    serializer_class = MortalityEventSerializer
    permission_classes = [ProductionPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['event_date', 'bird_type', 'created_at']
    ordering = ['-event_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range and bird type
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        bird_type = self.request.query_params.get('bird_type')
        
        if date_from:
            queryset = queryset.filter(event_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(event_date__lte=date_to)
        if bird_type:
            queryset = queryset.filter(bird_type=bird_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FeedItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FeedItem model.
    Provides CRUD operations for feed item records.
    """
    queryset = FeedItem.objects.filter(is_active=True)
    serializer_class = FeedItemSerializer
    permission_classes = [ProductionPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['item_name', 'supplier_name']
    ordering_fields = ['item_name', 'unit_cost_clp', 'created_at']
    ordering = ['item_name']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FeedMixViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FeedMix model.
    Provides CRUD operations for feed mix records.
    """
    queryset = FeedMix.objects.filter(is_active=True)
    serializer_class = FeedMixSerializer
    permission_classes = [ProductionPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['mix_date', 'created_at']
    ordering = ['-mix_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(mix_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(mix_date__lte=date_to)
        
        return queryset
    
    @action(detail=True, methods=['get', 'post'])
    def items(self, request, pk=None):
        """
        Get or add items to a feed mix.
        """
        feed_mix = self.get_object()
        
        if request.method == 'GET':
            items = FeedMixItem.objects.filter(feed_mix=feed_mix, is_active=True)
            serializer = FeedMixItemSerializer(items, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = FeedMixItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Validate total proportion doesn't exceed 100%
            current_total = FeedMixItem.objects.filter(
                feed_mix=feed_mix,
                is_active=True
            ).aggregate(total=Sum('proportion_pct'))['total'] or Decimal('0')
            
            new_proportion = serializer.validated_data['proportion_pct']
            
            if current_total + new_proportion > 100:
                return Response(
                    {'detail': f'Total proportion would exceed 100% (current: {current_total}%)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save(
                feed_mix=feed_mix,
                created_by=request.user.id
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FeedMixItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FeedMixItem model.
    Provides CRUD operations for feed mix item records.
    """
    queryset = FeedMixItem.objects.filter(is_active=True)
    serializer_class = FeedMixItemSerializer
    permission_classes = [ProductionPermission]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FeedConsumptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FeedConsumption model.
    Provides CRUD operations for feed consumption records.
    """
    queryset = FeedConsumption.objects.filter(is_active=True)
    serializer_class = FeedConsumptionSerializer
    permission_classes = [ProductionPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['consumption_date', 'created_at']
    ordering = ['-consumption_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(consumption_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(consumption_date__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FinanceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FinanceCategory model.
    Provides CRUD operations for finance category records.
    """
    queryset = FinanceCategory.objects.filter(is_active=True)
    serializer_class = FinanceCategorySerializer
    permission_classes = [FinancePermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name']
    ordering_fields = ['category_name', 'type', 'created_at']
    ordering = ['type', 'category_name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by type
        category_type = self.request.query_params.get('type')
        if category_type:
            queryset = queryset.filter(type=category_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FinanceTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FinanceTransaction model.
    Provides CRUD operations for finance transaction records.
    """
    queryset = FinanceTransaction.objects.filter(is_active=True)
    serializer_class = FinanceTransactionSerializer
    permission_classes = [FinancePermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['transaction_date', 'amount_clp', 'created_at']
    ordering = ['-transaction_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range, category, and type
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        category_id = self.request.query_params.get('category_id')
        category_type = self.request.query_params.get('category_type')
        
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if category_type:
            queryset = queryset.filter(category__type=category_type)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)


class FinanceSummaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for FinanceSummary model.
    Provides CRUD operations for finance summary records.
    """
    queryset = FinanceSummary.objects.filter(is_active=True)
    serializer_class = FinanceSummarySerializer
    permission_classes = [FinancePermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['year_month', 'created_at']
    ordering = ['-year_month']
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate or update finance summary for a specific month.
        """
        year_month = request.data.get('year_month')
        
        if not year_month:
            return Response(
                {'detail': 'year_month is required (format: YYYY-MM)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate format
        try:
            datetime.strptime(year_month, '%Y-%m')
        except ValueError:
            return Response(
                {'detail': 'Invalid year_month format. Use YYYY-MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate totals for the month
        year, month = year_month.split('-')
        transactions = FinanceTransaction.objects.filter(
            transaction_date__year=year,
            transaction_date__month=month,
            is_active=True
        )
        
        income = transactions.filter(
            category__type='income'
        ).aggregate(total=Sum('amount_clp'))['total'] or Decimal('0')
        
        expense = transactions.filter(
            category__type='expense'
        ).aggregate(total=Sum('amount_clp'))['total'] or Decimal('0')
        
        # Create or update summary
        summary, created = FinanceSummary.objects.update_or_create(
            year_month=year_month,
            defaults={
                'total_income_clp': income,
                'total_expense_clp': expense,
                'generated_by': request.user.id,
                'updated_by': request.user.id,
            }
        )
        
        serializer = FinanceSummarySerializer(summary)
        return Response(
            {
                'message': 'Summary generated successfully',
                'created': created,
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class ReportExportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ReportExport model.
    Provides CRUD operations for report export records.
    """
    queryset = ReportExport.objects.filter(is_active=True, deleted_at__isnull=True)
    serializer_class = ReportExportSerializer
    permission_classes = [ReportPermission]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'report_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by report type and format
        report_type = self.request.query_params.get('report_type')
        file_format = self.request.query_params.get('file_format')
        
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if file_format:
            queryset = queryset.filter(file_format=file_format)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user.id)
    
    def perform_destroy(self, instance):
        """Soft delete by setting deleted_at and deleted_by."""
        instance.deleted_at = timezone.now()
        instance.deleted_by = self.request.user.id
        instance.is_active = False
        instance.save(update_fields=['deleted_at', 'deleted_by', 'is_active'])
