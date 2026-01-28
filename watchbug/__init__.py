"""
Watchbug - Sistema de reporte de bugs unificado para usuarios pilotos

Uso básico:
    from watchbug import Watchbug
    
    watchbug = Watchbug()
    script_tag = watchbug.get_script_tag()
    # Inyectar script_tag en tu HTML
"""

from .core import Watchbug
from .checks import ServiceStatus, ValidationResult

__version__ = "0.1.0"
__all__ = ["Watchbug", "ServiceStatus", "ValidationResult"]
