"""
Watchbug Core - Sistema de reporte de bugs unificado

Este módulo contiene la clase principal Watchbug que orquesta la recolección
de información de errores desde múltiples fuentes (Sentry, LogRocket) y
opcionalmente las almacena en Supabase.
"""

import os
import json
import logging
from typing import Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

from .checks import (
    ServiceStatus,
    ValidationResult,
    validate_sentry_dsn,
    validate_logrocket_id,
    validate_supabase_credentials,
    check_sentry_connection,
    check_logrocket_connection,
    check_supabase_connection,
)


# Configurar logging
logger = logging.getLogger("watchbug")
logger.setLevel(logging.INFO)


class Watchbug:
    """
    Clase principal de Watchbug.
    
    Watchbug puede funcionar en diferentes modos:
    - Con Supabase: Almacenamiento centralizado + integración con Sentry/LogRocket
    - Sin Supabase: Los errores van directamente a Sentry/LogRocket (modo lightweight)
    - Cualquier combinación de servicios es válida
    
    El sistema se desactiva automáticamente si:
    - WATCHBUG_ENABLED=False
    - Ningún servicio está configurado correctamente
    """
    
    def __init__(self):
        """Inicializa Watchbug cargando configuración desde variables de entorno."""
        load_dotenv()
        
        # Flag maestro para activar/desactivar todo el sistema
        self.master_enabled = os.getenv("WATCHBUG_ENABLED", "True") == "True"
        
        # Configuración de cada servicio
        self.services = {
            'sentry': {
                'enabled': self._parse_bool_env("SENTRY_ENABLED", default=None),
                'explicitly_disabled': self._parse_bool_env("SENTRY_ENABLED", default=None) is False,
                'dsn': os.getenv("SENTRY_DSN"),
                'validation': None,  # Se llenará en check_service()
            },
            'logrocket': {
                'enabled': self._parse_bool_env("LOGROCKET_ENABLED", default=None),
                'explicitly_disabled': self._parse_bool_env("LOGROCKET_ENABLED", default=None) is False,
                'id': os.getenv("LOGROCKET_ID"),
                'validation': None,
            },
            'supabase': {
                'enabled': self._parse_bool_env("SUPABASE_ENABLED", default=None),
                'explicitly_disabled': self._parse_bool_env("SUPABASE_ENABLED", default=None) is False,
                'url': os.getenv("SUPABASE_URL"),
                'key': os.getenv("SUPABASE_KEY"),
                'validation': None,
            }
        }
        
        # Auto-detectar qué servicios deberían estar activos
        self._apply_smart_defaults()
        
        # Validar configuración inicial
        self._initial_validation()
        
        # --- Inicialización del cliente Supabase ---
        self._supabase_client: Optional[Client] = None
        if self.services['supabase']['enabled']:
            try:
                url = self.services['supabase']['url']
                key = self.services['supabase']['key']
                # Creamos el cliente oficial
                self._supabase_client = create_client(url, key)
                logger.info("Cliente de Supabase inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando Supabase client: {e}")
                # Si falla la inicialización, desactivamos el servicio para evitar errores en runtime
                self.services['supabase']['enabled'] = False
                self._supabase_client = None

    @property
    def supabase(self) -> Optional[Client]:
        """Acceso directo al cliente de Supabase."""
        return self._supabase_client
    
    def _parse_bool_env(self, var_name: str, default: Optional[bool] = None) -> Optional[bool]:
        """Parse una variable de entorno como booleano."""
        value = os.getenv(var_name)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes")
    
    def _apply_smart_defaults(self):
        """Aplica lógica inteligente para activar/desactivar servicios."""
        for service_name, config in self.services.items():
            if config['enabled'] is not None:
                continue
            
            if service_name == 'sentry':
                config['enabled'] = bool(config['dsn'])
            elif service_name == 'logrocket':
                config['enabled'] = bool(config['id'])
            elif service_name == 'supabase':
                config['enabled'] = bool(config['url'] and config['key'])
    
    def _initial_validation(self):
        """Ejecuta validación inicial y configura el estado de Watchbug."""
        if not self.master_enabled:
            logger.info("Watchbug está desactivado (WATCHBUG_ENABLED=False)")
            return
        
        validation_results = self.check_all(online=False)
        valid_services = [name for name, result in validation_results.items() if result.is_valid()]
        
        if not valid_services:
            logger.warning("Watchbug no tiene servicios configurados. Se desactivará.")
            self.master_enabled = False
        else:
            logger.info(f"Watchbug inicializado con: {', '.join(valid_services)}")
    
    def is_enabled(self) -> bool:
        return self.master_enabled
    
    def check_service(self, service_name: str, online: bool = False) -> ValidationResult:
        if service_name not in self.services:
            raise ValueError(f"Servicio desconocido: '{service_name}'")
        
        config = self.services[service_name]
        
        if config['explicitly_disabled']:
            result = ValidationResult(ServiceStatus.DISABLED, f"{service_name} desactivado explícitamente")
            config['validation'] = result
            return result
        
        if service_name == 'sentry':
            result = validate_sentry_dsn(config['dsn'])
            if online and result.is_valid(): result = check_sentry_connection(config['dsn'])
        elif service_name == 'logrocket':
            result = validate_logrocket_id(config['id'])
            if online and result.is_valid(): result = check_logrocket_connection(config['id'])
        elif service_name == 'supabase':
            result = validate_supabase_credentials(config['url'], config['key'])
            if online and result.is_valid(): result = check_supabase_connection(config['url'], config['key'])
        
        config['validation'] = result
        return result
    
    def check_all(self, online: bool = False) -> Dict[str, ValidationResult]:
        return {name: self.check_service(name, online=online) for name in self.services}
    
    def get_config_status(self) -> Dict:
        status = {'master_enabled': self.master_enabled, 'services': {}}
        for service_name, config in self.services.items():
            service_status = {
                'enabled': config['enabled'],
                'configured': False,
                'validation': None,
            }
            if service_name == 'sentry': service_status['configured'] = bool(config['dsn'])
            elif service_name == 'logrocket': service_status['configured'] = bool(config['id'])
            elif service_name == 'supabase': service_status['configured'] = bool(config['url'] and config['key'])
            
            if config['validation']:
                service_status['validation'] = {
                    'status': config['validation'].status.value,
                    'message': config['validation'].message,
                }
            status['services'][service_name] = service_status
        return status
    
    def get_script_tag(self, api_endpoint: str = "/watchbug/report") -> str:
        if not self.is_enabled():
            return ""
        
        widget_path = os.path.join(os.path.dirname(__file__), 'static', 'watchbug-widget.js')
        try:
            with open(widget_path, 'r', encoding='utf-8') as f:
                widget_js = f.read()
        except FileNotFoundError:
            logger.error(f"Widget JavaScript no encontrado en {widget_path}")
            return ""
        
        config = {
            'enabled': True,
            'services': {
                'sentry': self.services['sentry']['enabled'],
                'logrocket': self.services['logrocket']['enabled'],
                'supabase': self.services['supabase']['enabled']
            },
            'apiEndpoint': api_endpoint
        }
        
        return f"""
<script>window.__WATCHBUG_CONFIG__ = {json.dumps(config)};</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js" integrity="sha512-D/fON2XxZ0f5TrA/qNg4/mfnHDnCPPBST0jUnr1x+bBBCNIaACWODR+g5iIQ/KRJ7+R8fR/Y+VwzhC0Lgh+4A==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script>{widget_js}</script>
""".strip()