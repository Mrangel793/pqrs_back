"""
Script de prueba rápida para verificar configuración.

Ejecutar: python test_connection.py
"""

import sys
from pathlib import Path


def test_imports():
    """Verificar que se pueden importar los módulos necesarios"""
    print("🔍 Verificando imports...")
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import pyodbc
        print("  ✅ FastAPI instalado")
        print("  ✅ SQLAlchemy instalado")
        print("  ✅ Pydantic instalado")
        print("  ✅ PyODBC instalado")
        return True
    except ImportError as e:
        print(f"  ❌ Error importando módulo: {str(e)}")
        print("  Ejecuta: pip install -r requirements.txt")
        return False


def test_env_file():
    """Verificar que existe el archivo .env"""
    print("\n🔍 Verificando archivo .env...")
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ Archivo .env encontrado")
        return True
    else:
        print("  ❌ Archivo .env no encontrado")
        print("  Ejecuta: copy .env.example .env")
        return False


def test_config():
    """Verificar configuración"""
    print("\n🔍 Verificando configuración...")
    try:
        from app.config import settings
        print(f"  ✅ APP_NAME: {settings.APP_NAME}")
        print(f"  ✅ DEBUG: {settings.DEBUG}")

        # Verificar DATABASE_URL (sin mostrar contraseña)
        if settings.DATABASE_URL:
            db_url_safe = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else "***"
            print(f"  ✅ DATABASE_URL configurado: ...@{db_url_safe}")
        else:
            print("  ❌ DATABASE_URL no configurado")
            return False

        # Verificar SECRET_KEY
        if settings.SECRET_KEY and settings.SECRET_KEY != "tu-secret-key-segura":
            print("  ✅ SECRET_KEY configurado")
        else:
            print("  ⚠️  SECRET_KEY usa valor por defecto (cambiar en producción)")

        # Verificar CORS
        print(f"  ✅ CORS Origins: {settings.cors_origins_list}")

        return True
    except Exception as e:
        print(f"  ❌ Error cargando configuración: {str(e)}")
        return False


def test_database():
    """Verificar conexión a base de datos"""
    print("\n🔍 Verificando conexión a base de datos...")
    try:
        from app.database import verify_connection
        if verify_connection():
            print("  ✅ Conexión a base de datos exitosa")
            return True
        else:
            print("  ❌ No se pudo conectar a la base de datos")
            print("  Verifica:")
            print("    - SQL Server está ejecutándose")
            print("    - Credenciales correctas en .env")
            print("    - ODBC Driver 17 instalado")
            return False
    except Exception as e:
        print(f"  ❌ Error verificando base de datos: {str(e)}")
        return False


def test_tables():
    """Verificar que existen las tablas"""
    print("\n🔍 Verificando tablas en base de datos...")
    try:
        from app.database import engine
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = ['usuarios', 'casos', 'escalamientos', 'adjuntos', 'configuracion', 'auditoria']

        if not tables:
            print("  ⚠️  No hay tablas en la base de datos")
            print("  Ejecuta: python create_tables.py")
            return False

        print(f"  📊 Tablas encontradas: {len(tables)}")
        for table in expected_tables:
            if table in tables:
                print(f"    ✅ {table}")
            else:
                print(f"    ❌ {table} (faltante)")

        return len([t for t in expected_tables if t in tables]) == len(expected_tables)

    except Exception as e:
        print(f"  ⚠️  No se pudieron verificar las tablas: {str(e)}")
        return False


def test_upload_dir():
    """Verificar directorio de uploads"""
    print("\n🔍 Verificando directorio de uploads...")
    upload_dir = Path("./uploads")
    if upload_dir.exists():
        print(f"  ✅ Directorio uploads existe")
        return True
    else:
        print(f"  ❌ Directorio uploads no existe")
        return False


def main():
    """Ejecutar todas las pruebas"""
    print("=" * 70)
    print("  SISTEMA PQR - VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 70)

    results = {
        "Imports": test_imports(),
        "Archivo .env": test_env_file(),
        "Configuración": test_config(),
        "Base de datos": test_database(),
        "Tablas": test_tables(),
        "Directorio uploads": test_upload_dir()
    }

    print("\n" + "=" * 70)
    print("  RESUMEN")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test}")

    print(f"\n  Total: {passed}/{total} pruebas pasadas")

    if passed == total:
        print("\n  🎉 ¡Todo está configurado correctamente!")
        print("  Puedes iniciar el servidor con: uvicorn app.main:app --reload")
    else:
        print("\n  ⚠️  Hay problemas de configuración que resolver")
        print("  Revisa los mensajes de error arriba")

    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
