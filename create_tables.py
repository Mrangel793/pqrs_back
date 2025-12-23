"""
Script para crear las tablas de la base de datos.

Este script verifica la existencia de cada tabla antes de crearla,
evitando errores si algunas tablas ya existen.

Ejecutar este script después de configurar el .env con las credenciales de SQL Server.

Uso:
    python create_tables.py
"""

from sqlalchemy import inspect, text
from app.database import engine, Base, verify_connection
from app.models.models import (
    # Catálogos
    EstadoCaso,
    Semaforo,
    TipoPDF,
    EstadoEnvio,
    TipoAdjunto,
    TipoAccion,
    # Principales
    Usuario,
    Caso,
    CasoIdentificador,
    Escalamiento,
    Adjunto,
    FuenteCorreo,
    AuditoriaEvento,
    Configuracion,
    LogIngesta,
    Sesion
)


def get_existing_tables():
    """Obtener lista de tablas que ya existen en la base de datos"""
    inspector = inspect(engine)
    return set(inspector.get_table_names())


def create_tables_smart():
    """
    Crear tablas de forma inteligente.
    Solo crea las tablas que no existen, respetando el orden de dependencias.
    """
    print("🔧 Iniciando creación inteligente de tablas...")
    
    # Verificar conexión
    print("\n📊 Verificando conexión a base de datos...")
    if not verify_connection():
        print("❌ Error: No se pudo conectar a la base de datos")
        print("Verifica tu configuración en el archivo .env")
        return False
    
    print("✅ Conexión exitosa")
    
    # Obtener tablas existentes
    print("\n🔍 Verificando tablas existentes...")
    existing_tables = get_existing_tables()
    
    if existing_tables:
        print(f"📋 Se encontraron {len(existing_tables)} tablas existentes:")
        for table in sorted(existing_tables):
            print(f"   ✓ {table}")
    else:
        print("📋 No se encontraron tablas existentes (base de datos vacía)")
    
    # Definir orden de creación (respetando dependencias de foreign keys)
    tables_order = [
        # Primero: Catálogos sin dependencias
        ('tab_estadocaso', EstadoCaso, 'Catálogo de Estados de Caso'),
        ('tab_semaforo', Semaforo, 'Catálogo de Semáforos'),
        ('tab_tipopdf', TipoPDF, 'Catálogo de Tipos de PDF'),
        ('tab_estadoenvio', EstadoEnvio, 'Catálogo de Estados de Envío'),
        ('tab_tipoadjunto', TipoAdjunto, 'Catálogo de Tipos de Adjunto'),
        ('tab_tipoaccion', TipoAccion, 'Catálogo de Tipos de Acción'),
        
        # Segundo: Usuario (sin dependencias de otras tablas principales)
        ('tab_usuario', Usuario, 'Usuarios del Sistema'),
        
        # Tercero: Configuración y LogIngesta (dependen de Usuario)
        ('tab_configuracion', Configuracion, 'Configuración del Sistema'),
        ('tab_logingesta', LogIngesta, 'Logs de Ingesta de Correos'),
        
        # Cuarto: Sesión (depende de Usuario)
        ('tab_sesion', Sesion, 'Sesiones de Usuario'),
        
        # Quinto: Caso (depende de catálogos y Usuario)
        ('tab_caso', Caso, 'Casos (PQR Escaladas)'),
        
        # Sexto: Tablas que dependen de Caso
        ('tab_casoidentificador', CasoIdentificador, 'Identificadores de Caso'),
        ('tab_escalamiento', Escalamiento, 'Escalamientos de Casos'),
        ('tab_adjunto', Adjunto, 'Adjuntos de Casos'),
        ('tab_fuentecorreo', FuenteCorreo, 'Fuentes de Correo'),
        ('tab_auditoriaevento', AuditoriaEvento, 'Eventos de Auditoría'),
    ]
    
    # Crear tablas una por una
    print("\n📝 Creando tablas faltantes...")
    created_count = 0
    skipped_count = 0
    error_count = 0
    
    for table_name, model_class, description in tables_order:
        if table_name in existing_tables:
            print(f"   ⏭️  {table_name:30} - Ya existe (omitiendo)")
            skipped_count += 1
        else:
            try:
                # Crear solo esta tabla
                model_class.__table__.create(bind=engine, checkfirst=True)
                print(f"   ✅ {table_name:30} - Creada ({description})")
                created_count += 1
            except Exception as e:
                print(f"   ❌ {table_name:30} - Error: {str(e)[:60]}")
                error_count += 1
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE CREACIÓN DE TABLAS")
    print("=" * 70)
    print(f"✅ Tablas creadas:    {created_count}")
    print(f"⏭️  Tablas omitidas:   {skipped_count} (ya existían)")
    print(f"❌ Errores:           {error_count}")
    print(f"📋 Total de tablas:   {len(tables_order)}")
    print("=" * 70)
    
    if error_count > 0:
        print("\n⚠️  Hubo errores durante la creación. Revisa los mensajes arriba.")
        return False
    elif created_count > 0:
        print(f"\n🎉 Se crearon {created_count} tablas nuevas exitosamente!")
        
        # Preguntar si desea ejecutar seeds
        print("\n" + "=" * 70)
        print("🌱 DATOS INICIALES (SEEDS)")
        print("=" * 70)
        print("Se recomienda insertar datos iniciales para el correcto funcionamiento:")
        print("  - Catálogos (estados, tipos, semáforos)")
        print("  - Usuarios de prueba")
        print("  - Configuración del sistema")
        print()
        
        run_seeds = input("¿Deseas insertar los datos iniciales ahora? (s/n): ").strip().lower()
        if run_seeds == 's':
            print()
            try:
                from seed_database import seed_all
                seed_all()
            except ImportError:
                print("⚠️  No se encontró el archivo seed_database.py")
                print("   Ejecuta manualmente: python seed_database.py")
            except Exception as e:
                print(f"❌ Error ejecutando seeds: {str(e)}")
        else:
            print("\n💡 Puedes ejecutar las seeds más tarde con: python seed_database.py")
        
        return True
    else:
        print("\n✨ Todas las tablas ya existían. No se creó nada nuevo.")
        
        # Preguntar si desea ejecutar seeds de todas formas
        print("\n💡 ¿Deseas verificar/insertar datos iniciales? (s/n): ", end="")
        run_seeds = input().strip().lower()
        if run_seeds == 's':
            print()
            try:
                from seed_database import seed_all
                seed_all()
            except ImportError:
                print("⚠️  No se encontró el archivo seed_database.py")
            except Exception as e:
                print(f"❌ Error ejecutando seeds: {str(e)}")
        
        return True


def create_all_tables():
    """
    Crear todas las tablas usando el método tradicional de SQLAlchemy.
    Este método crea todas las tablas de una vez.
    """
    print("🔧 Iniciando creación de tablas (método tradicional)...")
    
    # Verificar conexión
    print("\n📊 Verificando conexión a base de datos...")
    if not verify_connection():
        print("❌ Error: No se pudo conectar a la base de datos")
        print("Verifica tu configuración en el archivo .env")
        return False
    
    print("✅ Conexión exitosa")
    
    # Crear tablas
    print("\n📝 Creando todas las tablas...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Proceso completado. Tablas creadas o verificadas:")
        
        # Listar todas las tablas
        tables = [
            "tab_estadocaso", "tab_semaforo", "tab_tipopdf", "tab_estadoenvio",
            "tab_tipoadjunto", "tab_tipoaccion", "tab_usuario", "tab_configuracion",
            "tab_logingesta", "tab_sesion", "tab_caso", "tab_casoidentificador",
            "tab_escalamiento", "tab_adjunto", "tab_fuentecorreo", "tab_auditoriaevento"
        ]
        
        for table in tables:
            print(f"   ✓ {table}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {str(e)}")
        return False


def drop_tables():
    """Eliminar todas las tablas (¡CUIDADO!)"""
    print("⚠️  ADVERTENCIA: Esta operación eliminará todas las tablas y sus datos")
    print("⚠️  Esto incluye:")
    print("   - Todos los casos y sus datos relacionados")
    print("   - Todos los usuarios y sesiones")
    print("   - Toda la configuración del sistema")
    print("   - Todos los logs y auditorías")
    print()
    confirm = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ")
    
    if confirm == "CONFIRMAR":
        print("\n🗑️  Eliminando tablas...")
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ Todas las tablas han sido eliminadas")
            return True
        except Exception as e:
            print(f"❌ Error eliminando tablas: {str(e)}")
            return False
    else:
        print("❌ Operación cancelada")
        return False


def verify_tables():
    """Verificar qué tablas existen en la base de datos"""
    print("🔍 Verificando tablas en la base de datos...")
    
    if not verify_connection():
        print("❌ Error: No se pudo conectar a la base de datos")
        return False
    
    existing_tables = get_existing_tables()
    
    expected_tables = [
        "tab_estadocaso", "tab_semaforo", "tab_tipopdf", "tab_estadoenvio",
        "tab_tipoadjunto", "tab_tipoaccion", "tab_usuario", "tab_configuracion",
        "tab_logingesta", "tab_sesion", "tab_caso", "tab_casoidentificador",
        "tab_escalamiento", "tab_adjunto", "tab_fuentecorreo", "tab_auditoriaevento"
    ]
    
    print(f"\n📊 Estado de las tablas ({len(existing_tables)}/{len(expected_tables)} existen):\n")
    
    for table in expected_tables:
        if table in existing_tables:
            print(f"   ✅ {table:30} - Existe")
        else:
            print(f"   ❌ {table:30} - No existe")
    
    missing = set(expected_tables) - existing_tables
    extra = existing_tables - set(expected_tables)
    
    if missing:
        print(f"\n⚠️  Faltan {len(missing)} tablas:")
        for table in sorted(missing):
            print(f"   - {table}")
    
    if extra:
        print(f"\n📋 Tablas adicionales encontradas ({len(extra)}):")
        for table in sorted(extra):
            print(f"   + {table}")
    
    if not missing and not extra:
        print("\n✨ ¡Perfecto! Todas las tablas esperadas existen.")
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("  SISTEMA PQR - GESTIÓN DE BASE DE DATOS")
    print("=" * 70)
    
    print("\nOpciones:")
    print("1. Crear tablas (inteligente - solo crea las faltantes)")
    print("2. Crear tablas (tradicional - crea todas de una vez)")
    print("3. Verificar tablas existentes")
    print("4. Insertar datos iniciales (seeds)")
    print("5. Eliminar todas las tablas (PELIGROSO)")
    print("6. Recrear tablas + seeds (Eliminar, crear e insertar datos)")
    
    option = input("\nSelecciona una opción (1-6): ").strip()
    
    if option == "1":
        create_tables_smart()
    elif option == "2":
        create_all_tables()
    elif option == "3":
        verify_tables()
    elif option == "4":
        # Ejecutar seeds directamente
        try:
            from seed_database import seed_all
            seed_all()
        except ImportError:
            print("❌ No se encontró el archivo seed_database.py")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    elif option == "5":
        drop_tables()
    elif option == "6":
        print("\n⚠️  Esta opción eliminará TODAS las tablas y datos, luego las recreará")
        print("    e insertará los datos iniciales.")
        if drop_tables():
            print()
            if create_tables_smart():
                print("\n🌱 Insertando datos iniciales...")
                try:
                    from seed_database import seed_all
                    seed_all()
                except ImportError:
                    print("❌ No se encontró el archivo seed_database.py")
                    print("   Ejecuta manualmente: python seed_database.py")
                except Exception as e:
                    print(f"❌ Error ejecutando seeds: {str(e)}")
    else:
        print("❌ Opción inválida")
    
    print("\n" + "=" * 70)
