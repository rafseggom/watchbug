-- Watchbug - Schema de Supabase
-- 
-- Este script crea las tablas y estructuras necesarias para almacenar
-- los reportes de bugs en Supabase.

-- ============================================
-- Tabla principal de reportes
-- ============================================

CREATE TABLE IF NOT EXISTS bug_reports (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Información básica
    comment TEXT NOT NULL,
    url TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Contexto del navegador
    user_agent TEXT,
    viewport_width INTEGER,
    viewport_height INTEGER,
    
    -- Errores capturados
    errors JSONB DEFAULT '[]'::jsonb,
    console_errors JSONB DEFAULT '[]'::jsonb,
    network_errors JSONB DEFAULT '[]'::jsonb,
    
    -- Integración con servicios externos
    sentry_event_id TEXT,
    logrocket_session_url TEXT,
    
    -- Archivo de screenshot
    screenshot_url TEXT,
    screenshot_size INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para búsqueda rápida
CREATE INDEX IF NOT EXISTS idx_bug_reports_timestamp ON bug_reports(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_bug_reports_url ON bug_reports(url);
CREATE INDEX IF NOT EXISTS idx_bug_reports_sentry ON bug_reports(sentry_event_id) WHERE sentry_event_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_bug_reports_created ON bug_reports(created_at DESC);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bug_reports_updated_at BEFORE UPDATE
    ON bug_reports FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Configuración de Storage Bucket
-- ============================================
-- 
-- NOTA: Ejecutar esto desde el dashboard de Supabase:
--
-- 1. Ve a Storage en el dashboard de Supabase
-- 2. Crea un nuevo bucket llamado: "watchbug-screenshots"
-- 3. Configuración:
--    - Public: No (privado por defecto)
--    - File size limit: 5MB
--    - Allowed MIME types: image/png
--
-- 4. Policies (RLS):
--    - Permitir INSERT para authenticated/anon users
--    - Permitir SELECT para authenticated users
--
-- O ejecutar SQL:

/*
-- Crear bucket (requiere privilegios de admin)
INSERT INTO storage.buckets (id, name, public)
VALUES ('watchbug-screenshots', 'watchbug-screenshots', false);

-- Policy para permitir upload
CREATE POLICY "Allow upload screenshots"
ON storage.objects FOR INSERT
TO authenticated, anon
WITH CHECK (bucket_id = 'watchbug-screenshots');

-- Policy para permitir lectura (solo usuarios autenticados)
CREATE POLICY "Allow read screenshots"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'watchbug-screenshots');
*/

-- ============================================
-- Vistas útiles
-- ============================================

-- Vista de reportes recientes con conteo de errores
CREATE OR REPLACE VIEW recent_bug_reports AS
SELECT 
    id,
    comment,
    url,
    timestamp,
    jsonb_array_length(COALESCE(errors, '[]'::jsonb)) as error_count,
    jsonb_array_length(COALESCE(console_errors, '[]'::jsonb)) as console_error_count,
    jsonb_array_length(COALESCE(network_errors, '[]'::jsonb)) as network_error_count,
    sentry_event_id,
    logrocket_session_url,
    screenshot_url,
    created_at
FROM bug_reports
ORDER BY created_at DESC
LIMIT 100;

-- ============================================
-- Funciones de utilidad
-- ============================================

-- Función para obtener estadísticas de reportes
CREATE OR REPLACE FUNCTION get_bug_report_stats()
RETURNS TABLE (
    total_reports BIGINT,
    reports_today BIGINT,
    reports_this_week BIGINT,
    reports_with_screenshots BIGINT,
    reports_with_sentry BIGINT,
    reports_with_logrocket BIGINT,
    avg_errors_per_report NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_reports,
        COUNT(*) FILTER (WHERE timestamp > NOW() - INTERVAL '1 day')::BIGINT as reports_today,
        COUNT(*) FILTER (WHERE timestamp > NOW() - INTERVAL '7 days')::BIGINT as reports_this_week,
        COUNT(*) FILTER (WHERE screenshot_url IS NOT NULL)::BIGINT as reports_with_screenshots,
        COUNT(*) FILTER (WHERE sentry_event_id IS NOT NULL)::BIGINT as reports_with_sentry,
        COUNT(*) FILTER (WHERE logrocket_session_url IS NOT NULL)::BIGINT as reports_with_logrocket,
        AVG(jsonb_array_length(COALESCE(errors, '[]'::jsonb)))::NUMERIC as avg_errors_per_report
    FROM bug_reports;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Row Level Security (RLS)
-- ============================================

-- Habilitar RLS en la tabla
ALTER TABLE bug_reports ENABLE ROW LEVEL SECURITY;

-- Policy: Permitir INSERT a usuarios anónimos (desde el widget)
CREATE POLICY "Allow anonymous insert"
ON bug_reports FOR INSERT
TO anon
WITH CHECK (true);

-- Policy: Permitir SELECT solo a usuarios autenticados
CREATE POLICY "Allow authenticated select"
ON bug_reports FOR SELECT
TO authenticated
USING (true);

-- Policy: Permitir UPDATE/DELETE solo a usuarios autenticados
CREATE POLICY "Allow authenticated update"
ON bug_reports FOR UPDATE
TO authenticated
USING (true);

CREATE POLICY "Allow authenticated delete"
ON bug_reports FOR DELETE
TO authenticated
USING (true);

-- ============================================
-- Datos de ejemplo (opcional, para testing)
-- ============================================

-- Comentar estas líneas en producción
/*
INSERT INTO bug_reports (comment, url, user_agent, viewport_width, viewport_height, errors, console_errors)
VALUES 
(
    'El botón de guardar no funciona después de llenar el formulario',
    'https://miapp.com/dashboard',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    1920,
    1080,
    '[{"type": "javascript", "message": "Cannot read property of undefined"}]'::jsonb,
    '[{"message": "API timeout error"}]'::jsonb
);
*/
