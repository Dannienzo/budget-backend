from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( DashboardView, CategoryViewSet, ExpenseViewSet, IncomeViewSet, BudgetViewSet,TransactionViewSet, AnalyticsViewSet, UserProfileViewSet, export_transactions_csv, export_transactions_excel,
generate_monthly_pdf_report, import_bank_csv, preview_bank_csv, )

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'income', IncomeViewSet, basename='income')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'profile', UserProfileViewSet, basename='profile')




urlpatterns  = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/export/csv/', export_transactions_csv, name='export-csv'),
    path('reports/export/excel/', export_transactions_excel, name='export-excel'),
    path('reports/monthly-pdf/', generate_monthly_pdf_report, name='monthly-pdf'),
    path('reports/import/preview', preview_bank_csv, name='preview_ csv'),
    path('reports/import/upload', import_bank_csv, name='import-csv'),
    path('', include(router.urls)),
]