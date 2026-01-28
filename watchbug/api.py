"""
Watchbug API - Endpoint para recibir reportes del frontend

Este módulo proporciona handlers para frameworks web (Flask, Django, FastAPI)
que procesan los reportes enviados desde el widget frontend.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx  # Usamos httpx directamente para evitar dependencias pesadas

logger = logging.getLogger("watchbug.api")


class BugReport:
    """Representa un reporte de bug enviado desde el frontend."""
    
    def __init__(self, data: Dict[str, Any], screenshot: Optional[bytes] = None):
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
        return f"BugReport(url='{self.url}', errors={len(self.errors)}, comment='{self.comment[:50]}...')"


class ReportHandler:
    """Handler base para procesar reportes de bugs."""
    
    def __init__(self, watchbug_instance):
        self.watchbug = watchbug_instance
    
    def process_report(self, report: BugReport) -> Dict[str, Any]:
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
            # Mostrar logs en consola
            print(f"\n📍 URL: {report.url}")
            print(f"💬 Comentario: {report.comment}")
            print(f"❌ Errores JS: {len(report.errors)} | 📝 Consola: {len(report.console_errors)} | 🌐 Red: {len(report.network_errors)}")
            print(f"📸 Screenshot: {'✓ Capturado' if report.screenshot else '✗ No disponible'}")
            
            # Subir a Supabase si está habilitado
            if self.watchbug.services['supabase']['enabled']:
                try:
                    print(f"   💾 Supabase: Guardando...")
                    supabase_id = self._save_to_supabase(report)
                    result['report_id'] = supabase_id
                    result['services_used'].append('supabase')
                    print(f"   💾 Supabase: ✓ Guardado con ID: {supabase_id}")
                except Exception as e:
                    print(f"   💾 Supabase: ✗ Error: {str(e)}")
                    logger.error(f"Error guardando en Supabase: {e}", exc_info=True)
                    result['errors'].append(f"Supabase error: {str(e)}")
            
            # Informar de otros servicios
            if report.sentry_event_id:
                result['services_used'].append('sentry')
                result['sentry_event_id'] = report.sentry_event_id
                print(f"   🔥 Sentry ID: {report.sentry_event_id}")
            
            if report.logrocket_session_url:
                result['services_used'].append('logrocket')
                result['logrocket_session_url'] = report.logrocket_session_url
                print(f"   📹 LogRocket: {report.logrocket_session_url}")

            print("\n" + "="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR procesando reporte: {e}")
            logger.error(f"Error procesando reporte: {e}", exc_info=True)
            result['success'] = False
            result['errors'].append(str(e))
        
        return result
    
    def _save_to_supabase(self, report: BugReport) -> str:
        """
        Guarda el reporte en Supabase usando httpx directamente.
        Esto evita dependencias pesadas que requieren compilación C++.
        """
        import hashlib
        
        # Recuperar credenciales del config de watchbug
        config = self.watchbug.services['supabase']
        url = config['url']
        key = config['key']
        
        if not url or not key:
            raise Exception("Credenciales Supabase incompletas o no configuradas")

        # Headers comunes para autenticación
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }

        # 1. Subir Screenshot al Storage
        screenshot_url = None
        screenshot_size = None
        
        if report.screenshot:
            try:
                # Generar nombre único
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                url_hash = hashlib.md5(report.url.encode()).hexdigest()[:8]
                filename = f"{timestamp}_{url_hash}.png"
                bucket_name = "watchbug-screenshots"
                
                # API Endpoint de Storage (POST /storage/v1/object/{bucket}/{filename})
                storage_url = f"{url}/storage/v1/object/{bucket_name}/{filename}"
                storage_headers = {
                    **headers,
                    "Content-Type": "image/png"
                }
                
                with httpx.Client() as client:
                    resp = client.post(
                        storage_url,
                        content=report.screenshot,
                        headers=storage_headers,
                        timeout=30.0
                    )
                    resp.raise_for_status()
                
                # Construir URL pública
                screenshot_url = f"{url}/storage/v1/object/public/{bucket_name}/{filename}"
                screenshot_size = len(report.screenshot)
                logger.info(f"Screenshot subido: {filename}")
                
            except Exception as e:
                logger.error(f"Error subiendo screenshot: {e}", exc_info=True)
                # No bloqueamos el reporte si falla la imagen

        # 2. Insertar en Base de Datos (PostgREST)
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
        
        # Endpoint de la tabla (POST /rest/v1/{table})
        db_url = f"{url}/rest/v1/bug_reports"
        db_headers = {
            **headers,
            "Content-Type": "application/json",
            "Prefer": "return=representation"  # Importante: para que devuelva el ID creado
        }
        
        with httpx.Client() as client:
            resp = client.post(
                db_url,
                json=data,
                headers=db_headers,
                timeout=30.0
            )
            resp.raise_for_status()
            result = resp.json()
            
        if not result or len(result) == 0:
            raise Exception("Supabase no retornó ID después del insert")
            
        return result[0]['id']


# ============================================
# Framework Integrations (Flask, Django, FastAPI)
# ============================================

def create_flask_endpoint(watchbug_instance):
    """Crea un endpoint Flask para recibir reportes."""
    handler = ReportHandler(watchbug_instance)
    
    def flask_view():
        from flask import request, jsonify
        try:
            print("\n[Watchbug API] Recibiendo reporte...")
            data_str = request.form.get('data')
            if not data_str: return jsonify({'error': 'No data provided'}), 400
            
            try: data = json.loads(data_str)
            except json.JSONDecodeError as e: return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
            
            screenshot = None
            if 'screenshot' in request.files:
                screenshot = request.files['screenshot'].read()
            
            report = BugReport(data, screenshot)
            result = handler.process_report(report)
            
            return jsonify(result), (200 if result['success'] else 500)
                
        except Exception as e:
            logger.error(f"Error en endpoint Flask: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    return flask_view


def create_django_view(watchbug_instance):
    """Crea una view de Django para recibir reportes."""
    handler = ReportHandler(watchbug_instance)
    
    def django_view(request):
        from django.http import JsonResponse
        from django.views.decorators.csrf import csrf_exempt
        
        @csrf_exempt
        def _view(request):
            if request.method != 'POST': return JsonResponse({'error': 'Method not allowed'}, status=405)
            try:
                data_str = request.POST.get('data')
                if not data_str: return JsonResponse({'error': 'No data provided'}, status=400)
                
                data = json.loads(data_str)
                screenshot = None
                if 'screenshot' in request.FILES:
                    screenshot = request.FILES['screenshot'].read()
                
                report = BugReport(data, screenshot)
                result = handler.process_report(report)
                
                return JsonResponse(result, status=(200 if result['success'] else 500))
                    
            except Exception as e:
                logger.error(f"Error en view Django: {e}", exc_info=True)
                return JsonResponse({'error': str(e)}, status=500)
        return _view(request)
    return django_view


def create_fastapi_endpoint(watchbug_instance):
    """Crea un endpoint FastAPI para recibir reportes."""
    handler = ReportHandler(watchbug_instance)
    
    async def fastapi_endpoint(request):
        from fastapi.responses import JSONResponse
        try:
            form = await request.form()
            data_str = form.get('data')
            if not data_str: return JSONResponse({'error': 'No data provided'}, status_code=400)
            
            data = json.loads(data_str)
            screenshot = None
            if 'screenshot' in form:
                screenshot = await form['screenshot'].read()
            
            report = BugReport(data, screenshot)
            result = handler.process_report(report)
            return JSONResponse(result, status_code=(200 if result['success'] else 500))
                
        except Exception as e:
            logger.error(f"Error en endpoint FastAPI: {e}", exc_info=True)
            return JSONResponse({'error': str(e)}, status_code=500)
    return fastapi_endpoint