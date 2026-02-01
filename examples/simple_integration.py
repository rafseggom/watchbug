"""
Watchbug - Ejemplo Simplificado de Integración

Este ejemplo demuestra cómo integrar Watchbug en Flask con una sola línea.
"""

from flask import Flask, render_template_string
from watchbug.flask import setup_watchbug, init_sentry_before_flask
from watchbug import Watchbug

# Paso 1: Inicializar Watchbug
watchbug = Watchbug()

# Paso 2: Inicializar Sentry ANTES de Flask (evita problemas con reload)
init_sentry_before_flask(watchbug)

# Paso 3: Crear app Flask
app = Flask(__name__)

# Paso 4: Configurar Watchbug (UNA SOLA LÍNEA)
setup_watchbug(app, watchbug)

# Template de ejemplo
TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Watchbug - Ejemplo Simplificado</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .info {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        .info p {
            margin: 5px 0;
            color: #555;
        }
        
        .demo-buttons {
            display: grid;
            gap: 15px;
            margin-top: 30px;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        button:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button.danger {
            background: #e74c3c;
        }
        
        button.danger:hover {
            background: #c0392b;
        }
        
        code {
            background: #f1f3f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        .feature-list {
            list-style: none;
            margin-top: 20px;
        }
        
        .feature-list li {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
            color: #555;
        }
        
        .feature-list li:last-child {
            border-bottom: none;
        }
        
        .feature-list li::before {
            content: "✓ ";
            color: #667eea;
            font-weight: bold;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐛 Watchbug</h1>
        <p class="subtitle">Ejemplo de Integración Simplificada</p>
        
        <div class="info">
            <p><strong>Estado:</strong> Watchbug está activo</p>
            <p><strong>Integración:</strong> Una sola línea de código</p>
            <p><strong>Widget:</strong> Busca el botón 🐛 en la esquina inferior derecha</p>
        </div>
        
        <h3>Características Habilitadas:</h3>
        <ul class="feature-list">
            <li>Widget flotante para reportar bugs</li>
            <li>Captura automática de errores JavaScript</li>
            <li>Screenshots del navegador</li>
            <li>Integración con Sentry (tracking de errores)</li>
            <li>Integración con LogRocket (grabación de sesiones)</li>
            <li>Almacenamiento en Supabase</li>
        </ul>
        
        <div class="demo-buttons">
            <button onclick="testSuccess()">
                ✅ Acción Normal (Sin Errores)
            </button>
            <button class="danger" onclick="testError()">
                ⚠️ Simular Error (Prueba Watchbug)
            </button>
        </div>
        
        <div class="info" style="margin-top: 30px;">
            <p><strong>💡 Cómo Probar:</strong></p>
            <p>1. Haz clic en "Simular Error"</p>
            <p>2. Haz clic en el botón 🐛 de la esquina</p>
            <p>3. Describe el problema y envía el reporte</p>
            <p>4. ¡El error se enviará a Sentry, LogRocket y Supabase!</p>
        </div>
        
        <div class="info" style="margin-top: 20px; background: #fff3cd; border-left-color: #ffc107;">
            <p><strong>🔧 Configuración:</strong></p>
            <p>Solo necesitas 4 líneas en tu <code>app.py</code>:</p>
            <pre style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; overflow-x: auto;"><code>from watchbug.flask import setup_watchbug
watchbug = Watchbug()
init_sentry_before_flask(watchbug)
setup_watchbug(app, watchbug)</code></pre>
        </div>
    </div>
    
    <!-- Watchbug Widget se inyecta automáticamente -->
    {{ watchbug_script|safe }}
    
    <script>
        function testSuccess() {
            alert('✅ Todo funcionó correctamente!\\n\\nEsta es una acción normal sin errores.');
        }
        
        function testError() {
            console.log('🧪 Generando error de prueba...');
            
            // Generar error intencional
            throw new Error('Error de prueba generado intencionalmente para demostrar Watchbug');
        }
        
        console.log('%c🐛 Watchbug Activo', 'background: #667eea; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;');
        console.log('Widget cargado correctamente. Busca el botón 🐛 en la esquina inferior derecha.');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🐛 WATCHBUG - EJEMPLO SIMPLIFICADO")
    print("="*60)
    print("\n📱 Servidor iniciado en: http://localhost:5000")
    print("\n🎯 Características:")
    print("   ✓ Integración con una sola línea")
    print("   ✓ Widget automático inyectado")
    print("   ✓ Captura de errores habilitada")
    print("   ✓ Dashboard disponible (si WATCHBUG_ADMIN=true)")
    print("\n💡 Cómo probar:")
    print("   1. Abre http://localhost:5000 en tu navegador")
    print("   2. Haz clic en 'Simular Error'")
    print("   3. Haz clic en el botón 🐛 que aparece abajo a la derecha")
    print("   4. Completa el formulario de reporte")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
