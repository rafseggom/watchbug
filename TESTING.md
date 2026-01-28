# 🧪 Guía Completa de Pruebas - Watchbug

Esta guía te llevará paso a paso para probar **todas las funcionalidades** de Watchbug.

---

## 📋 Checklist Pre-Pruebas

Antes de empezar, asegúrate de tener:

- [x] **Servidor Flask corriendo** en `localhost:5000`
- [ ] **Bucket de Supabase** creado y configurado como público
- [ ] **Credenciales** en `.env` correctas

---

## 1️⃣ Configurar Supabase Storage (CRÍTICO para screenshots)

### Paso 1: Crear el Bucket

1. Ve a **https://supabase.com/dashboard**
2. Selecciona tu proyecto
3. En el menú lateral: **Storage** > **Create a new bucket**
4. Nombre del bucket: `watchbug-screenshots`
5. **IMPORTANTE**: Marca la casilla **"Public bucket"** ✓
6. Click en **Create bucket**

### Paso 2: Verificar que es Público

1. En Storage, click en el bucket `watchbug-screenshots`
2. Ve a **Policies** (en la parte superior)
3. Debería aparecer algo como:
   ```
   Policy name: Public Access
   Definition: Allows public access to objects
   ```
4. Si no hay política, créala:
   - Click en **New Policy**
   - Selecciona **For full customization**
   - Policy name: `Public Access`
   - Definition:
     ```sql
     ((bucket_id = 'watchbug-screenshots'::text) AND (auth.role() = 'anon'::text))
     ```
   - Allowed operations: SELECT ✓

### Paso 3: Probar Acceso Público

1. Sube un archivo de prueba al bucket manualmente
2. Copia la URL pública (debería ser algo como):
   ```
   https://aumwkipjuzhvnywajhsu.supabase.co/storage/v1/object/public/watchbug-screenshots/test.png
   ```
3. Pega esa URL en tu navegador
4. **Debería mostrar la imagen** sin pedir autenticación

---

## 2️⃣ Verificar Configuración General

### Comprobar que todo está activo

```bash
cd e:\Proyectos Github\watchbug
watchbug status
```

**Salida esperada:**
```
🔍 Estado de Watchbug
==================================================
✓ Watchbug HABILITADO

Servicios configurados:
  ✓ Sentry       - Activo
  ✓ LogRocket    - Activo
  ✓ Supabase     - Activo

Dashboard: HABILITADO (solo desarrollo)
```

### Probar conectividad real

```bash
watchbug check --online
```

Esto verificará:
- ✓ Sentry DSN es válido y el proyecto existe
- ✓ LogRocket ID es válido
- ✓ Supabase responde correctamente

---

## 3️⃣ Prueba Básica del Widget

### Paso 1: Acceder a la Demo

1. Abre **http://localhost:5000** en tu navegador
2. Abre las **herramientas de desarrollador** (F12)
3. Ve a la pestaña **Console**

### Paso 2: Verificar que el Widget está Activo

En la consola deberías ver:
```
[Watchbug] Inicializando widget...
[Watchbug] Widget listo ✓
[Watchbug] Servicios activos: {sentry: true, logrocket: true, supabase: true}
[Watchbug] Dashboard de administración habilitado en /watchbug/dashboard
```

### Paso 3: Verificar Botones Flotantes

Deberías ver en la esquina inferior derecha:
- **🐛** (botón rojo) - Reportar bug
- **📊** (botón morado) - Dashboard

---

## 4️⃣ Prueba Completa de Captura de Errores

### Test 1: Error de JavaScript

1. En `localhost:5000`, click en **"Error de JavaScript"**
2. En la consola verás:
   ```
   Uncaught Error: Este es un error de JavaScript provocado
   ```
3. **Sentry** debería capturar este error automáticamente

### Test 2: Error de Consola

1. Click en **"Error de Consola"**
2. En la consola verás:
   ```
   [Watchbug] Error de consola capturado
   ```

### Test 3: Error de Red (404)

1. Click en **"Error de Red (404)"**
2. En la pestaña **Network** de las dev tools verás un request fallido
3. En la consola:
   ```
   [Watchbug] Error de red capturado
   ```

---

## 5️⃣ Enviar un Reporte Completo

### Paso 1: Provocar Errores

1. Click en **"Error de JavaScript"**
2. Click en **"Error de Consola"**
3. Espera 2 segundos

### Paso 2: Abrir Modal de Reporte

1. Click en el botón **🐛** (esquina inferior derecha)
2. Se abre un modal blanco con el título "🐛 Reportar Problema"

### Paso 3: Describir el Problema

En el textarea escribe:
```
Probando el sistema completo. La página mostró errores al hacer click en los botones de prueba.
```

### Paso 4: Enviar

1. Click en **"Enviar Reporte"**
2. Verás mensajes de progreso:
   ```
   Capturando información... 📸
   Capturando pantalla...
   Enviando reporte...
   ```
3. Mensaje final:
   ```
   ✅ Reporte enviado correctamente. ¡Gracias!
   ```
4. El modal se cierra automáticamente después de 2 segundos

### Paso 5: Verificar en la Consola del Servidor

En la terminal donde corre Flask verás:
```
============================================================
🐛 NUEVO REPORTE DE BUG RECIBIDO
============================================================

📍 URL: http://localhost:5000/
💬 Comentario: Probando el sistema completo...
❌ Errores JS: 1 | 📝 Consola: 1 | 🌐 Red: 1
📸 Screenshot: ✓ Capturado
   💾 Supabase: Guardando...
   💾 Supabase: ✓ Guardado con ID: abc-123-def
   🔥 Sentry ID: 1234567890abcdef
   📹 LogRocket: https://app.logrocket.com/...
```

---

## 6️⃣ Verificar en Sentry

### Paso 1: Acceder a Sentry

1. Ve a **https://sentry.io**
2. Login con tu cuenta
3. Selecciona tu proyecto

### Paso 2: Ver el Error

1. En el dashboard principal verás: **"Error: Este es un error de JavaScript provocado"**
2. Click en el error para ver detalles:
   - **Stack trace** completo
   - **Breadcrumbs** (acciones previas)
   - **User Agent** y navegador
   - **URL** donde ocurrió
   - **Contexto adicional** enviado por Watchbug

### Paso 3: Verificar Contexto de Watchbug

En la pestaña **Additional Data** o **Context** deberías ver:
- `watchbug_comment`: El comentario del usuario
- `watchbug_console_errors`: Errores de consola capturados
- `watchbug_network_errors`: Requests fallidos

---

## 7️⃣ Verificar en LogRocket

### Paso 1: Acceder a LogRocket

1. Ve a **https://app.logrocket.com**
2. Login con tu cuenta
3. Selecciona tu app: **mpnrbc/watchbug**

### Paso 2: Ver tu Sesión

1. Verás una lista de sesiones recientes
2. La tuya debería estar marcada con:
   - URL: `localhost:5000`
   - Timestamp: Hace unos minutos
3. Click para abrir la sesión

### Paso 3: Reproducir lo que Hiciste

LogRocket reproduce tu sesión completa:
- **Video** de lo que viste en pantalla
- **Clicks** en los botones
- **Consola** con todos los logs
- **Red** con todos los requests
- **Errores** resaltados en rojo

---

## 8️⃣ Verificar en Supabase

### Paso 1: Acceder a la Base de Datos

1. Ve a **https://supabase.com/dashboard**
2. Selecciona tu proyecto
3. Ve a **Table Editor** > **bug_reports**

### Paso 2: Ver el Reporte

Deberías ver una fila nueva con:
- `id`: UUID único
- `created_at`: Timestamp de hace unos minutos
- `comment`: Tu comentario
- `url`: `http://localhost:5000/`
- `errors`: Array JSON con el error de JavaScript
- `console_errors`: Array JSON con errores de consola
- `network_errors`: Array JSON con requests fallidos
- `sentry_event_id`: ID del evento en Sentry
- `logrocket_session_url`: URL de la sesión en LogRocket
- `screenshot_url`: URL pública de la captura

### Paso 3: Ver el Screenshot

1. Copia el valor de `screenshot_url`
2. Pégalo en tu navegador
3. **Debería mostrar la captura** de pantalla del momento exacto

Si la imagen **NO** se muestra:
- ❌ El bucket no es público
- ❌ El bucket no existe
- ❌ No tienes permisos de Storage en tu plan de Supabase

---

## 9️⃣ Usar el Dashboard de Watchbug

### Paso 1: Acceder al Dashboard

1. En `localhost:5000`, click en el botón **📊** (morado)
2. O ve directo a: **http://localhost:5000/watchbug/dashboard**

### Paso 2: Explorar el Dashboard

Deberías ver:

**Estadísticas (3 cards):**
- Total de Reportes
- Reportes de Hoy
- Reportes con Screenshot

**Links a Servicios (3 cards):**
- **Sentry** - Click en "Ver Dashboard" → Abre Sentry.io
- **LogRocket** - Click en "Ver Dashboard" → Abre LogRocket
- **Supabase** - Click en "Ver Dashboard" → Abre Supabase

**Tabla de Reportes:**
- Lista de todos los reportes ordenados por fecha
- Columnas: Fecha, URL, Comentario, Errores, Screenshot
- Click en cualquier fila → Modal con detalles completos

### Paso 3: Filtrar Reportes

Prueba los filtros:
- **Buscar**: Escribe parte de la URL o comentario
- **Dropdown**: 
  - "Con errores"
  - "Con screenshot"
  - "Vinculado a Sentry"

### Paso 4: Ver Detalles de un Reporte

1. Click en cualquier reporte de la tabla
2. Se abre un modal con:
   - Información general (URL, comentario, viewport)
   - Errores JavaScript (si los hay)
   - Errores de consola
   - Errores de red
   - Screenshot (imagen)
   - Event ID de Sentry
   - Link a sesión de LogRocket

---

## 🔟 Prueba de Estrés (Opcional)

### Generar Múltiples Reportes

```javascript
// Ejecuta esto en la consola del navegador (F12)
for (let i = 0; i < 5; i++) {
    setTimeout(() => {
        throw new Error(`Error de prueba ${i+1}`);
    }, i * 2000);
}
```

Luego reporta con diferentes comentarios:
- "Primer error de la serie"
- "Segundo error"
- etc.

Ve al dashboard y verifica que todos aparecen.

---

## ✅ Checklist Final de Verificación

### Frontend
- [x] Botón 🐛 aparece en esquina inferior derecha
- [x] Botón 📊 aparece al lado del 🐛
- [x] Modal de reporte se abre al hacer click
- [x] Screenshot se captura correctamente
- [x] Modal se cierra tras enviar

### Backend
- [x] Endpoint `/watchbug/report` recibe el POST
- [x] Logs aparecen en consola del servidor
- [x] Reporte se guarda en Supabase
- [x] Screenshot se sube al bucket

### Sentry
- [x] Error aparece en Issues
- [x] Stack trace es correcto
- [x] Contexto de Watchbug está presente
- [x] Event ID coincide con Supabase

### LogRocket
- [x] Sesión se graba automáticamente
- [x] Se puede reproducir la sesión
- [x] Errores están resaltados
- [x] URL de sesión coincide con Supabase

### Supabase
- [x] Fila nueva en tabla `bug_reports`
- [x] Todos los campos están poblados
- [x] Screenshot URL es accesible públicamente
- [x] JSON de errores está bien formateado

### Dashboard
- [x] Estadísticas se actualizan
- [x] Links a servicios funcionan
- [x] Tabla muestra todos los reportes
- [x] Filtros funcionan correctamente
- [x] Modal de detalles muestra toda la info

---

## 🐛 Troubleshooting

### El screenshot no se sube a Supabase

**Problema:** `screenshot_url` está NULL en la base de datos

**Soluciones:**
1. Verifica que el bucket `watchbug-screenshots` existe
2. Verifica que el bucket es **público**
3. Revisa los logs del servidor Flask para ver el error exacto
4. Prueba subir un archivo manualmente al bucket

### Los botones no aparecen

**Problema:** No veo 🐛 ni 📊

**Soluciones:**
1. Recarga la página con Ctrl+F5 (forzar recarga)
2. Revisa la consola del navegador por errores de JavaScript
3. Verifica que `WATCHBUG_ADMIN=true` en `.env`
4. Reinicia el servidor Flask

### El dashboard está vacío

**Problema:** No hay reportes en la tabla

**Soluciones:**
1. Envía un reporte primero desde la página principal
2. Verifica conexión a Supabase
3. Revisa la consola del navegador (F12) por errores de API
4. Comprueba que la tabla `bug_reports` existe en Supabase

### Timeout conectando a Supabase

**Problema:** "The read operation timed out"

**Soluciones:**
1. Verifica tu conexión a internet
2. Comprueba que el proyecto de Supabase no está pausado
3. Aumenta el timeout en `dashboard.py` (actualmente 5 segundos)
4. Prueba con `watchbug check --online` para verificar conectividad

---

## 📊 Métricas de Éxito

Una prueba exitosa debe cumplir:

✅ **100% de servicios activos** (Sentry, LogRocket, Supabase)  
✅ **0 errores** en consola del navegador (aparte de los provocados)  
✅ **1 reporte** guardado en Supabase tras enviar  
✅ **1 evento** creado en Sentry  
✅ **1 sesión** grabada en LogRocket  
✅ **1 screenshot** accesible públicamente  
✅ **Dashboard** muestra el reporte correctamente  

---

## 🎉 ¡Felicidades!

Si todos los pasos funcionan correctamente, **Watchbug está 100% operativo**.

Ahora puedes integrarlo en tu aplicación real y empezar a recibir reportes de bugs con contexto completo de tus usuarios.
