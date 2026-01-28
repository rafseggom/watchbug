# Tests de Watchbug

Suite de tests automatizados para validar la funcionalidad de Watchbug.

## Estructura

```
tests/
├── __init__.py              # Paquete de tests
├── conftest.py              # Fixtures compartidos
├── test_checks.py           # Tests de validación de servicios
├── test_core.py             # Tests de funcionalidad principal
├── test_api.py              # Tests de endpoints y procesamiento
└── test_integration.py      # Tests de integración end-to-end
```

## Ejecutar tests

### Instalar dependencias de desarrollo

```bash
pip install -e ".[dev]"
```

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests específicos

```bash
# Tests de un módulo específico
pytest tests/test_core.py

# Tests de una clase específica
pytest tests/test_checks.py::TestSentryValidation

# Un test individual
pytest tests/test_core.py::TestWatchbugInit::test_init_with_env_vars

# Tests con un marker específico
pytest -m integration
```

### Con coverage

```bash
# Ejecutar tests con reporte de coverage
pytest --cov=watchbug --cov-report=html

# Ver reporte en navegador
start htmlcov/index.html  # Windows
```

### Modos verbosos

```bash
# Modo verbose (más detalle)
pytest -v

# Modo muy verbose (máximo detalle)
pytest -vv

# Mostrar print statements
pytest -s

# Detener en primer fallo
pytest -x
```

## Fixtures disponibles

Definidos en `conftest.py`:

- **test_env_vars**: Configura variables de entorno de prueba
- **clean_env**: Limpia variables de entorno
- **sample_bug_report**: Reporte de bug de ejemplo
- **sample_screenshot**: Screenshot PNG de prueba
- **temp_env_file**: Archivo .env temporal

## Escribir nuevos tests

### Template básico

```python
import pytest
from watchbug.core import Watchbug

class TestMyFeature:
    """Tests para mi nueva funcionalidad."""
    
    def test_something(self, test_env_vars):
        """Verifica que algo funciona."""
        wb = Watchbug()
        result = wb.my_method()
        assert result is True
```

### Usar fixtures

```python
def test_with_fixture(sample_bug_report):
    """Test que usa fixture de reporte."""
    assert sample_bug_report['comment'] is not None
```

### Marcar tests

```python
@pytest.mark.integration
def test_end_to_end():
    """Test de integración completo."""
    pass

@pytest.mark.slow
def test_performance():
    """Test que tarda varios segundos."""
    pass
```

## Cobertura actual

Ejecutar `pytest --cov=watchbug` para ver cobertura actual.

**Objetivo**: >80% de cobertura en código principal.

## Tests de integración

Los tests en `test_integration.py` validan flujos completos:

- Inicialización → Validación → Reporte → Procesamiento
- Generación de widget con diferentes configuraciones
- Manejo de errores y casos edge

## CI/CD

Estos tests se pueden integrar en GitHub Actions:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest --cov=watchbug
```

## Solución de problemas

### ImportError en tests

```bash
# Reinstalar en modo desarrollo
pip install -e .
```

### Tests fallan con variables de entorno

Los tests usan fixtures que configuran env vars automáticamente.
Si fallan, verifica que no tengas un `.env` real interfiriendo.

### Flask/Django/FastAPI no disponible

Los tests de framework están marcados con `skipif` para ejecutarse
solo si el framework está instalado. No afectan el resto de tests.
