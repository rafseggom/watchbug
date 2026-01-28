"""
Tests para watchbug.core - Funcionalidad principal
"""

import pytest
import os
from watchbug.core import Watchbug
from watchbug.checks import ServiceStatus


class TestWatchbugInit:
    """Tests para inicialización de Watchbug."""
    
    def test_init_with_env_vars(self, test_env_vars):
        """Verifica inicialización con variables de entorno."""
        wb = Watchbug()
        
        assert wb.services['sentry']['enabled'] is True
        assert wb.services['logrocket']['enabled'] is True
        assert wb.services['supabase']['enabled'] is True
    
    def test_init_without_env_vars(self, clean_env):
        """Verifica inicialización sin variables de entorno."""
        wb = Watchbug()
        
        # Todos los servicios deben estar deshabilitados
        assert wb.services['sentry']['enabled'] is False
        assert wb.services['logrocket']['enabled'] is False
        assert wb.services['supabase']['enabled'] is False
    
    def test_init_with_explicit_params(self, clean_env):
        """Verifica inicialización con parámetros explícitos."""
        wb = Watchbug(
            sentry_dsn="https://test@o123.ingest.sentry.io/456",
            logrocket_id="test/app"
        )
        
        assert wb.services['sentry']['enabled'] is True
        assert wb.services['logrocket']['enabled'] is True
        assert wb.services['supabase']['enabled'] is False
    
    def test_explicit_params_override_env(self, test_env_vars):
        """Verifica que parámetros explícitos sobrescriben env vars."""
        wb = Watchbug(
            sentry_dsn="https://override@o999.ingest.sentry.io/999"
        )
        
        assert "override" in wb.services['sentry']['dsn']
        assert wb.services['sentry']['enabled'] is True


class TestWatchbugServiceChecks:
    """Tests para verificación de servicios."""
    
    def test_check_sentry_enabled(self, test_env_vars):
        """Verifica check de Sentry habilitado."""
        wb = Watchbug()
        result = wb.check_service('sentry')
        
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
    
    def test_check_sentry_disabled(self, clean_env):
        """Verifica check de Sentry deshabilitado."""
        wb = Watchbug()
        result = wb.check_service('sentry')
        
        assert result.valid is False
        assert result.status == ServiceStatus.NOT_CONFIGURED
    
    def test_check_logrocket_enabled(self, test_env_vars):
        """Verifica check de LogRocket habilitado."""
        wb = Watchbug()
        result = wb.check_service('logrocket')
        
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
    
    def test_check_supabase_enabled(self, test_env_vars):
        """Verifica check de Supabase habilitado."""
        wb = Watchbug()
        result = wb.check_service('supabase')
        
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
    
    def test_check_invalid_service(self, test_env_vars):
        """Verifica que servicios inválidos lanzan error."""
        wb = Watchbug()
        
        with pytest.raises(ValueError, match="Servicio desconocido"):
            wb.check_service('invalid_service')
    
    def test_check_all_services(self, test_env_vars):
        """Verifica check de todos los servicios."""
        wb = Watchbug()
        results = wb.check_all()
        
        assert 'sentry' in results
        assert 'logrocket' in results
        assert 'supabase' in results
        
        assert results['sentry'].valid is True
        assert results['logrocket'].valid is True
        assert results['supabase'].valid is True


class TestWatchbugScriptTag:
    """Tests para generación del script tag."""
    
    def test_get_script_tag_basic(self, test_env_vars):
        """Verifica generación básica del script tag."""
        wb = Watchbug()
        script = wb.get_script_tag(api_endpoint='/api/watchbug/report')
        
        assert '<script>' in script
        assert 'window.__WATCHBUG_CONFIG__' in script
        assert '/api/watchbug/report' in script
        assert 'html2canvas' in script
    
    def test_script_tag_contains_config(self, test_env_vars):
        """Verifica que el script tag contiene la configuración."""
        wb = Watchbug()
        script = wb.get_script_tag(api_endpoint='/test/endpoint')
        
        assert '"apiEndpoint": "/test/endpoint"' in script
        assert '"sentry":' in script
        assert '"logrocket":' in script
    
    def test_script_tag_with_disabled_services(self, clean_env):
        """Verifica script tag con servicios deshabilitados."""
        wb = Watchbug()
        script = wb.get_script_tag(api_endpoint='/test')
        
        assert 'window.__WATCHBUG_CONFIG__' in script
        assert '/test' in script
    
    def test_script_tag_includes_widget_js(self, test_env_vars):
        """Verifica que el script tag incluye el código del widget."""
        wb = Watchbug()
        script = wb.get_script_tag(api_endpoint='/test')
        
        # Verificar que contiene código del widget
        assert 'WatchbugState' in script or 'watchbug' in script.lower()


class TestWatchbugSmartDefaults:
    """Tests para smart defaults."""
    
    def test_sentry_dsn_enabled_by_default(self):
        """Verifica que un DSN válido habilita Sentry automáticamente."""
        wb = Watchbug(
            sentry_dsn="https://test@o123.ingest.sentry.io/456"
        )
        
        assert wb.services['sentry']['enabled'] is True
    
    def test_invalid_dsn_disables_sentry(self):
        """Verifica que un DSN inválido deshabilita Sentry."""
        wb = Watchbug(
            sentry_dsn="invalid-dsn"
        )
        
        assert wb.services['sentry']['enabled'] is False
    
    def test_logrocket_id_enabled_by_default(self):
        """Verifica que un ID válido habilita LogRocket."""
        wb = Watchbug(
            logrocket_id="org/app"
        )
        
        assert wb.services['logrocket']['enabled'] is True
    
    def test_supabase_both_required(self):
        """Verifica que Supabase requiere URL y key."""
        # Solo URL
        wb1 = Watchbug(
            supabase_url="https://test.supabase.co"
        )
        assert wb1.services['supabase']['enabled'] is False
        
        # Solo key
        wb2 = Watchbug(
            supabase_key="test-key-123"
        )
        assert wb2.services['supabase']['enabled'] is False
        
        # Ambos
        wb3 = Watchbug(
            supabase_url="https://test.supabase.co",
            supabase_key="test-key-123"
        )
        assert wb3.services['supabase']['enabled'] is True
