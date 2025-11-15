"""
Vistas del módulo de Finanzas - Categorías y Transacciones Financieras.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from core.models import FinanceCategory, FinanceTransaction
from core.forms import FinanceCategoryForm, FinanceTransactionForm
from core.decorators import finance_write_required


# ============================================================================
# CATEGORÍAS FINANCIERAS
# ============================================================================

@login_required
def finance_category_list(request):
    """Muestra la lista de categorías financieras."""
    categories = FinanceCategory.objects.filter(is_active=True).order_by('type', 'category_name')
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'finance/category_list.html', {'categories': page_obj})


@login_required
@finance_write_required
def finance_category_create(request):
    """Crear categoría financiera."""
    if request.method == 'POST':
        form = FinanceCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user.id
            category.save()
            messages.success(request, 'Categoría financiera creada exitosamente')
            return redirect('finance_category_list')
    else:
        form = FinanceCategoryForm()
    
    context = {
        'form': form,
        'title': 'Nueva Categoría Financiera',
        'cancel_url': 'finance_category_list',
        'icon': 'bi-tags'
    }
    return render(request, 'finance/category_form.html', context)


@login_required
@finance_write_required
def finance_category_edit(request, pk):
    """Editar categoría financiera."""
    category = get_object_or_404(FinanceCategory, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = FinanceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.updated_by = request.user.id
            category.save()
            messages.success(request, 'Categoría financiera actualizada exitosamente')
            return redirect('finance_category_list')
    else:
        form = FinanceCategoryForm(instance=category)
    
    context = {
        'form': form,
        'title': 'Editar Categoría Financiera',
        'cancel_url': 'finance_category_list',
        'icon': 'bi-tags'
    }
    return render(request, 'finance/category_form.html', context)


@login_required
@finance_write_required
def finance_category_delete(request, pk):
    """Eliminar categoría financiera (soft delete)."""
    category = get_object_or_404(FinanceCategory, pk=pk, is_active=True)
    category.is_active = False
    category.updated_by = request.user.id
    category.save()
    messages.success(request, 'Categoría financiera eliminada exitosamente')
    return redirect('finance_category_list')


# ============================================================================
# TRANSACCIONES FINANCIERAS
# ============================================================================

@login_required
def finance_transaction_list(request):
    """Muestra la lista de transacciones financieras."""
    transactions = FinanceTransaction.objects.filter(
        is_active=True
    ).select_related('category').order_by('-transaction_date', '-created_at')
    
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'finance/transaction_list.html', {'transactions': page_obj})


@login_required
@finance_write_required
def finance_transaction_create(request):
    """Crear transacción financiera."""
    if request.method == 'POST':
        form = FinanceTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user.id
            transaction.save()
            messages.success(request, 'Transacción financiera creada exitosamente')
            return redirect('finance_transaction_list')
    else:
        form = FinanceTransactionForm()
    
    context = {
        'form': form,
        'title': 'Nueva Transacción Financiera',
        'cancel_url': 'finance_transaction_list',
        'icon': 'bi-cash-stack'
    }
    return render(request, 'finance/transaction_form.html', context)


@login_required
@finance_write_required
def finance_transaction_edit(request, pk):
    """Editar transacción financiera."""
    transaction = get_object_or_404(FinanceTransaction, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = FinanceTransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.updated_by = request.user.id
            transaction.save()
            messages.success(request, 'Transacción financiera actualizada exitosamente')
            return redirect('finance_transaction_list')
    else:
        form = FinanceTransactionForm(instance=transaction)
    
    context = {
        'form': form,
        'title': 'Editar Transacción Financiera',
        'cancel_url': 'finance_transaction_list',
        'icon': 'bi-cash-stack'
    }
    return render(request, 'finance/transaction_form.html', context)


@login_required
@finance_write_required
def finance_transaction_delete(request, pk):
    """Eliminar transacción financiera (soft delete)."""
    transaction = get_object_or_404(FinanceTransaction, pk=pk, is_active=True)
    transaction.is_active = False
    transaction.updated_by = request.user.id
    transaction.save()
    messages.success(request, 'Transacción financiera eliminada exitosamente')
    return redirect('finance_transaction_list')
