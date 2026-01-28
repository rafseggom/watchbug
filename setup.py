from setuptools import setup, find_packages

setup(
    name="watchbug",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sentry-sdk",
        "python-dotenv",
    ],
    author="rafseggom",
    description="Herramienta de reporte de bugs centralizada para usuarios pilotos",
)