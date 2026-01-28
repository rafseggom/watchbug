from setuptools import setup, find_packages

setup(
    name="watchbug",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "watchbug": ["static/*.js"],
    },
    install_requires=[
        "sentry-sdk",
        "python-dotenv",
        "postgrest>=2.0.0",  # Cliente PostgreSQL de Supabase (sin pyiceberg)
        "httpx>=0.26.0",     # Para llamadas HTTP a Supabase
        "supabase>=2.0.0",  # Cliente oficial de Supabase
        "pydantic>=2.0.0",   # Para validación de datos
    ],
    author="rafseggom",
    description="Herramienta de reporte de bugs centralizada para usuarios pilotos",
    entry_points={
        "console_scripts": [
            "watchbug=watchbug.cli:main",
        ],
    },
)