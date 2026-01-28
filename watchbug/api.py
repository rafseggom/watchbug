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
        logger.info(f"Procesando reporte: {report}")
        
        result = {
            'success': True,
            'report_id': None,
            'services_used': [],
            'errors': []
        }
        
        try:
            # TODO (Milestone 3): Subir a Supabase si está habilitado
            if self.watchbug.services['supabase']['enabled']:
                logger.info("Supabase habilitado - guardando en base de datos")
                # supabase_id = self._save_to_supabase(report)
                # result['report_id'] = supabase_id
                # result['services_used'].append('supabase')
                logger.warning("Integración con Supabase pendiente (Milestone 3)")
            
            # TODO (Milestone 4): Vincular con Sentry si hay eventId
            if report.sentry_event_id and self.watchbug.services['sentry']['enabled']:
                logger.info(f"Sentry Event ID detectado: {report.sentry_event_id}")
                result['services_used'].append('sentry')
                result['sentry_event_id'] = report.sentry_event_id
            
            # TODO (Milestone 4): Vincular con LogRocket si hay sessionURL
            if report.logrocket_session_url and self.watchbug.services['logrocket']['enabled']:
                logger.info(f"LogRocket Session URL detectado: {report.logrocket_session_url}")
                result['services_used'].append('logrocket')
                result['logrocket_session_url'] = report.logrocket_session_url
            
            # Por ahora, solo loggeamos el reporte
            logger.info("Reporte recibido correctamente:")
            logger.info(f"  URL: {report.url}")
            logger.info(f"  Comentario: {report.comment}")
            logger.info(f"  Errores JS: {len(report.errors)}")
            logger.info(f"  Errores consola: {len(report.console_errors)}")
            logger.info(f"  Errores red: {len(report.network_errors)}")
            logger.info(f"  Screenshot: {'Sí' if report.screenshot else 'No'}")
            
        except Exception as e:
            logger.error(f"Error procesando reporte: {e}", exc_info=True)
            result['success'] = False
            result['errors'].append(str(e))
        
        return result
    
    def _save_to_supabase(self, report: BugReport) -> str:
        """
        Guarda el reporte en Supabase.
        
        TODO: Implementar en Milestone 3
        
        Args:
            report: El reporte a guardar
            
        Returns:
            ID del reporte en Supabase
        """
        # from supabase import create_client
        # client = create_client(
        #     self.watchbug.services['supabase']['url'],
        #     self.watchbug.services['supabase']['key']
        # )
        # 
        # # Subir screenshot al Storage si existe
        # screenshot_url = None
        # if report.screenshot:
        #     filename = f"screenshots/{report.timestamp}_{hash(report.url)}.png"
        #     client.storage.from_('watchbug-reports').upload(filename, report.screenshot)
        #     screenshot_url = client.storage.from_('watchbug-reports').get_public_url(filename)
        # 
        # # Insertar en tabla de reportes
        # data = report.to_dict()
        # data['screenshot_url'] = screenshot_url
        # result = client.table('bug_reports').insert(data).execute()
        # 
        # return result.data[0]['id']
        
        raise NotImplementedError("Implementar en Milestone 3")


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
            # Parsear datos JSON
            data_str = request.form.get('data')
            if not data_str:
                return jsonify({'error': 'No data provided'}), 400
            
            data = json.loads(data_str)
            
            # Obtener screenshot si existe
            screenshot = None
            if 'screenshot' in request.files:
                screenshot = request.files['screenshot'].read()
            
            # Crear y procesar reporte
            report = BugReport(data, screenshot)
            result = handler.process_report(report)
            
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500
                
        except Exception as e:
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
