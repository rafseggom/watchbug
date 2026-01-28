"""
Script de demostración de Watchbug
Muestra el uso programático de la librería
"""

from watchbug import Watchbug

def main():
    print("=== Watchbug Demo ===\n")
    
    # Inicializar Watchbug
    watchbug = Watchbug()
    
    # Verificar si está habilitado
    print(f"Sistema habilitado: {watchbug.is_enabled()}\n")
    
    # Validar todos los servicios (offline)
    print("Validando servicios (offline)...")
    results = watchbug.check_all(online=False)
    
    for service_name, result in results.items():
        status_icon = "✓" if result.is_valid() else "✗"
        print(f"{status_icon} {service_name.capitalize()}: {result.status.value}")
        if result.message and not result.is_valid():
            print(f"  → {result.message.split(chr(10))[0]}")  # Primera línea del mensaje
    
    print("\n--- Estado de configuración ---")
    config = watchbug.get_config_status()
    print(f"Master enabled: {config['master_enabled']}")
    
    for service, info in config['services'].items():
        print(f"\n{service.capitalize()}:")
        print(f"  Enabled: {info['enabled']}")
        print(f"  Configured: {info['configured']}")
        if info['validation']:
            print(f"  Status: {info['validation']['status']}")
    
    # Demostrar uso en frameworks web
    print("\n--- Integración con frameworks web ---")
    script_tag = watchbug.get_script_tag()
    if script_tag:
        print("Script tag generado (listo para inyectar en HTML)")
    else:
        print("Script tag vacío (Watchbug desactivado o pendiente de implementar)")
    
    print("\n=== Fin de la demo ===")


if __name__ == "__main__":
    main()
