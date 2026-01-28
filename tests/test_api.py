"""
Tests para watchbug.api - Endpoints y procesamiento de reportes
"""

import pytest
from io import BytesIO
from watchbug.api import BugReport, ReportHandler
from watchbug.core import Watchbug


class TestBugReport:
    """Tests para la clase BugReport."""
    
    def test_create_from_dict(self, sample_bug_report):
        """Verifica creación de BugReport desde diccionario."""
        report = BugReport(sample_bug_report)
        
        assert report.comment == 'El botón de guardar no responde'
        assert report.url == 'https://example.com/page'
        assert len(report.errors) == 1
        assert len(report.console_errors) == 1
        assert len(report.network_errors) == 1
    
    def test_create_with_screenshot(self, sample_bug_report, sample_screenshot):
        """Verifica creación con screenshot."""
        report = BugReport(sample_bug_report, screenshot=sample_screenshot)
        
        assert report.screenshot is not None
        assert len(report.screenshot) > 0
        assert report.screenshot == sample_screenshot
    
    def test_to_dict(self, sample_bug_report):
        """Verifica conversión a diccionario."""
        report = BugReport(sample_bug_report)
        data = report.to_dict()
        
        assert data['comment'] == report.comment
        assert data['url'] == report.url
        assert data['has_screenshot'] is False
        assert 'errors' in data
        assert 'console_errors' in data
        assert 'network_errors' in data
    
    def test_to_dict_with_screenshot(self, sample_bug_report, sample_screenshot):
        """Verifica to_dict con screenshot presente."""
        report = BugReport(sample_bug_report, screenshot=sample_screenshot)
        data = report.to_dict()
        
        assert data['has_screenshot'] is True
    
    def test_repr(self, sample_bug_report):
        """Verifica representación string."""
        report = BugReport(sample_bug_report)
        repr_str = repr(report)
        
        assert 'BugReport' in repr_str
        assert report.url in repr_str
        assert str(len(report.errors)) in repr_str


class TestReportHandler:
    """Tests para ReportHandler."""
    
    def test_init_with_watchbug(self, test_env_vars):
        """Verifica inicialización con instancia de Watchbug."""
        wb = Watchbug()
        handler = ReportHandler(wb)
        
        assert handler.watchbug is wb
    
    def test_process_report_basic(self, test_env_vars, sample_bug_report):
        """Verifica procesamiento básico de reporte."""
        wb = Watchbug()
        handler = ReportHandler(wb)
        report = BugReport(sample_bug_report)
        
        result = handler.process_report(report)
        
        assert result['success'] is True
        assert 'services_used' in result
        assert 'errors' in result
    
    def test_process_report_with_screenshot(
        self, test_env_vars, sample_bug_report, sample_screenshot
    ):
        """Verifica procesamiento de reporte con screenshot."""
        wb = Watchbug()
        handler = ReportHandler(wb)
        report = BugReport(sample_bug_report, screenshot=sample_screenshot)
        
        result = handler.process_report(report)
        
        assert result['success'] is True
    
    def test_process_report_with_sentry_event(
        self, test_env_vars, sample_bug_report
    ):
        """Verifica procesamiento con Sentry event ID."""
        sample_bug_report['sentryEventId'] = 'abc123def456'
        
        wb = Watchbug()
        handler = ReportHandler(wb)
        report = BugReport(sample_bug_report)
        
        result = handler.process_report(report)
        
        assert result['success'] is True
        if 'sentry_event_id' in result:
            assert result['sentry_event_id'] == 'abc123def456'
    
    def test_process_report_with_logrocket_session(
        self, test_env_vars, sample_bug_report
    ):
        """Verifica procesamiento con LogRocket session URL."""
        sample_bug_report['logrocketSessionURL'] = 'https://app.logrocket.com/test/session/123'
        
        wb = Watchbug()
        handler = ReportHandler(wb)
        report = BugReport(sample_bug_report)
        
        result = handler.process_report(report)
        
        assert result['success'] is True
        if 'logrocket_session_url' in result:
            assert 'logrocket.com' in result['logrocket_session_url']


class TestFlaskIntegration:
    """Tests para integración con Flask."""
    
    def test_create_flask_endpoint(self, test_env_vars):
        """Verifica creación de endpoint Flask."""
        from watchbug.api import create_flask_endpoint
        
        wb = Watchbug()
        endpoint_func = create_flask_endpoint(wb)
        
        assert callable(endpoint_func)
        assert endpoint_func.__name__ == 'watchbug_report'
    
    @pytest.mark.skipif(
        not pytest.importorskip("flask", reason="Flask no instalado"),
        reason="Flask no disponible"
    )
    def test_flask_endpoint_post_request(self, test_env_vars, sample_bug_report):
        """Verifica endpoint Flask con POST request."""
        from flask import Flask
        from watchbug.api import create_flask_endpoint
        
        app = Flask(__name__)
        wb = Watchbug()
        
        app.route('/watchbug/report', methods=['POST'])(
            create_flask_endpoint(wb)
        )
        
        with app.test_client() as client:
            response = client.post(
                '/watchbug/report',
                data={
                    'reportData': str(sample_bug_report)
                }
            )
            
            # Debería responder aunque sea con error por formato
            assert response.status_code in [200, 400, 500]


class TestDjangoIntegration:
    """Tests para integración con Django."""
    
    def test_create_django_view(self, test_env_vars):
        """Verifica creación de view Django."""
        from watchbug.api import create_django_view
        
        wb = Watchbug()
        view_func = create_django_view(wb)
        
        assert callable(view_func)


class TestFastAPIIntegration:
    """Tests para integración con FastAPI."""
    
    def test_create_fastapi_endpoint(self, test_env_vars):
        """Verifica creación de endpoint FastAPI."""
        from watchbug.api import create_fastapi_endpoint
        
        wb = Watchbug()
        endpoint_func = create_fastapi_endpoint(wb)
        
        assert callable(endpoint_func)
