"""
Ejemplo de aplicación Flask con Watchbug integrado

Este ejemplo muestra cómo integrar Watchbug en una aplicación Flask.
"""

import os
from flask import Flask, render_template_string
from watchbug import Watchbug
from watchbug.api import create_flask_endpoint
from watchbug.dashboard import create_flask_dashboard

app = Flask(__name__)

# Configuración de Flask para manejar archivos grandes
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB máximo
app.config['UPLOAD_FOLDER'] = '/tmp'

# Inicializar Watchbug
watchbug = Watchbug()

# Inicializar Sentry ANTES de registrar rutas (solo si está habilitado)
# Esto evita que Flask se reinicie cuando Sentry se inicializa
if watchbug.services['sentry']['enabled']:
    try:
        import sentry_sdk
        from watchbug.api import _sentry_initialized
        
        if not _sentry_initialized:
            dsn = watchbug.services['sentry']['dsn']
            sentry_sdk.init(
                dsn=dsn,
                traces_sample_rate=0.0,
                profiles_sample_rate=0.0,
                debug=False,
            )
            # Marcar como inicializado
            import watchbug.api as api_module
            api_module._sentry_initialized = True
            print("✓ Sentry inicializado en startup")
    except Exception as e:
        print(f"⚠ Error inicializando Sentry: {e}")
        # Desactivar Sentry si falla la inicialización
        watchbug.services['sentry']['enabled'] = False

# Registrar endpoint de reportes
app.add_url_rule(
    '/watchbug/report',
    'watchbug_report',
    create_flask_endpoint(watchbug),
    methods=['POST']
)

# Registrar dashboard si está habilitado
admin_enabled = os.getenv('WATCHBUG_ADMIN', 'false').lower() == 'true'
if admin_enabled:
    dashboard_view, api_reports, api_report_details, api_service_links, api_stats = create_flask_dashboard(watchbug)
    
    app.add_url_rule(
        '/watchbug/dashboard',
        'watchbug_dashboard',
        dashboard_view,
        methods=['GET']
    )
    
    app.add_url_rule(
        '/watchbug/dashboard/api/reports',
        'watchbug_api_reports',
        api_reports,
        methods=['GET']
    )
    
    app.add_url_rule(
        '/watchbug/dashboard/api/reports/<report_id>',
        'watchbug_api_report_details',
        api_report_details,
        methods=['GET']
    )
    
    app.add_url_rule(
        '/watchbug/dashboard/api/services',
        'watchbug_api_services',
        api_service_links,
        methods=['GET']
    )
    
    app.add_url_rule(
        '/watchbug/dashboard/api/stats',
        'watchbug_api_stats',
        api_stats,
        methods=['GET']
    )

# Template HTML de ejemplo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo de Watchbug</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #FF6B6B;
            padding-bottom: 10px;
        }
        .card {
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 5px;
        }
        button:hover {
            background: #45a049;
        }
        button.error {
            background: #f44336;
        }
        button.error:hover {
            background: #da190b;
        }
        .info {
            background: #E3F2FD;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
        }
        .warning {
            background: #FFF3E0;
            border-left: 4px solid #FF9800;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>🐛 Watchbug - Demo Interactiva</h1>
    
    <div class="info">
        <strong>¿Qué es Watchbug?</strong><br>
        Watchbug es un sistema que unifica reportes de bugs desde usuarios no técnicos.
        Captura errores, screenshots y contexto automáticamente.
    </div>
    
    <div class="card">
        <h2>Servicios Activos:</h2>
        <ul>
            <li>🔥 Sentry: {{ 'Activo' if sentry else 'Inactivo' }}</li>
            <li>📹 LogRocket: {{ 'Activo' if logrocket else 'Inactivo' }}</li>
            <li>💾 Supabase: {{ 'Activo' if supabase else 'Inactivo' }}</li>
        </ul>
    </div>
    
    <div class="card">
        <h2>Prueba el Widget</h2>
        <p>El botón flotante rojo 🐛 en la esquina inferior derecha te permite reportar bugs.</p>
        
        <h3>Provoca algunos errores para probar:</h3>
        
        <button onclick="throwError()">
            💥 Generar Error de JavaScript
        </button>
        
        <button onclick="throwPromiseError()">
            ⚡ Error de Promise
        </button>
        
        <button onclick="makeFailedRequest()">
            🌐 Petición HTTP Fallida
        </button>
        
        <button onclick="logErrors()">
            📝 Mensajes de Console
        </button>
        
        <button onclick="clearErrors()" class="error">
            🗑️ Limpiar Errores
        </button>
    </div>
    
    <div class="warning">
        <strong>💡 Tip:</strong> Después de generar errores, haz clic en el botón 🐛
        para abrir el formulario de reporte. Verás que Watchbug ha capturado
        automáticamente todos los errores.
    </div>
    
    <div class="card">
        <h2>Cómo Funciona</h2>
        <ol>
            <li><strong>Intercepta errores:</strong> Captura automáticamente errores de JavaScript, consola y red</li>
            <li><strong>Captura pantalla:</strong> Toma un screenshot del estado actual de la página</li>
            <li><strong>Recopila contexto:</strong> URL, navegador, viewport, timestamp</li>
            <li><strong>Vincula servicios:</strong> Conecta con Sentry Event ID y LogRocket Session</li>
            <li><strong>Envía reporte:</strong> Todo unificado en un solo paquete al backend</li>
        </ol>
    </div>
    
    <script>
        function throwError() {
            try {
                throw new Error('Este es un error de ejemplo generado por el botón');
            } catch (e) {
                console.error('Error capturado:', e);
                throw e;
            }
        }
        
        function throwPromiseError() {
            Promise.reject(new Error('Error en Promise rechazada'));
        }
        
        function makeFailedRequest() {
            fetch('/endpoint-que-no-existe')
                .then(response => {
                    if (!response.ok) {
                        console.error('Petición fallida:', response.status);
                    }
                })
                .catch(error => {
                    console.error('Error en fetch:', error);
                });
        }
        
        function logErrors() {
            console.error('Error 1: Validación de formulario falló');
            console.error('Error 2: Usuario sin permisos');
            console.error('Error 3: Timeout en la petición');
        }
        
        function clearErrors() {
            // Acceder al estado global de Watchbug
            const script = document.querySelector('script:not([src])');
            if (script && script.textContent.includes('WatchbugState')) {
                console.log('[Demo] Limpiando errores del estado de Watchbug');
                // El estado está dentro de una closure, pero podemos acceder vía consola
                console.log('[Demo] Ejecuta en la consola: WatchbugState');
            }
            alert('Para ver el estado de errores, abre la consola del navegador y escribe: WatchbugState');
        }
    </script>
    
    <!-- Inyectar Watchbug Widget -->
    {{ watchbug_script|safe }}
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal de demostración."""
    
    # Obtener el script tag de Watchbug
    watchbug_script = watchbug.get_script_tag(api_endpoint='/watchbug/report')
    
    # Obtener estado de configuración real (con credenciales válidas)
    config_status = watchbug.get_config_status()
    
    # Renderizar template con la configuración (solo activos si tienen credenciales Y están enabled)
    return render_template_string(
        HTML_TEMPLATE,
        watchbug_script=watchbug_script,
        sentry=config_status['services']['sentry']['configured'] and config_status['services']['sentry']['enabled'],
        logrocket=config_status['services']['logrocket']['configured'] and config_status['services']['logrocket']['enabled'],
        supabase=config_status['services']['supabase']['configured'] and config_status['services']['supabase']['enabled']
    )


@app.route('/test')
def test_widget():
    """Página de prueba para debuggear el widget."""
    import os
    template_path = os.path.join(os.path.dirname(__file__), 'test_widget.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    watchbug_script = watchbug.get_script_tag(api_endpoint='/watchbug/report')
    return render_template_string(template, watchbug_script=watchbug_script)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Watchbug Demo App - Flask")
    print("="*60)
    print(f"\n✓ Watchbug está {'ACTIVO' if watchbug.is_enabled() else 'DESACTIVADO'}")
    
    config = watchbug.get_config_status()
    print("\nServicios configurados:")
    for service, info in config['services'].items():
        status = "✓" if info['enabled'] else "○"
        print(f"  {status} {service.capitalize()}")
    
    print("\n" + "="*60)
    print("Abre tu navegador en: http://localhost:5000")
    print("="*60 + "\n")
    
    # Configurar extra_files para evitar reinicios innecesarios
    # Solo observar archivos de este proyecto, no de librerías
    import sys
    extra_files = []
    
    # Desactivar el reloader temporalmente si Sentry está habilitado
    # Esto evita problemas con Sentry en modo debug
    use_reloader = not watchbug.services['sentry']['enabled']
    
    if not use_reloader:
        print("⚠ Auto-reloader desactivado porque Sentry está habilitado")
        print("  (Evita conflictos con Flask debug mode)\n")
    
    app.run(debug=True, port=5000, use_reloader=use_reloader)
