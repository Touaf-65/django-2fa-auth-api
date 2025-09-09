"""
Tests pour l'app Analytics
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from apps.analytics.models import (
    Report, ReportTemplate, ReportSchedule,
    AnalyticsDashboard, DashboardWidget,
    AnalyticsMetric, MetricValue,
    DataExport, ExportFormat
)
from apps.analytics.services import ReportService, AnalyticsService, ExportService, DashboardService

User = get_user_model()


class AnalyticsModelsTestCase(TestCase):
    """Tests pour les modèles Analytics"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_report_template_creation(self):
        """Test de création d'un template de rapport"""
        template = ReportTemplate.objects.create(
            name='Test Template',
            report_type='user_activity',
            created_by=self.user
        )
        
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.report_type, 'user_activity')
        self.assertTrue(template.is_active)
    
    def test_report_creation(self):
        """Test de création d'un rapport"""
        template = ReportTemplate.objects.create(
            name='Test Template',
            report_type='user_activity',
            created_by=self.user
        )
        
        report = Report.objects.create(
            name='Test Report',
            template=template,
            report_type='user_activity',
            generated_by=self.user
        )
        
        self.assertEqual(report.name, 'Test Report')
        self.assertEqual(report.status, 'pending')
        self.assertEqual(report.generated_by, self.user)
    
    def test_dashboard_creation(self):
        """Test de création d'un tableau de bord"""
        dashboard = AnalyticsDashboard.objects.create(
            name='Test Dashboard',
            dashboard_type='executive',
            owner=self.user
        )
        
        self.assertEqual(dashboard.name, 'Test Dashboard')
        self.assertEqual(dashboard.owner, self.user)
        self.assertFalse(dashboard.is_public)
    
    def test_metric_creation(self):
        """Test de création d'une métrique"""
        metric = AnalyticsMetric.objects.create(
            name='test_metric',
            display_name='Test Metric',
            category='user',
            metric_type='counter'
        )
        
        self.assertEqual(metric.name, 'test_metric')
        self.assertEqual(metric.category, 'user')
        self.assertTrue(metric.is_active)


class AnalyticsServicesTestCase(TestCase):
    """Tests pour les services Analytics"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.analytics_service = AnalyticsService()
    
    def test_metric_calculation(self):
        """Test de calcul de métrique"""
        # Créer une métrique de test
        metric = AnalyticsMetric.objects.create(
            name='total_users',
            display_name='Total Users',
            category='user',
            metric_type='counter'
        )
        
        # Calculer la métrique
        result = self.analytics_service.calculate_metric('total_users')
        
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
    
    def test_metric_trend(self):
        """Test de récupération de tendance de métrique"""
        # Créer une métrique de test
        metric = AnalyticsMetric.objects.create(
            name='test_trend_metric',
            display_name='Test Trend Metric',
            category='user',
            metric_type='counter'
        )
        
        # Récupérer la tendance
        trend = self.analytics_service.get_metric_trend('test_trend_metric', days=7)
        
        self.assertIsInstance(trend, list)
        self.assertEqual(len(trend), 7)  # 7 jours


class AnalyticsAPITestCase(APITestCase):
    """Tests pour les API Analytics"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_report_template_list(self):
        """Test de liste des templates de rapports"""
        ReportTemplate.objects.create(
            name='Test Template',
            report_type='user_activity',
            created_by=self.user
        )
        
        response = self.client.get('/api/analytics/reports/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_dashboard_creation(self):
        """Test de création de tableau de bord"""
        data = {
            'name': 'Test Dashboard',
            'dashboard_type': 'executive',
            'description': 'Test description'
        }
        
        response = self.client.post('/api/analytics/dashboards/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Dashboard')
    
    def test_metric_list(self):
        """Test de liste des métriques"""
        AnalyticsMetric.objects.create(
            name='test_metric',
            display_name='Test Metric',
            category='user',
            metric_type='counter'
        )
        
        response = self.client.get('/api/analytics/metrics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_export_format_list(self):
        """Test de liste des formats d'export"""
        ExportFormat.objects.create(
            name='CSV',
            format_type='csv',
            mime_type='text/csv',
            file_extension='csv'
        )
        
        response = self.client.get('/api/analytics/exports/formats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AnalyticsIntegrationTestCase(TestCase):
    """Tests d'intégration pour Analytics"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.report_service = ReportService()
        self.analytics_service = AnalyticsService()
        self.export_service = ExportService()
        self.dashboard_service = DashboardService()
    
    def test_full_report_workflow(self):
        """Test du workflow complet de rapport"""
        # Créer un template
        template = ReportTemplate.objects.create(
            name='User Activity Template',
            report_type='user_activity',
            created_by=self.user
        )
        
        # Créer un rapport
        report = Report.objects.create(
            name='User Activity Report',
            template=template,
            report_type='user_activity',
            generated_by=self.user
        )
        
        # Générer le rapport
        generated_report = self.report_service.generate_report(report.id, self.user)
        
        self.assertEqual(generated_report.status, 'completed')
        self.assertIsNotNone(generated_report.data)
        self.assertIsNotNone(generated_report.summary)
    
    def test_dashboard_with_widgets(self):
        """Test de tableau de bord avec widgets"""
        # Créer un tableau de bord
        dashboard = self.dashboard_service.create_dashboard(
            name='Test Dashboard',
            dashboard_type='executive',
            owner=self.user
        )
        
        # Créer un widget
        widget_data = {
            'name': 'Test Widget',
            'widget_type': 'metric',
            'config': {'metric_name': 'total_users'},
            'position_x': 0,
            'position_y': 0,
            'width': 4,
            'height': 3
        }
        
        widget = self.dashboard_service.add_widget(dashboard.id, widget_data, self.user)
        
        self.assertEqual(widget.name, 'Test Widget')
        self.assertEqual(widget.dashboard, dashboard)
    
    def test_export_workflow(self):
        """Test du workflow d'export"""
        # Créer un format d'export
        export_format = ExportFormat.objects.create(
            name='CSV',
            format_type='csv',
            mime_type='text/csv',
            file_extension='csv'
        )
        
        # Créer un export
        export = self.export_service.create_export(
            name='Test Export',
            data_source='user_activity',
            export_format=export_format,
            user=self.user
        )
        
        # Traiter l'export
        processed_export = self.export_service.process_export(export.id)
        
        self.assertEqual(processed_export.status, 'completed')
        self.assertIsNotNone(processed_export.file_path)

