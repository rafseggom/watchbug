"""
Tests de integración end-to-end

Estos tests verifican flujos completos del sistema.
"""

import pytest
from watchbug.core import Watchbug
from watchbug.api import BugReport, ReportHandler


class TestEndToEndFlow:
    """Tests de flujo completo desde widget hasta almacenamiento."""
    
    def test_complete_bug_report_flow(
        self, test_env_vars, sample_bug_report, sample_screenshot
    ):
        """
        Test completo: inicializar Watchbug → crear reporte → procesar
        """
        # 1. Inicializar Watchbug
        wb = Watchbug()
        assert wb.services['sentry']['enabled'] is True
        
        # 2. Verificar servicios
        results = wb.check_all()
        assert results['sentry'].valid is True
        
        # 3. Crear reporte con datos completos
        report = BugReport(sample_bug_report, screenshot=sample_screenshot)
        assert report.screenshot is not None
        
        # 4. Procesar reporte
        handler = ReportHandler(wb)
        result = handler.process_report(report)
        
        # 5. Verificar resultado
        assert result['success'] is True
        assert 'services_used' in result
    
    def test_widget_injection(self, test_env_vars):
        """
        Test de generación del script tag para inyección en HTML
        """
        # 1. Inicializar
        wb = Watchbug()
        
        # 2. Generar script tag
        script = wb.get_script_tag(api_endpoint='/api/bugs')
        
        # 3. Verificar contenido
        assert '<script>' in script
        assert 'window.__WATCHBUG_CONFIG__' in script
        assert '/api/bugs' in script
        assert 'html2canvas' in script
        
        # 4. Verificar que incluye configuración de servicios
        assert 'sentry' in script.lower()
        assert 'logrocket' in script.lower()
    
    def test_minimal_configuration(self, clean_env):
        """
        Test con configuración mínima (sin servicios externos)
        """
        # Watchbug debería funcionar sin servicios configurados
        wb = Watchbug()
        
        # Todos deshabilitados
        assert wb.services['sentry']['enabled'] is False
        assert wb.services['logrocket']['enabled'] is False
        assert wb.services['supabase']['enabled'] is False
        
        # Pero el widget aún se puede generar
        script = wb.get_script_tag(api_endpoint='/test')
        assert script is not None
        assert '/test' in script
    
    def test_partial_configuration(self, clean_env):
        """
        Test con solo algunos servicios configurados
        """
        # Solo Sentry
        wb = Watchbug(
            sentry_dsn="https://test@o123.ingest.sentry.io/456"
        )
        
        assert wb.services['sentry']['enabled'] is True
        assert wb.services['logrocket']['enabled'] is False
        assert wb.services['supabase']['enabled'] is False
        
        # Procesar reporte
        sample_data = {
            'comment': 'Test',
            'url': 'https://test.com',
            'userAgent': 'Test',
            'viewport': {'width': 1920, 'height': 1080},
            'errors': [],
            'consoleErrors': [],
            'networkErrors': []
        }
        
        report = BugReport(sample_data)
        handler = ReportHandler(wb)
        result = handler.process_report(report)
        
        assert result['success'] is True


class TestErrorHandling:
    """Tests de manejo de errores."""
    
    def test_invalid_report_data(self, test_env_vars):
        """Verifica manejo de datos inválidos en reporte."""
        wb = Watchbug()
        
        # Datos mínimos requeridos
        minimal_data = {
            'comment': '',
            'url': '',
            'userAgent': '',
            'viewport': {},
            'errors': [],
            'consoleErrors': [],
            'networkErrors': []
        }
        
        report = BugReport(minimal_data)
        handler = ReportHandler(wb)
        
        # No debería lanzar excepción
        result = handler.process_report(report)
        assert 'success' in result
    
    def test_missing_screenshot(self, test_env_vars, sample_bug_report):
        """Verifica que funciona sin screenshot."""
        wb = Watchbug()
        handler = ReportHandler(wb)
        
        report = BugReport(sample_bug_report)  # Sin screenshot
        result = handler.process_report(report)
        
        assert result['success'] is True
        
        report_dict = report.to_dict()
        assert report_dict['has_screenshot'] is False


class TestServiceIntegration:
    """Tests de integración con servicios externos (mocked)."""
    
    def test_sentry_integration_ready(self, test_env_vars):
        """Verifica que Sentry está listo para integración."""
        wb = Watchbug()
        
        assert wb.services['sentry']['enabled'] is True
        assert wb.services['sentry']['dsn'] is not None
        assert 'ingest.sentry.io' in wb.services['sentry']['dsn'] or \
               'ingest.de.sentry.io' in wb.services['sentry']['dsn']
    
    def test_logrocket_integration_ready(self, test_env_vars):
        """Verifica que LogRocket está listo para integración."""
        wb = Watchbug()
        
        assert wb.services['logrocket']['enabled'] is True
        assert wb.services['logrocket']['id'] is not None
        assert '/' in wb.services['logrocket']['id']
    
    def test_supabase_integration_ready(self, test_env_vars):
        """Verifica que Supabase está listo para integración."""
        wb = Watchbug()
        
        assert wb.services['supabase']['enabled'] is True
        assert wb.services['supabase']['url'] is not None
        assert wb.services['supabase']['key'] is not None
        assert 'supabase.co' in wb.services['supabase']['url']
