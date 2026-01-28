# Watchbug - Ejemplos de Integración

Esta carpeta contiene ejemplos de cómo integrar Watchbug en diferentes frameworks web.

## 📁 Ejemplos Disponibles

### `flask_app.py` - Aplicación Flask Completa

Una demo interactiva que muestra todas las capacidades de Watchbug:

**Características:**
- ✅ Widget flotante de reporte de bugs
- ✅ Interceptores de errores en acción
- ✅ Captura de screenshots
- ✅ Botones para generar errores de prueba
- ✅ Integración con Sentry, LogRocket y Supabase

**Cómo ejecutar:**
```bash
# Desde la raíz del proyecto
python examples/flask_app.py

# Abre http://localhost:5000 en tu navegador
```

**Qué probar:**
1. Haz clic en los botones para generar diferentes tipos de errores
2. Observa cómo el widget captura automáticamente los errores
3. Haz clic en el botón flotante 🐛 para abrir el formulario
4. Describe el problema y envía el reporte
5. Revisa la consola del servidor para ver los logs del reporte

---

## 🚀 Otros Frameworks (Próximamente)

### Django

```python
# En tu urls.py
from watchbug import Watchbug
from watchbug.api import create_django_view

watchbug = Watchbug()

urlpatterns = [
    path('watchbug/report/', create_django_view(watchbug)),
]
```

### FastAPI

```python
from fastapi import FastAPI
from watchbug import Watchbug
from watchbug.api import create_fastapi_endpoint

app = FastAPI()
watchbug = Watchbug()

app.post('/watchbug/report')(create_fastapi_endpoint(watchbug))
```

---

## 📝 Notas

- Asegúrate de tener configurado tu archivo `.env` antes de ejecutar los ejemplos
- Los reportes actualmente solo se loggean en consola (Milestone 2)
- La integración con Supabase para almacenamiento estará disponible en Milestone 3
