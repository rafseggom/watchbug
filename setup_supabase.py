"""
Script de configuración de Supabase para Watchbug

Este script te guía en la configuración de tu proyecto de Supabase
y crea las tablas necesarias.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_credentials():
    """Verifica que las credenciales de Supabase estén configuradas."""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Credenciales de Supabase no encontradas en .env")
        print("\nPor favor, configura:")
        print("  SUPABASE_URL=https://tu-proyecto.supabase.co")
        print("  SUPABASE_KEY=tu-anon-key")
        return False
    
    print(f"✓ SUPABASE_URL: {url}")
    print(f"✓ SUPABASE_KEY: {key[:20]}...")
    return True


def test_connection():
    """Prueba la conexión con Supabase."""
    try:
        import httpx
    except ImportError:
        print("❌ httpx no está instalado")
        print("\nInstálalo con: pip install httpx postgrest pydantic")
        return False
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    try:
        # Probar conexión con la API REST
        with httpx.Client() as client:
            response = client.get(
                f"{url}/rest/v1/",
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}"
                },
                timeout=10.0
            )
            response.raise_for_status()
        
        print("\n✓ Cliente de Supabase conectado correctamente")
        return True
    except Exception as e:
        print(f"\n❌ Error conectando con Supabase: {e}")
        return False


def check_table_exists():
    """Verifica si la tabla bug_reports existe."""
    import httpx
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{url}/rest/v1/bug_reports?limit=1",
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}"
                },
                timeout=10.0
            )
            response.raise_for_status()
        
        print("✓ Tabla 'bug_reports' existe")
        return True
    except Exception as e:
        print(f"✗ Tabla 'bug_reports' no existe o no es accesible")
        print(f"  Error: {str(e)[:100]}")
        return False


def check_storage_bucket():
    """Verifica si el bucket de storage existe."""
    import httpx
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    try:
        # Intentar listar archivos del bucket
        with httpx.Client() as client:
            response = client.get(
                f"{url}/storage/v1/object/list/watchbug-screenshots",
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}"
                },
                timeout=10.0
            )
            response.raise_for_status()
        
        print("✓ Bucket 'watchbug-screenshots' existe")
        return True
    except Exception as e:
        print(f"✗ Bucket 'watchbug-screenshots' no existe o no es accesible")
        print(f"  Error: {str(e)[:100]}")
        return False


def create_test_report():
    """Crea un reporte de prueba."""
    import httpx
    
    print("\n📝 Creando reporte de prueba...")
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    try:
        data = {
            'comment': 'Reporte de prueba desde setup_supabase.py',
            'url': 'https://example.com/test',
            'user_agent': 'Watchbug Setup Script',
            'viewport_width': 1920,
            'viewport_height': 1080,
            'errors': [],
            'console_errors': [{'message': 'Test console error'}],
            'network_errors': []
        }
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        with httpx.Client() as client:
            # Insertar reporte
            response = client.post(
                f"{url}/rest/v1/bug_reports",
                json=data,
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
        
        if result and len(result) > 0:
            report_id = result[0]['id']
            print(f"✓ Reporte de prueba creado con ID: {report_id}")
            
            # Eliminar el reporte de prueba
            with httpx.Client() as client:
                response = client.delete(
                    f"{url}/rest/v1/bug_reports?id=eq.{report_id}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
            
            print(f"✓ Reporte de prueba eliminado")
            return True
        else:
            print("✗ No se pudo crear el reporte de prueba")
            return False
            
    except Exception as e:
        print(f"✗ Error creando reporte de prueba: {e}")
        return False


def main():
    """Función principal."""
    print("="*60)
    print("🐛 Watchbug - Configuración de Supabase")
    print("="*60)
    
    # 1. Verificar credenciales
    print("\n1️⃣  Verificando credenciales...")
    if not check_credentials():
        return
    
    # 2. Probar conexión
    print("\n2️⃣  Probando conexión...")
    if not test_connection():
        return
    
    # 3. Verificar tabla
    print("\n3️⃣  Verificando tabla 'bug_reports'...")
    table_exists = check_table_exists()
    
    if not table_exists:
        print("\n❗ La tabla 'bug_reports' no existe.")
        print("\nPara crearla:")
        print("  1. Abre el dashboard de Supabase")
        print("  2. Ve a SQL Editor")
        print("  3. Ejecuta el contenido de: supabase_schema.sql")
        print(f"\nArchivo: {os.path.join(os.getcwd(), 'supabase_schema.sql')}")
        return
    
    # 4. Verificar bucket de storage
    print("\n4️⃣  Verificando bucket de storage...")
    bucket_exists = check_storage_bucket()
    
    if not bucket_exists:
        print("\n❗ El bucket 'watchbug-screenshots' no existe.")
        print("\nPara crearlo:")
        print("  1. Abre el dashboard de Supabase")
        print("  2. Ve a Storage")
        print("  3. Crea un nuevo bucket:")
        print("     - Name: watchbug-screenshots")
        print("     - Public: No (privado)")
        print("     - File size limit: 5MB")
        print("     - Allowed MIME types: image/png")
    
    # 5. Crear reporte de prueba
    if table_exists:
        print("\n5️⃣  Probando inserción de datos...")
        create_test_report()
    
    # Resumen final
    print("\n" + "="*60)
    print("✅ Configuración completada")
    print("="*60)
    
    if table_exists and bucket_exists:
        print("\n🎉 Supabase está listo para usar con Watchbug!")
        print("\nEjecuta la demo para probarlo:")
        print("  python examples/flask_app.py")
    else:
        print("\n⚠️  Completa los pasos pendientes antes de usar Watchbug")
    
    print()


if __name__ == '__main__':
    main()
