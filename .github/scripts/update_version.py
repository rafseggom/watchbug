#!/usr/bin/env python3
"""
Script para actualizar la versión en setup.py y __init__.py
Usado por semantic-release durante el proceso de release
"""
import sys
import re

def update_setup_py(version):
    """Actualiza la versión en setup.py"""
    with open('setup.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar versión
    updated = re.sub(
        r'version\s*=\s*["\'][^"\']+["\']',
        f'version="{version}"',
        content
    )
    
    with open('setup.py', 'w', encoding='utf-8') as f:
        f.write(updated)
    
    print(f"✓ setup.py actualizado a v{version}")

def update_init_py(version):
    """Actualiza la versión en watchbug/__init__.py"""
    try:
        with open('watchbug/__init__.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Si ya existe __version__, reemplazarla
        if '__version__' in content:
            updated = re.sub(
                r'__version__\s*=\s*["\'][^"\']+["\']',
                f'__version__ = "{version}"',
                content
            )
        else:
            # Si no existe, añadirla después de los imports
            lines = content.split('\n')
            # Buscar la última línea de import
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    last_import_idx = i
            
            # Insertar después de los imports
            lines.insert(last_import_idx + 1, f'\n__version__ = "{version}"')
            updated = '\n'.join(lines)
        
        with open('watchbug/__init__.py', 'w', encoding='utf-8') as f:
            f.write(updated)
        
        print(f"✓ watchbug/__init__.py actualizado a v{version}")
    except FileNotFoundError:
        print("⚠ watchbug/__init__.py no encontrado, saltando...")

def main():
    if len(sys.argv) < 2:
        print("Error: Se requiere la versión como argumento")
        print("Uso: update_version.py <version>")
        sys.exit(1)
    
    version = sys.argv[1]
    print(f"\n🔄 Actualizando versión a {version}...\n")
    
    update_setup_py(version)
    update_init_py(version)
    
    print(f"\n✅ Versión actualizada correctamente a {version}\n")

if __name__ == '__main__':
    main()
