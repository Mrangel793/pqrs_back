"""
Script para crear las tablas de la base de datos.

Ejecutar este script después de configurar el .env con las credenciales de SQL Server.

Uso:
    python create_tables.py
"""

from app.database import engine, Base, verify_connection
from app.models.models import (
    Usuario,
    Caso,
    Escalamiento,
    Adjunto,
    Configuracion,
    Auditoria
)


def create_tables():
    """Crear todas las tablas en la base de datos"""
    print("🔧 Iniciando creación de tablas...")

    # Verificar conexión
    print("\n📊 Verificando conexión a base de datos...")
    if not verify_connection():
        print("❌ Error: No se pudo conectar a la base de datos")
        print("Verifica tu configuración en el archivo .env")
        return False

    print("✅ Conexión exitosa")

    # Crear tablas
    print("\n📝 Creando tablas...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente:")
        print("   - usuarios")
        print("   - casos")
        print("   - escalamientos")
        print("   - adjuntos")
        print("   - configuracion")
        print("   - auditoria")
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {str(e)}")
        return False


def drop_tables():
    """Eliminar todas las tablas (¡CUIDADO!)"""
    print("⚠️  ADVERTENCIA: Esta operación eliminará todas las tablas y sus datos")
    confirm = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ")

    if confirm == "CONFIRMAR":
        print("\n🗑️  Eliminando tablas...")
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ Tablas eliminadas")
            return True
        except Exception as e:
            print(f"❌ Error eliminando tablas: {str(e)}")
            return False
    else:
        print("❌ Operación cancelada")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  SISTEMA PQR - GESTIÓN DE BASE DE DATOS")
    print("=" * 60)

    print("\nOpciones:")
    print("1. Crear tablas")
    print("2. Eliminar tablas (PELIGROSO)")
    print("3. Recrear tablas (Eliminar y crear de nuevo)")

    option = input("\nSelecciona una opción (1-3): ").strip()

    if option == "1":
        create_tables()
    elif option == "2":
        drop_tables()
    elif option == "3":
        if drop_tables():
            create_tables()
    else:
        print("❌ Opción inválida")

    print("\n" + "=" * 60)
