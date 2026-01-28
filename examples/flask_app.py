"""
Ejemplo de aplicación Flask con Watchbug integrado

Este ejemplo muestra cómo integrar Watchbug en una aplicación Flask.
"""

from flask import Flask, render_template_string
from watchbug import Watchbug
from watchbug.api import create_flask_endpoint

app = Flask(__name__)

# Inicializar Watchbug
watchbug = Watchbug()

# Registrar endpoint de reportes
app.add_url_rule(
    '/watchbug/report',
    'watchbug_report',
    create_flask_endpoint(watchbug),
    methods=['POST']
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
            throw new Error('Este es un error de ejemplo generado por el botón');
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
                });
        }
        
        function logErrors() {
            console.error('Error 1: Validación de formulario falló');
            console.error('Error 2: Usuario sin permisos');
            console.error('Error 3: Timeout en la petición');
        }
        
        function clearErrors() {
            if (window.WatchbugState) {
                window.WatchbugState.errors = [];
                window.WatchbugState.consoleErrors = [];
                window.WatchbugState.networkErrors = [];
                alert('Errores limpiados');
            }
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
    
    # Renderizar template con la configuración
    return render_template_string(
        HTML_TEMPLATE,
        watchbug_script=watchbug_script,
        sentry=watchbug.services['sentry']['enabled'],
        logrocket=watchbug.services['logrocket']['enabled'],
        supabase=watchbug.services['supabase']['enabled']
    )


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
    
    app.run(debug=True, port=5000)
