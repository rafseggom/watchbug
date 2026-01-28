# 🐛 Watchbug

**Sistema unificado de reporte de bugs** que integra Sentry, LogRocket y Supabase para capturar errores, sesiones de usuario y screenshots en un solo lugar.

Cuando un usuario encuentra un problema, Watchbug captura automáticamente:
- **Stack trace** del error (Sentry)
- **Sesión del usuario** con replay (LogRocket)
- **Screenshot** del momento exacto
- **Comentario** descriptivo del usuario
- **Contexto** completo (URL, navegador, consola, red)

Todo se almacena centralizadamente en Supabase para análisis posterior.

---

## 📦 Instalación

### Desde pip (recomendado)

```bash
pip install watchbug
```

### Desde código fuente

```bash
git clone https://github.com/tu-usuario/watchbug.git
cd watchbug
pip install -e .
```

---

## ⚙️ Configuración

### 1. Crea tu archivo de variables de entorno

```bash
cp .env.example .env
```

### 2. Configura tus credenciales en `.env`

```bash
# Control maestro
WATCHBUG_ENABLED=True

# Sentry - Tracking de errores
SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>

# LogRocket - Grabación de sesiones
LOGROCKET_ID=your-org/your-app

# Supabase - Almacenamiento centralizado
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...  # Tu anon/public key
SUPABASE_BUCKET_NAME=watchbug-screenshots

# Dashboard de administración (solo desarrollo)
WATCHBUG_ADMIN=false  # Cambiar a 'true' para habilitar
```

#### Obtener credenciales:

**Sentry:**
1. Ve a https://sentry.io/settings/projects/
2. Selecciona tu proyecto
3. Copia el DSN que aparece en "Client Keys (DSN)"

**LogRocket:**
1. Ve a https://app.logrocket.com/
2. Settings > Setup
3. Copia el App ID (formato: `organization/app-name`)

**Supabase:**
1. Ve a https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Settings > API
4. Copia el "Project URL" y "anon/public key"
5. Ve a Storage > Create Bucket
6. Crea un bucket llamado `watchbug-screenshots` y márcalo como **público**

### 3. Crear la tabla en Supabase

Ejecuta este SQL en el SQL Editor de Supabase:

```sql
CREATE TABLE bug_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  url TEXT NOT NULL,
  user_comment TEXT NOT NULL,
  user_agent TEXT,
  viewport JSONB,
  errors JSONB,
  console_errors JSONB,
  network_errors JSONB,
  sentry_event_id TEXT,
  logrocket_session_url TEXT,
  screenshot_url TEXT
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_bug_reports_created_at ON bug_reports(created_at DESC);
CREATE INDEX idx_bug_reports_url ON bug_reports(url);
CREATE INDEX idx_bug_reports_sentry ON bug_reports(sentry_event_id) WHERE sentry_event_id IS NOT NULL;
```

### 4. Validar configuración

Watchbug incluye un CLI para verificar que todo está correcto:

```bash
# Validación rápida
watchbug check

# Ver estado detallado
watchbug status

# Probar conectividad real con los servicios
watchbug check --online
```

Ejemplo de salida:

```
🔍 Watchbug - Validación de Servicios
==================================================
✓ Sentry       - DSN válido
✓ LogRocket    - ID válido  
✓ Supabase     - Credenciales válidas

✓ Todos los servicios configurados correctamente (3/3)
```

---

## 🚀 Uso

### Integración con Flask

```python
from flask import Flask, render_template
from watchbug import Watchbug
from watchbug.api import create_flask_endpoint

app = Flask(__name__)

# Inicializar Watchbug (carga automáticamente desde .env)
watchbug = Watchbug()

# Registrar endpoint de reportes
app.add_url_rule(
    '/watchbug/report',
    'watchbug_report',
    create_flask_endpoint(watchbug),
    methods=['POST']
)

@app.route('/')
def index():
    # Inyectar widget en tu HTML
    script_tag = watchbug.get_script_tag(api_endpoint='/watchbug/report')
    return render_template('index.html', watchbug_script=script_tag)
```

En tu template `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Mi App</title>
</head>
<body>
    <h1>Mi Aplicación</h1>
    
    <!-- Contenido de tu app -->
    
    <!-- Inyectar Watchbug al final del body -->
    {{ watchbug_script|safe }}
</body>
</html>
```

### Integración con Django

```python
# urls.py
from django.urls import path
from watchbug import Watchbug
from watchbug.api import create_django_view

watchbug = Watchbug()

urlpatterns = [
    path('watchbug/report/', create_django_view(watchbug)),
]

# views.py
from django.shortcuts import render

def my_view(request):
    script_tag = watchbug.get_script_tag(api_endpoint='/watchbug/report/')
    return render(request, 'index.html', {'watchbug_script': script_tag})
```

### Integración con FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from watchbug import Watchbug
from watchbug.api import create_fastapi_endpoint

app = FastAPI()
watchbug = Watchbug()

# Registrar endpoint
app.post('/watchbug/report')(create_fastapi_endpoint(watchbug))

@app.get('/', response_class=HTMLResponse)
async def index():
    script_tag = watchbug.get_script_tag(api_endpoint='/watchbug/report')
    return f"""
    <html>
        <body>
            <h1>Mi App</h1>
            {script_tag}
        </body>
    </html>
    """
```

### Dashboard de Administración (Opcional)

Si configuras `WATCHBUG_ADMIN=true` en tu `.env`, tendrás acceso a un dashboard visual para ver todos los reportes.

**Flask:**

```python
import os
from watchbug.dashboard import create_flask_dashboard

# Solo habilitar en desarrollo
if os.getenv('WATCHBUG_ADMIN', 'false').lower() == 'true':
    dashboard_view, api_reports, api_report_details, api_services, api_stats = create_flask_dashboard(watchbug)
    
    app.add_url_rule('/watchbug/dashboard', 'watchbug_dashboard', dashboard_view, methods=['GET'])
    app.add_url_rule('/watchbug/dashboard/api/reports', 'watchbug_api_reports', api_reports, methods=['GET'])
    app.add_url_rule('/watchbug/dashboard/api/reports/<report_id>', 'watchbug_api_report_details', api_report_details, methods=['GET'])
    app.add_url_rule('/watchbug/dashboard/api/services', 'watchbug_api_services', api_services, methods=['GET'])
    app.add_url_rule('/watchbug/dashboard/api/stats', 'watchbug_api_stats', api_stats, methods=['GET'])
```

Con el dashboard habilitado:
- Aparece un botón flotante 📊 al lado del botón de reportes 🐛
- Dashboard accesible en `/watchbug/dashboard`
- Tabla interactiva con todos los reportes
- Estadísticas en tiempo real
- Links directos a Sentry, LogRocket y Supabase
- Visor de screenshots

---

## 🔧 Cómo Funciona

### 1. Widget Frontend

El widget JavaScript se inyecta automáticamente con `get_script_tag()` y:

- **Intercepta errores** globales de JavaScript (`window.onerror`, `unhandledrejection`)
- **Captura errores de consola** (`console.error`)
- **Monitorea requests fallidos** (fetch y XHR)
- **Integra Sentry** para capturar stack traces
- **Integra LogRocket** para grabar la sesión del usuario
- **Muestra un botón flotante** 🐛 en la esquina inferior derecha

### 2. Captura de Reportes

Cuando el usuario hace clic en el botón 🐛:

1. Se abre un modal pidiendo que describa el problema
2. Al enviar:
   - Captura screenshot con **html2canvas**
   - Recopila errores interceptados
   - Obtiene el Event ID de Sentry (si hay)
   - Obtiene la URL de sesión de LogRocket (si hay)
   - Envía todo al endpoint `/watchbug/report`

### 3. Procesamiento Backend

El endpoint de Watchbug:

1. Recibe el reporte con screenshot
2. **Envía a Sentry** (si está configurado) con contexto completo
3. **Linkea con LogRocket** (si está configurado)
4. **Sube screenshot a Supabase Storage** (si está configurado)
5. **Guarda registro en tabla `bug_reports`** de Supabase

### 4. Almacenamiento en Supabase

Cada reporte se guarda con:

```json
{
  "id": "uuid",
  "created_at": "2024-01-15T10:30:00Z",
  "url": "https://miapp.com/checkout",
  "user_comment": "El botón de pagar no responde",
  "errors": [...],
  "console_errors": [...],
  "network_errors": [...],
  "sentry_event_id": "abc123",
  "logrocket_session_url": "https://app.logrocket.com/...",
  "screenshot_url": "https://supabase.co/storage/.../screenshot.png"
}
```

### 5. Flujo Completo

```
Usuario → Encuentra Error
   ↓
Widget → Intercepta automáticamente
   ↓
Usuario → Click en 🐛 → Describe problema
   ↓
Widget → Captura screenshot + contexto
   ↓
Backend → Procesa reporte
   ├→ Sentry (stack trace)
   ├→ LogRocket (session URL)
   └→ Supabase (registro centralizado)
```

---

## 🛠️ Uso Programático

### Validar servicios

```python
from watchbug import Watchbug

watchbug = Watchbug()

# Verificar si está habilitado
if watchbug.is_enabled():
    print("✓ Watchbug activo")

# Validar configuración
results = watchbug.check_all(online=False)
for service, result in results.items():
    if result.is_valid():
        print(f"✓ {service} OK")
    else:
        print(f"✗ {service}: {result.message}")
```

### Ver servicios activos

```python
for service, config in watchbug.services.items():
    if config['enabled']:
        print(f"✓ {service} activo")
```

---

## 📝 Ejemplo Completo

Ver el archivo `examples/flask_app.py` para un ejemplo completo funcional con:

- Integración de Watchbug
- Rutas de ejemplo
- Dashboard administrativo
- Botones de prueba para generar errores

Ejecutar el ejemplo:

```bash
cd examples
python flask_app.py
```

---

## 🔒 Seguridad

- **NUNCA** subas tu archivo `.env` al repositorio
- El `.env.example` contiene solo placeholders
- **Dashboard** (`WATCHBUG_ADMIN=true`) solo debe activarse en desarrollo
- Las claves de Supabase deben ser del tipo **anon/public** (no service_role)
- El bucket de Supabase debe ser **público** para acceder a screenshots

---

## 📚 Comandos CLI

```bash
# Ver ayuda
watchbug --help

# Validar configuración (solo formato)
watchbug check

# Ver estado de servicios
watchbug status

# Probar conectividad real
watchbug check --online

# Validar servicio específico
watchbug check sentry
watchbug check logrocket
watchbug check supabase
```

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/mi-feature`)
3. Commit tus cambios (`git commit -m 'Agrega mi feature'`)
4. Push a la rama (`git push origin feature/mi-feature`)
5. Abre un Pull Request

---

## 📄 Licencia

MIT License - Ver archivo [LICENSE](LICENSE) para más detalles.

### 5. Probar la Demo

```bash
# Ejecutar aplicación de ejemplo
python examples/flask_app.py

# Abre http://localhost:5000 en tu navegador
```

La demo incluye botones para generar errores de prueba y ver cómo Watchbug los captura automáticamente.

## 🏗️ Estado del Proyecto

### ✅ Milestone 1: Sistema de Configuración (COMPLETADO)

- [x] Estructura de paquete Python instalable
- [x] Carga de configuración desde `.env`
- [x] Validación de formato para Sentry DSN, LogRocket ID, Supabase credentials
- [x] CLI para diagnóstico (`watchbug check`, `watchbug status`)
- [x] Auto-detección inteligente de servicios habilitados
- [x] Degradación silenciosa si la configuración es inválida
- [x] Soporte para servicios independientes (cualquier combinación funciona)

### ✅ Milestone 2: Widget Frontend (COMPLETADO)

- [x] Botón flotante de reporte de bugs con UI completa
- [x] Captura de pantalla del DOM con html2canvas
- [x] Interceptores de errores:
  - [x] `window.onerror` (errores globales de JavaScript)
  - [x] `unhandledrejection` (promesas rechazadas)
  - [x] `console.error` (errores de consola)
  - [x] `fetch` (peticiones HTTP fallidas)
  - [x] `XMLHttpRequest` (peticiones XHR fallidas)
- [x] Extracción de IDs externos (Sentry eventId, LogRocket sessionURL)
- [x] Sistema de inyección de widget con `get_script_tag()`
- [x] API endpoints para Flask, Django y FastAPI
- [x] Formulario de reporte con comentario del usuario
- [x] Aplicación de demostración con Flask

### 🚧 Próximos Milestones
- [ ] Cliente de Supabase en Python
- [ ] Subida de capturas al Storage
- [ ] Almacenamiento de metadatos en tablas
- [ ] Tests de conectividad online (implementar TODOs en `checks.py`)

**Milestone 4: Conectores de Sentry y LogRocket**
- [ ] Extracción automática de `eventId` de Sentry
- [ ] Extracción de `sessionURL` de LogRocket
- [ ] Vinculación de datos entre servicios

**Milestone 5: Middleware para Frameworks**
- [ ] Adaptador para Django
- [ ] Adaptador para Flask
- [ ] Adaptador para FastAPI
- [ ] Inyección automática de script en HTML

## 🧪 Validación y Health Checks

Watchbug incluye un robusto sistema de validación en dos niveles:

### Validación Offline (Sin Credenciales Reales)

Valida el **formato** de las credenciales sin hacer llamadas de red:

- **Sentry DSN**: Verifica estructura `https://<key>@<org>.ingest.sentry.io/<project>`
- **LogRocket ID**: Verifica formato `organization-slug/app-slug`
- **Supabase**: Verifica formato de URL y que la key sea un JWT válido

### Validación Online (TODO: Milestone 3)

Prueba **conectividad real** con los servicios:

- Sentry: Envía evento de prueba
- LogRocket: Verifica existencia del proyecto
- Supabase: Intenta autenticación o query simple

## 📚 Arquitectura

```
watchbug/
├── __init__.py           # API pública
├── core.py               # Clase principal Watchbug
├── checks.py             # Validadores y health checks
├── cli.py                # Interfaz de línea de comandos
├── api.py                # Endpoints para frameworks web
└── static/
    └── watchbug-widget.js  # Widget JavaScript del frontend

examples/
└── flask_app.py          # Aplicación de demostración
```

### Componentes Principales

**Frontend (JavaScript)**
- **Widget UI**: Botón flotante + diálogo de reporte
- **Interceptores**: Captura automática de errores (JS, consola, red)
- **Screenshot**: Captura visual del DOM con html2canvas
- **Integración**: Extrae IDs de Sentry y LogRocket

**Backend (Python)**
- **`Watchbug`**: Orquestador principal y gestor de configuración
- **`ReportHandler`**: Procesa reportes del frontend
- **`BugReport`**: Estructura de datos del reporte
- **Framework adapters**: Flask, Django, FastAPI

### Flujo de Datos

```
Usuario → Genera Error → Interceptor → Estado del Widget
                ↓
         Click en Botón 🐛
                ↓
   Captura Screenshot + Recopila Contexto
                ↓
         Envía FormData al Backend
                ↓
    ReportHandler procesa y almacena
                ↓
  [Sentry] + [LogRocket] + [Supabase*]
  
  * Supabase = Milestone 3
```

**`Watchbug`**: Clase principal que orquesta todo el sistema
- Carga configuración desde `.env`
- Auto-detecta servicios habilitados
- Proporciona health checks
- Genera script tag para frontend (Milestone 2)

**`ServiceStatus`**: Enum con estados posibles de un servicio
- `NOT_CONFIGURED`: Sin credenciales
- `INVALID_FORMAT`: Formato inválido
- `VALID_FORMAT`: Validación offline OK
- `CONNECTED`: Test online exitoso
- `CONNECTION_FAILED`: Error de conectividad
- `DISABLED`: Desactivado explícitamente

**`ValidationResult`**: Resultado de una validación
- `status`: ServiceStatus
- `message`: Mensaje descriptivo (con guías educativas si falla)
- `details`: Información adicional (project refs, previews, etc.)

## 🎓 Mensajes Educativos

Cuando un servicio no está configurado o tiene errores, Watchbug proporciona mensajes **educativos** que guían al usuario:

```
Sentry DSN no configurado. Para obtener tu DSN:
  1. Ve a https://sentry.io/settings/projects/
  2. Selecciona tu proyecto
  3. Copia el DSN desde 'Client Keys (DSN)'
  4. Añade SENTRY_DSN=<tu_dsn> a tu archivo .env
```

## 🔒 Seguridad

- Las credenciales se cargan **solo desde variables de entorno**
- Los previews de keys muestran solo los primeros 20-30 caracteres
- El `.env` está en `.gitignore` por defecto (no se versiona)
- Degradación silenciosa: errores de config no rompen la aplicación

## 🤝 Contribuir

El proyecto está en desarrollo activo. Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**rafseggom** - [GitHub](https://github.com/rafseggom)

---

**Estado**: 🚀 Milestone 2 completado - Widget Frontend operativo  
**Próximo paso**: Milestone 3 - Integración con Supabase

### ✨ Nuevo en Milestone 2

- 🎨 **Widget JavaScript completo** con botón flotante y diálogo de reporte
- 📸 **Captura de pantalla automática** del DOM usando html2canvas
- 🔍 **Interceptores de errores** para JavaScript, consola, fetch y XHR
- 🔗 **Extracción de IDs** de Sentry y LogRocket para vincular servicios
- 🌐 **API endpoints** listos para Flask, Django y FastAPI
- 🎭 **Demo interactiva** en `examples/flask_app.py`

**Prueba ahora:**
```bash
python examples/flask_app.py
# Abre http://localhost:5000
```
