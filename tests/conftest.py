"""
Fixtures compartidos para tests de Watchbug
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
def test_env_vars(monkeypatch):
    """Fixture que configura variables de entorno de prueba."""
    monkeypatch.setenv('SENTRY_DSN', 'https://test123@o123456.ingest.sentry.io/123456')
    monkeypatch.setenv('LOGROCKET_ID', 'test-org/test-app')
    monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
    monkeypatch.setenv('SUPABASE_KEY', 'test-key-1234567890')


@pytest.fixture
def clean_env(monkeypatch):
    """Fixture que limpia todas las variables de entorno de Watchbug."""
    monkeypatch.delenv('SENTRY_DSN', raising=False)
    monkeypatch.delenv('LOGROCKET_ID', raising=False)
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('SUPABASE_KEY', raising=False)


@pytest.fixture
def sample_bug_report():
    """Fixture con un reporte de bug de ejemplo."""
    return {
        'comment': 'El botón de guardar no responde',
        'url': 'https://example.com/page',
        'timestamp': '2026-01-28T10:30:00Z',
        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'viewport': {'width': 1920, 'height': 1080},
        'errors': [
            {
                'type': 'javascript',
                'message': 'Cannot read property "name" of undefined',
                'stack': 'Error: at line 42',
                'timestamp': '2026-01-28T10:29:58Z'
            }
        ],
        'consoleErrors': [
            {'message': 'API timeout', 'timestamp': '2026-01-28T10:29:55Z'}
        ],
        'networkErrors': [
            {'url': '/api/save', 'status': 500, 'timestamp': '2026-01-28T10:29:57Z'}
        ]
    }


@pytest.fixture
def sample_screenshot():
    """Fixture con un screenshot PNG de prueba (1x1 pixel transparente)."""
    # PNG de 1x1 pixel transparente (67 bytes)
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'


@pytest.fixture
def temp_env_file(tmp_path):
    """Crea un archivo .env temporal para testing."""
    env_file = tmp_path / ".env"
    env_content = """
SENTRY_DSN=https://test@o123.ingest.sentry.io/456
LOGROCKET_ID=test/app
SUPABASE_URL=https://test.supabase.co
SUPABASE_KEY=test-key
"""
    env_file.write_text(env_content.strip())
    return env_file
