"""
Configuration admin pour l'app Analytics
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Report, ReportTemplate, ReportSchedule,
    AnalyticsDashboard, DashboardWidget,
    AnalyticsMetric, MetricValue,
    DataExport, ExportFormat
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'status', 'generated_by', 'generated_at', 'execution_time']
    list_filter = ['report_type', 'status', 'generated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['generated_at', 'execution_time', 'file_size', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by', 'template')
    
    def execution_time_display(self, obj):
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return "-"
    execution_time_display.short_description = "Temps d'exécution"


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'frequency', 'is_active', 'last_run', 'next_run']
    list_filter = ['frequency', 'is_active', 'last_run']
    search_fields = ['name']
    readonly_fields = ['last_run', 'next_run', 'total_runs', 'successful_runs', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('template', 'created_by')


@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard_type', 'owner', 'is_public', 'view_count', 'created_at']
    list_filter = ['dashboard_type', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['view_count', 'last_updated', 'created_at', 'updated_at']
    filter_horizontal = ['shared_with']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard', 'widget_type', 'chart_type', 'is_visible', 'position_display']
    list_filter = ['widget_type', 'chart_type', 'is_visible']
    search_fields = ['name', 'data_source']
    readonly_fields = ['last_updated', 'created_at', 'updated_at']
    
    def position_display(self, obj):
        return f"({obj.position_x}, {obj.position_y}) {obj.width}x{obj.height}"
    position_display.short_description = "Position"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('dashboard')


@admin.register(AnalyticsMetric)
class AnalyticsMetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'category', 'metric_type', 'is_active', 'last_calculated']
    list_filter = ['category', 'metric_type', 'is_active', 'alert_enabled']
    search_fields = ['name', 'display_name', 'description']
    readonly_fields = ['last_calculated', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(MetricValue)
class MetricValueAdmin(admin.ModelAdmin):
    list_display = ['metric', 'value', 'timestamp', 'source']
    list_filter = ['metric', 'source', 'timestamp']
    search_fields = ['metric__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('metric', 'calculated_by')


@admin.register(ExportFormat)
class ExportFormatAdmin(admin.ModelAdmin):
    list_display = ['name', 'format_type', 'mime_type', 'is_active']
    list_filter = ['format_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'export_format', 'data_source', 'status', 'requested_by', 'processed_at', 'file_size_display']
    list_filter = ['export_format', 'data_source', 'status', 'processed_at']
    search_fields = ['name', 'description']
    readonly_fields = ['file_path', 'file_name', 'file_size', 'download_count', 'processed_at', 'execution_time', 'created_at', 'updated_at']
    
    def file_size_display(self, obj):
        if obj.file_size:
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "-"
    file_size_display.short_description = "Taille du fichier"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('export_format', 'requested_by')

