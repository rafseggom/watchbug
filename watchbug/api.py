"""
Watchbug API - Endpoint para recibir reportes del frontend

Este módulo proporciona handlers para frameworks web (Flask, Django, FastAPI)
que procesan los reportes enviados desde el widget frontend.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("watchbug.api")


class BugReport:
    """Representa un reporte de bug enviado desde el frontend."""
    
    def __init__(self, data: Dict[str, Any], screenshot: Optional[bytes] = None):
        """
        Inicializa un BugReport desde los datos del frontend.
        
        Args:
            data: Diccionario con la información del reporte
            screenshot: Bytes del screenshot (PNG), opcional
        """
        self.comment = data.get('comment', '')
        self.url = data.get('url', '')
        self.timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        self.user_agent = data.get('userAgent', '')
        self.viewport = data.get('viewport', {})
        self.errors = data.get('errors', [])
        self.console_errors = data.get('consoleErrors', [])
        self.network_errors = data.get('networkErrors', [])
        self.sentry_event_id = data.get('sentryEventId')
        self.logrocket_session_url = data.get('logrocketSessionURL')
        self.screenshot = screenshot
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el reporte a diccionario."""
        return {
            'comment': self.comment,
            'url': self.url,
            'timestamp': self.timestamp,
            'user_agent': self.user_agent,
            'viewport': self.viewport,
            'errors': self.errors,
            'console_errors': self.console_errors,
            'network_errors': self.network_errors,
            'sentry_event_id': self.sentry_event_id,
            'logrocket_session_url': self.logrocket_session_url,
            'has_screenshot': self.screenshot is not None
        }
    
    def __repr__(self):
        return (
            f"BugReport(url='{self.url}', "
            f"errors={len(self.errors)}, "
            f"comment='{self.comment[:50]}...')"
        )


class ReportHandler:
    """
    Handler base para procesar reportes de bugs.
    
    Subclases específicas implementan el procesamiento para cada framework.
    """
    
    def __init__(self, watchbug_instance):
        """
        Args:
            watchbug_instance: Instancia de la clase Watchbug
        """
        self.watchbug = watchbug_instance
    
    def process_report(self, report: BugReport) -> Dict[str, Any]:
        """
        Procesa un reporte de bug.
        
        Args:
            report: El reporte a procesar
            
        Returns:
            Diccionario con el resultado del procesamiento
        """
        print("\n" + "="*60)
        print("🐛 NUEVO REPORTE DE BUG RECIBIDO")
        print("="*60)
        
        result = {
            'success': True,
            'report_id': None,
            'services_used': [],
            'errors': []
        }
        
        try:
            # Mostrar información del reporte
            print(f"\n📍 URL: {report.url}")
            print(f"⏰ Timestamp: {report.timestamp}")
            print(f"💬 Comentario: {report.comment}")
            print(f"\n🖥️  Navegador: {report.user_agent[:80]}...")
            print(f"📐 Viewport: {report.viewport.get('width')}x{report.viewport.get('height')}")
            
            # Errores capturados
            print(f"\n❌ Errores JavaScript: {len(report.errors)}")
            if report.errors:
                for i, error in enumerate(report.errors[:3], 1):  # Mostrar primeros 3
                    print(f"   {i}. {error.get('type')}: {error.get('message')[:100]}")
            
            print(f"📝 Errores de Consola: {len(report.console_errors)}")
            if report.console_errors:
                for i, error in enumerate(report.console_errors[:3], 1):
                    print(f"   {i}. {error.get('message')[:100]}")
            
            print(f"🌐 Errores de Red: {len(report.network_errors)}")
            if report.network_errors:
                for i, error in enumerate(report.network_errors[:3], 1):
                    print(f"   {i}. {error.get('url')} - {error.get('status', 'Network error')}")
            
            print(f"\n📸 Screenshot: {'✓ Capturado' if report.screenshot else '✗ No disponible'}")
            if report.screenshot:
                print(f"   Tamaño: {len(report.screenshot)} bytes")
            
            # Servicios externos
            print(f"\n🔗 Servicios Vinculados:")
            
            # Subir a Supabase si está habilitado
            if self.watchbug.services['supabase']['enabled']:
                try:
                    print(f"   💾 Supabase: Guardando en base de datos...")
                    supabase_id = self._save_to_supabase(report)
                    result['report_id'] = supabase_id
                    result['services_used'].append('supabase')
                    print(f"   💾 Supabase: ✓ Guardado con ID: {supabase_id}")
                except Exception as e:
                    print(f"   💾 Supabase: ✗ Error: {str(e)}")
                    logger.error(f"Error guardando en Supabase: {e}", exc_info=True)
                    result['errors'].append(f"Supabase error: {str(e)}")
            else:
                print(f"   💾 Supabase: Desactivado")
            
            # TODO (Milestone 4): Vincular con Sentry si hay eventId
            if report.sentry_event_id and self.watchbug.services['sentry']['enabled']:
                print(f"   🔥 Sentry Event ID: {report.sentry_event_id}")
                result['services_used'].append('sentry')
                result['sentry_event_id'] = report.sentry_event_id
            else:
                print(f"   🔥 Sentry: No event ID")
            
            # TODO (Milestone 4): Vincular con LogRocket si hay sessionURL
            if report.logrocket_session_url and self.watchbug.services['logrocket']['enabled']:
                print(f"   📹 LogRocket Session: {report.logrocket_session_url}")
                result['services_used'].append('logrocket')
                result['logrocket_session_url'] = report.logrocket_session_url
            else:
                print(f"   📹 LogRocket: No session URL")
            
            print("\n" + "="*60)
            print("✅ Reporte procesado exitosamente")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR procesando reporte: {e}")
            logger.error(f"Error procesando reporte: {e}", exc_info=True)
            result['success'] = False
            result['errors'].append(str(e))
        
        return result
    
    def _save_to_supabase(self, report: BugReport) -> str:
        """
        Guarda el reporte en Supabase usando postgrest directamente.
        
        Args:
            report: El reporte a guardar
            
        Returns:
            ID del reporte en Supabase
        """
        import hashlib
        from datetime import datetime
        import httpx
        from postgrest import SyncPostgrestClient
        
        supabase_url = self.watchbug.services['supabase']['url']
        supabase_key = self.watchbug.services['supabase']['key']
        
        # Crear cliente PostgREST
        api_url = f"{supabase_url}/rest/v1"
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Subir screenshot al Storage si existe
        screenshot_url = None
        screenshot_size = None
        
        if report.screenshot:
            try:
                # Generar nombre único para el archivo
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                url_hash = hashlib.md5(report.url.encode()).hexdigest()[:8]
                filename = f"{timestamp}_{url_hash}.png"
                
                # Subir al Storage usando la API REST
                storage_url = f"{supabase_url}/storage/v1/object/watchbug-screenshots/{filename}"
                storage_headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}",
                    "Content-Type": "image/png",
                }
                
                with httpx.Client() as client:
                    storage_response = client.post(
                        storage_url,
                        content=report.screenshot,
                        headers=storage_headers,
                        timeout=30.0
                    )
                    storage_response.raise_for_status()
                
                # URL pública del screenshot
                screenshot_url = f"{supabase_url}/storage/v1/object/public/watchbug-screenshots/{filename}"
                screenshot_size = len(report.screenshot)
                
                logger.info(f"Screenshot subido a Supabase: {filename}")
                
            except Exception as e:
                logger.error(f"Error subiendo screenshot a Supabase: {e}", exc_info=True)
                # Continuar sin screenshot si falla
        
        # Preparar datos para insertar en la tabla
        data = {
            'comment': report.comment,
            'url': report.url,
            'timestamp': report.timestamp,
            'user_agent': report.user_agent,
            'viewport_width': report.viewport.get('width'),
            'viewport_height': report.viewport.get('height'),
            'errors': report.errors,
            'console_errors': report.console_errors,
            'network_errors': report.network_errors,
            'sentry_event_id': report.sentry_event_id,
            'logrocket_session_url': report.logrocket_session_url,
            'screenshot_url': screenshot_url,
            'screenshot_size': screenshot_size
        }
        
        # Insertar en tabla de bug_reports usando httpx directamente
        table_url = f"{api_url}/bug_reports"
        
        with httpx.Client() as client:
            response = client.post(
                table_url,
                json=data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
        
        if not result or len(result) == 0:
            raise Exception("Supabase no retornó datos después del insert")
        
        report_id = result[0]['id']
        logger.info(f"Reporte guardado en Supabase con ID: {report_id}")
        
        return report_id


# ============================================
# Flask Integration
# ============================================

def create_flask_endpoint(watchbug_instance):
    """
    Crea un endpoint Flask para recibir reportes.
    
    Uso:
        from flask import Flask
        from watchbug import Watchbug
        from watchbug.api import create_flask_endpoint
        
        app = Flask(__name__)
        watchbug = Watchbug()
        
        app.add_url_rule(
            '/watchbug/report',
            'watchbug_report',
            create_flask_endpoint(watchbug),
            methods=['POST']
        )
    
    Args:
        watchbug_instance: Instancia de Watchbug
        
    Returns:
        View function para Flask
    """
    handler = ReportHandler(watchbug_instance)
    
    def flask_view():
        from flask import request, jsonify
        
        try:
            print("\n[Watchbug API] Recibiendo reporte...")
            
            # Parsear datos JSON
            data_str = request.form.get('data')
            if not data_str:
                print("[Watchbug API] ERROR: No se recibió 'data' en el form")
                return jsonify({'error': 'No data provided'}), 400
            
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError as e:
                print(f"[Watchbug API] ERROR parseando JSON: {e}")
                return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
            
            # Obtener screenshot si existe
            screenshot = None
            if 'screenshot' in request.files:
                screenshot_file = request.files['screenshot']
                screenshot = screenshot_file.read()
                print(f"[Watchbug API] Screenshot recibido: {len(screenshot)} bytes")
            else:
                print("[Watchbug API] No se recibió screenshot")
            
            # Crear y procesar reporte
            report = BugReport(data, screenshot)
            result = handler.process_report(report)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
            print(f"[Watchbug API] EXCEPCIÓN en endpoint Flask: {e}")
            logger.error(f"Error en endpoint Flask: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    return flask_view


# ============================================
# Django Integration
# ============================================

def create_django_view(watchbug_instance):
    """
    Crea una view de Django para recibir reportes.
    
    Uso:
        # En urls.py
        from watchbug import Watchbug
        from watchbug.api import create_django_view
        
        watchbug = Watchbug()
        
        urlpatterns = [
            path('watchbug/report/', create_django_view(watchbug)),
        ]
    
    Args:
        watchbug_instance: Instancia de Watchbug
        
    Returns:
        View function para Django
    """
    handler = ReportHandler(watchbug_instance)
    
    def django_view(request):
        from django.http import JsonResponse
        from django.views.decorators.csrf import csrf_exempt
        
        @csrf_exempt
        def _view(request):
            if request.method != 'POST':
                return JsonResponse({'error': 'Method not allowed'}, status=405)
            
            try:
                # Parsear datos JSON
                data_str = request.POST.get('data')
                if not data_str:
                    return JsonResponse({'error': 'No data provided'}, status=400)
                
                data = json.loads(data_str)
                
                # Obtener screenshot si existe
                screenshot = None
                if 'screenshot' in request.FILES:
                    screenshot = request.FILES['screenshot'].read()
                
                # Crear y procesar reporte
                report = BugReport(data, screenshot)
                result = handler.process_report(report)
                
                if result['success']:
                    return JsonResponse(result, status=200)
                else:
                    return JsonResponse(result, status=500)
                    
            except Exception as e:
                logger.error(f"Error en view Django: {e}", exc_info=True)
                return JsonResponse({'error': str(e)}, status=500)
        
        return _view(request)
    
    return django_view


# ============================================
# FastAPI Integration
# ============================================

def create_fastapi_endpoint(watchbug_instance):
    """
    Crea un endpoint FastAPI para recibir reportes.
    
    Uso:
        from fastapi import FastAPI
        from watchbug import Watchbug
        from watchbug.api import create_fastapi_endpoint
        
        app = FastAPI()
        watchbug = Watchbug()
        
        app.post('/watchbug/report')(create_fastapi_endpoint(watchbug))
    
    Args:
        watchbug_instance: Instancia de Watchbug
        
    Returns:
        Endpoint function para FastAPI
    """
    handler = ReportHandler(watchbug_instance)
    
    async def fastapi_endpoint(request):
        from fastapi import Request
        from fastapi.responses import JSONResponse
        
        try:
            # Parsear form data
            form = await request.form()
            
            data_str = form.get('data')
            if not data_str:
                return JSONResponse({'error': 'No data provided'}, status_code=400)
            
            data = json.loads(data_str)
            
            # Obtener screenshot si existe
            screenshot = None
            if 'screenshot' in form:
                screenshot = await form['screenshot'].read()
            
            # Crear y procesar reporte
            report = BugReport(data, screenshot)
            result = handler.process_report(report)
            
            if result['success']:
                return JSONResponse(result, status_code=200)
            else:
                return JSONResponse(result, status_code=500)
                
        except Exception as e:
            logger.error(f"Error en endpoint FastAPI: {e}", exc_info=True)
            return JSONResponse({'error': str(e)}, status_code=500)
    
    return fastapi_endpoint
