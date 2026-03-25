from django.contrib import admin
from .models import *

# Register your models here.
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'notes')
    list_filter = ('user', 'category', 'date')

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'amount', 'date', 'notes')
    list_filter = ('user', 'source', 'date')

class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'amount', 'created_at', 'spent')
    list_filter = ('user', 'created_at')
    search_fields = ['user__username', 'name']


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'category', 'date')
    list_filter = ('user', 'type', 'category', 'date')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    list_filter = ('name',)

class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'amount', 'spent', 'percentage_used', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['user__username', 'name']

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'phone_number']

# Register models with admin site
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Income, IncomeAdmin)
admin.site.register(Budget, BudgetAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

