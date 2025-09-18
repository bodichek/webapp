from django.contrib import admin
from .models import FinancialFile, FinancialRow, FinancialAnalysis

@admin.register(FinancialFile)
class FinancialFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'file_type', 'file', 'csv_file', 'uploaded_at')
    list_filter = ('user', 'year', 'file_type')
    search_fields = ('user__username',)

@admin.register(FinancialRow)
class FinancialRowAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'file', 'line', 'description', 'value')
    list_filter = ('user', 'year')
    search_fields = ('user__username', 'line', 'description')

@admin.register(FinancialAnalysis)
class FinancialAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'year', 'file_type', 'key', 'value')
    list_filter = ('user', 'year', 'file_type')
    search_fields = ('user__username', 'key')
