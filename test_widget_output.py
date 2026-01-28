#!/usr/bin/env python
"""Script para verificar la salida del widget"""
from watchbug import Watchbug
import json

watchbug = Watchbug()
script_tag = watchbug.get_script_tag()

# Extraer el config JSON
import re
config_match = re.search(r'window\.__WATCHBUG_CONFIG__ = ({.*?});', script_tag)
if config_match:
    config = json.loads(config_match.group(1))
    print("✓ Config encontrado:")
    print(json.dumps(config, indent=2))
else:
    print("✗ Config no encontrado")

# Verificar que el widget.js está incluido
if 'createFloatingButton' in script_tag:
    print("\n✓ createFloatingButton está en el widget")
else:
    print("\n✗ createFloatingButton NO está en el widget")

if 'createDashboardButton' in script_tag:
    print("✓ createDashboardButton está en el widget")
else:
    print("✗ createDashboardButton NO está en el widget")

if 'createReportModal' in script_tag:
    print("✓ createReportModal está en el widget")
else:
    print("✗ createReportModal NO está en el widget")

# Ver las últimas líneas del widget para verificar init()
lines = script_tag.split('\n')
print(f"\n📝 Total de líneas generadas: {len(lines)}")
print("\n🔍 Últimas 15 líneas del script:")
for i, line in enumerate(lines[-15:], start=len(lines)-14):
    print(f"{i:3d}: {line}")
