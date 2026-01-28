# 🐛 Watchbug - Sistema de Reporte de Bugs Unificado

**Watchbug** es una herramienta que cierra el "Abismo de Información" entre usuarios piloto (no técnicos) y desarrolladores. Centraliza información de errores desde múltiples fuentes (Sentry, LogRocket, capturas de pantalla) en un solo reporte estructurado.

## 🎯 El Problema

Cuando un usuario piloto encuentra un error, suele decir:
- _"Le di al botón y no pasó nada"_
- _"La pantalla se quedó en blanco"_

Para un desarrollador, eso es **ruido**. Necesitamos:
- **Stacktrace** (Sentry)
- **Sesión de usuario** (LogRocket)
- **Captura de pantalla** del estado visual
- **Comentario** que explique la intención del usuario

## 💡 La Solución

Watchbug orquesta la recolección de estas "piezas del puzzle" y las unifica en un solo registro, opcionalmente almacenándolas en Supabase para consulta centralizada.

### Modos de Operación

Watchbug es flexible y puede funcionar con **cualquier combinación de servicios**:

- **🔥 Modo Completo**: Supabase + Sentry + LogRocket  
  Almacenamiento centralizado con integraciones completas
  
- **⚡ Modo Lightweight**: Solo Sentry + LogRocket  
  Sin base de datos propia, los errores van directamente a cada servicio
  
- **🎯 Modo Personalizado**: Cualquier combinación que necesites

## 🚀 Inicio Rápido

### 1. Instalación

```bash
pip install watchbug
```

### 2. Configuración

Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
# Edita .env con tus credenciales
```

Variables disponibles en `.env`:

```bash
# Control maestro
WATCHBUG_ENABLED=True

# Sentry (opcional)
SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>
# SENTRY_ENABLED=True  # Auto-detectado si hay DSN

# LogRocket (opcional)
LOGROCKET_ID=organization/app-name
# LOGROCKET_ENABLED=True  # Auto-detectado si hay ID

# Supabase (opcional)
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_KEY=eyJ...  # Anon/public key
# SUPABASE_ENABLED=True  # Auto-detectado si hay URL y Key
```

### 3. Validar Configuración

Watchbug incluye un CLI para validar tu configuración:

```bash
# Validación rápida (solo formato)
watchbug check

# Ver estado actual
watchbug status

# Probar conectividad (requiere credenciales reales)
watchbug check --online

# Validar un servicio específico
watchbug check sentry
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

### 4. Uso Programático

#### Uso Básico

```python
from watchbug import Watchbug

# Inicializar (carga automáticamente desde .env)
watchbug = Watchbug()

# Verificar si está habilitado
if watchbug.is_enabled():
    print("Watchbug activo con servicios:", 
          [s for s, cfg in watchbug.services.items() if cfg['enabled']])

# Validar servicios
results = watchbug.check_all(online=False)
for service, result in results.items():
    if result.is_valid():
        print(f"✓ {service} configurado correctamente")
    else:
        print(f"✗ {service}: {result.message}")
```

#### Integración con Flask

```python
from flask import Flask
from watchbug import Watchbug
from watchbug.api import create_flask_endpoint

app = Flask(__name__)
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

#### Integración con Django

```python
# En urls.py
from django.urls import path
from watchbug import Watchbug
from watchbug.api import create_django_view

watchbug = Watchbug()

urlpatterns = [
    path('watchbug/report/', create_django_view(watchbug)),
]

# En tu vista
def my_view(request):
    script_tag = watchbug.get_script_tag(api_endpoint='/watchbug/report/')
    return render(request, 'index.html', {'watchbug_script': script_tag})
```

#### Integración con FastAPI

```python
from fastapi import FastAPI, Request
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
    return f"<html><body>{script_tag}</body></html>"
```

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
