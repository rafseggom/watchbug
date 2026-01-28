"""
Tests para watchbug.checks - Validaciones de servicios
"""

import pytest
from watchbug.checks import (
    ServiceStatus,
    ValidationResult,
    validate_sentry_dsn,
    validate_logrocket_id,
    validate_supabase_credentials
)


class TestServiceStatus:
    """Tests para el enum ServiceStatus."""
    
    def test_status_values(self):
        """Verifica que todos los estados existen."""
        assert ServiceStatus.ENABLED.value == 'enabled'
        assert ServiceStatus.DISABLED.value == 'disabled'
        assert ServiceStatus.INVALID_CONFIG.value == 'invalid_config'
        assert ServiceStatus.NOT_CONFIGURED.value == 'not_configured'
        assert ServiceStatus.ONLINE.value == 'online'
        assert ServiceStatus.OFFLINE.value == 'offline'


class TestValidationResult:
    """Tests para la clase ValidationResult."""
    
    def test_valid_result(self):
        """Verifica creación de resultado válido."""
        result = ValidationResult(valid=True, status=ServiceStatus.ENABLED)
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
        assert result.message is None
    
    def test_invalid_result(self):
        """Verifica creación de resultado inválido con mensaje."""
        result = ValidationResult(
            valid=False,
            status=ServiceStatus.INVALID_CONFIG,
            message="Error de formato"
        )
        assert result.valid is False
        assert result.status == ServiceStatus.INVALID_CONFIG
        assert result.message == "Error de formato"


class TestSentryValidation:
    """Tests para validación de Sentry DSN."""
    
    def test_valid_sentry_dsn(self):
        """Verifica DSN válido de Sentry."""
        dsn = "https://abc123@o123456.ingest.sentry.io/456789"
        result = validate_sentry_dsn(dsn)
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
    
    def test_valid_sentry_dsn_with_region(self):
        """Verifica DSN válido de Sentry con región (.de)."""
        dsn = "https://abc123@o123456.ingest.de.sentry.io/456789"
        result = validate_sentry_dsn(dsn)
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
    
    def test_invalid_sentry_dsn_format(self):
        """Verifica rechazo de DSN con formato inválido."""
        invalid_dsns = [
            "not-a-url",
            "http://invalid",
            "https://missing-parts.com",
            "",
            None
        ]
        
        for dsn in invalid_dsns:
            result = validate_sentry_dsn(dsn)
            assert result.valid is False
            assert result.status == ServiceStatus.INVALID_CONFIG
            assert result.message is not None
    
    def test_empty_sentry_dsn(self):
        """Verifica que DSN vacío se marca como no configurado."""
        result = validate_sentry_dsn("")
        assert result.valid is False
        assert result.status == ServiceStatus.INVALID_CONFIG


class TestLogRocketValidation:
    """Tests para validación de LogRocket ID."""
    
    def test_valid_logrocket_id(self):
        """Verifica ID válido de LogRocket."""
        valid_ids = [
            "myorg/myapp",
            "test-org/test-app",
            "org123/app456"
        ]
        
        for lr_id in valid_ids:
            result = validate_logrocket_id(lr_id)
            assert result.valid is True
            assert result.status == ServiceStatus.ENABLED
    
    def test_invalid_logrocket_id(self):
        """Verifica rechazo de IDs inválidos."""
        invalid_ids = [
            "no-slash",
            "/missing-org",
            "missing-app/",
            "too/many/slashes",
            "",
            None
        ]
        
        for lr_id in invalid_ids:
            result = validate_logrocket_id(lr_id)
            assert result.valid is False
            assert result.status == ServiceStatus.INVALID_CONFIG


class TestSupabaseValidation:
    """Tests para validación de credenciales de Supabase."""
    
    def test_valid_supabase_credentials(self):
        """Verifica credenciales válidas de Supabase."""
        url = "https://myproject.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        
        result = validate_supabase_credentials(url, key)
        assert result.valid is True
        assert result.status == ServiceStatus.ENABLED
    
    def test_invalid_supabase_url(self):
        """Verifica rechazo de URL inválida."""
        invalid_urls = [
            "not-a-url",
            "http://wrong-domain.com",
            "https://notsupabase.com",
            "",
            None
        ]
        
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        
        for url in invalid_urls:
            result = validate_supabase_credentials(url, key)
            assert result.valid is False
            assert result.status == ServiceStatus.INVALID_CONFIG
    
    def test_invalid_supabase_key(self):
        """Verifica rechazo de key inválida."""
        url = "https://myproject.supabase.co"
        invalid_keys = [
            "short",
            "",
            None,
            "not-a-jwt-token"
        ]
        
        for key in invalid_keys:
            result = validate_supabase_credentials(url, key)
            assert result.valid is False
            assert result.status == ServiceStatus.INVALID_CONFIG
    
    def test_both_invalid(self):
        """Verifica cuando ambos parámetros son inválidos."""
        result = validate_supabase_credentials("", "")
        assert result.valid is False
        assert result.status == ServiceStatus.INVALID_CONFIG
