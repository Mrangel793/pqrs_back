"""
Script para insertar datos iniciales (seeds) en la base de datos.

Este script inserta datos base necesarios para el funcionamiento del sistema:
- Catálogos (estados, tipos, etc.)
- Usuarios iniciales
- Configuración del sistema

Ejecutar después de crear las tablas.

Uso:
    python seed_database.py
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine, SessionLocal, verify_connection
from app.models.models import (
    EstadoCaso, Semaforo, TipoPDF, EstadoEnvio, TipoAdjunto, TipoAccion,
    Usuario, Configuracion
)
import json


def seed_estado_caso(db: Session):
    """Insertar estados de caso"""
    print("   📋 Insertando Estados de Caso...")
    
    estados = [
        {'codigo': 'NUEVO', 'descripcion': 'Caso recién ingresado'},
        {'codigo': 'EN_GESTION', 'descripcion': 'En gestión'},
        {'codigo': 'ESCALADO', 'descripcion': 'Escalado internamente'},
        {'codigo': 'LISTO_PDF', 'descripcion': 'Respuesta lista'},
        {'codigo': 'ENVIADO_ENTIDAD', 'descripcion': 'Respuesta enviada'},
        {'codigo': 'CERRADO', 'descripcion': 'Caso cerrado'},
        {'codigo': 'INCOMPLETO', 'descripcion': 'Faltan datos'},
        {'codigo': 'ERROR_ENVIO', 'descripcion': 'Error al enviar correo'},
    ]
    
    count = 0
    for estado_data in estados:
        # Verificar si ya existe
        existing = db.query(EstadoCaso).filter_by(codigo=estado_data['codigo']).first()
        if not existing:
            estado = EstadoCaso(**estado_data)
            db.add(estado)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} estados insertados ({len(estados) - count} ya existían)")


def seed_semaforo(db: Session):
    """Insertar semáforos"""
    print("   🚦 Insertando Semáforos...")
    
    semaforos = [
        {'codigo': 'VERDE', 'descripcion': 'Sin urgencia', 'colorHex': '#22C55E', 'diasMin': 10, 'diasMax': None, 'orden': 1},
        {'codigo': 'MARINA', 'descripcion': 'Pre-alerta', 'colorHex': '#06B6D4', 'diasMin': 5, 'diasMax': 9, 'orden': 2},
        {'codigo': 'NARANJA', 'descripcion': 'Prioritario', 'colorHex': '#F97316', 'diasMin': 2, 'diasMax': 4, 'orden': 3},
        {'codigo': 'ROJO', 'descripcion': 'Crítico', 'colorHex': '#EF4444', 'diasMin': 0, 'diasMax': 1, 'orden': 4},
    ]
    
    count = 0
    for semaforo_data in semaforos:
        existing = db.query(Semaforo).filter_by(codigo=semaforo_data['codigo']).first()
        if not existing:
            semaforo = Semaforo(**semaforo_data)
            db.add(semaforo)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} semáforos insertados ({len(semaforos) - count} ya existían)")


def seed_tipo_pdf(db: Session):
    """Insertar tipos de PDF"""
    print("   📄 Insertando Tipos de PDF...")
    
    tipos = [
        {'codigo': 'FACTURA', 'descripcion': 'Respuesta Factura'},
        {'codigo': 'POSTILLA_APOSTILLA', 'descripcion': 'Respuesta Postilla/Apostilla'},
        {'codigo': 'FALLA_NO_RESPUESTA', 'descripcion': 'Falla o No disponibilidad'},
    ]
    
    count = 0
    for tipo_data in tipos:
        existing = db.query(TipoPDF).filter_by(codigo=tipo_data['codigo']).first()
        if not existing:
            tipo = TipoPDF(**tipo_data)
            db.add(tipo)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} tipos de PDF insertados ({len(tipos) - count} ya existían)")


def seed_estado_envio(db: Session):
    """Insertar estados de envío"""
    print("   📧 Insertando Estados de Envío...")
    
    estados = [
        {'codigo': 'PENDIENTE', 'descripcion': 'Pendiente de envío'},
        {'codigo': 'ENVIADO', 'descripcion': 'Enviado exitosamente'},
        {'codigo': 'FALLIDO', 'descripcion': 'Error en envío'},
    ]
    
    count = 0
    for estado_data in estados:
        existing = db.query(EstadoEnvio).filter_by(codigo=estado_data['codigo']).first()
        if not existing:
            estado = EstadoEnvio(**estado_data)
            db.add(estado)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} estados de envío insertados ({len(estados) - count} ya existían)")


def seed_tipo_adjunto(db: Session):
    """Insertar tipos de adjunto"""
    print("   📎 Insertando Tipos de Adjunto...")
    
    tipos = [
        {'codigo': 'IMAGEN_RESPUESTA', 'descripcion': 'Imagen insertada en respuesta'},
        {'codigo': 'ADJUNTO_CORREO', 'descripcion': 'Adjunto del correo original'},
        {'codigo': 'PDF_GENERADO', 'descripcion': 'PDF de respuesta generado'},
    ]
    
    count = 0
    for tipo_data in tipos:
        existing = db.query(TipoAdjunto).filter_by(codigo=tipo_data['codigo']).first()
        if not existing:
            tipo = TipoAdjunto(**tipo_data)
            db.add(tipo)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} tipos de adjunto insertados ({len(tipos) - count} ya existían)")


def seed_tipo_accion(db: Session):
    """Insertar tipos de acción de auditoría"""
    print("   🔍 Insertando Tipos de Acción...")
    
    tipos = [
        {'codigo': 'CASO_CREADO', 'descripcion': 'Caso creado'},
        {'codigo': 'CASO_ACTUALIZADO', 'descripcion': 'Caso actualizado'},
        {'codigo': 'CASO_ASIGNADO', 'descripcion': 'Caso asignado a responsable'},
        {'codigo': 'CASO_ESCALADO', 'descripcion': 'Caso escalado internamente'},
        {'codigo': 'ESTADO_CAMBIADO', 'descripcion': 'Estado del caso cambiado'},
        {'codigo': 'RESPUESTA_GUARDADA', 'descripcion': 'Respuesta guardada/actualizada'},
        {'codigo': 'PDF_GENERADO', 'descripcion': 'PDF de respuesta generado'},
        {'codigo': 'CORREO_ENVIADO', 'descripcion': 'Correo de respuesta enviado'},
        {'codigo': 'CORREO_FALLIDO', 'descripcion': 'Error al enviar correo'},
        {'codigo': 'ADJUNTO_SUBIDO', 'descripcion': 'Adjunto subido'},
        {'codigo': 'ADJUNTO_ELIMINADO', 'descripcion': 'Adjunto eliminado'},
        {'codigo': 'SEGUIMIENTO_RECIBIDO', 'descripcion': 'Correo de seguimiento recibido'},
        {'codigo': 'CONFIGURACION_ACTUALIZADA', 'descripcion': 'Configuración del sistema actualizada'},
        {'codigo': 'INGESTA_EJECUTADA', 'descripcion': 'Proceso de ingesta ejecutado'},
    ]
    
    count = 0
    for tipo_data in tipos:
        existing = db.query(TipoAccion).filter_by(codigo=tipo_data['codigo']).first()
        if not existing:
            tipo = TipoAccion(**tipo_data)
            db.add(tipo)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} tipos de acción insertados ({len(tipos) - count} ya existían)")


def seed_usuarios(db: Session):
    """Insertar usuarios iniciales"""
    print("   👥 Insertando Usuarios...")
    
    # Password hash para "temporal123" usando argon2
    password_hash = '$argon2id$v=19$m=65536,t=3,p=4$ztkbo9R67703RkiJca71ng$CatpNbzHqGub0MDbQ8dYNBp6tnxCdmlCwz/OudKeCYw'
    
    usuarios = [
        {'nombre': 'Administrador', 'correo': 'admin@entidad.gov.co', 'passwordHash': password_hash},
        {'nombre': 'Juan Pérez', 'correo': 'juan.perez@entidad.gov.co', 'passwordHash': password_hash},
        {'nombre': 'María García', 'correo': 'maria.garcia@entidad.gov.co', 'passwordHash': password_hash},
        {'nombre': 'Carlos López', 'correo': 'carlos.lopez@entidad.gov.co', 'passwordHash': password_hash},
        {'nombre': 'Ana Martínez', 'correo': 'ana.martinez@entidad.gov.co', 'passwordHash': password_hash},
    ]
    
    count = 0
    for usuario_data in usuarios:
        existing = db.query(Usuario).filter_by(correo=usuario_data['correo']).first()
        if not existing:
            usuario = Usuario(**usuario_data)
            db.add(usuario)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} usuarios insertados ({len(usuarios) - count} ya existían)")
    print(f"      🔑 Password para todos los usuarios: temporal123")


def seed_configuracion(db: Session):
    """Insertar configuración inicial del sistema"""
    print("   ⚙️  Insertando Configuración del Sistema...")
    
    configuraciones = [
        # Integración de correo
        {
            'clave': 'CORREO_BUZON',
            'valor': 'pqr@entidad.gov.co',
            'tipoDato': 'STRING',
            'descripcion': 'Dirección del buzón de correo para ingesta'
        },
        {
            'clave': 'CORREO_INGESTA_INTERVALO',
            'valor': '10',
            'tipoDato': 'INT',
            'descripcion': 'Intervalo de ingesta en minutos'
        },
        {
            'clave': 'CORREO_INGESTA_ACTIVA',
            'valor': 'true',
            'tipoDato': 'BOOL',
            'descripcion': 'Indica si la ingesta automática está activa'
        },
        
        # Plantillas de correo
        {
            'clave': 'PLANTILLA_CORREO_FACTURA',
            'valor': json.dumps({
                "asunto": "RE: Respuesta a su solicitud - Radicado {{radicado}}",
                "cuerpo": "Estimado usuario,\n\nEn atención a su solicitud con radicado {{radicado}}, adjuntamos la respuesta correspondiente.\n\nPuede consultar su factura en el siguiente enlace: {{enlace_consulta}}\n\nCordialmente,\nEquipo de Tecnología"
            }),
            'tipoDato': 'JSON',
            'descripcion': 'Plantilla de correo para respuestas tipo Factura'
        },
        {
            'clave': 'PLANTILLA_CORREO_POSTILLA',
            'valor': json.dumps({
                "asunto": "RE: Respuesta a su solicitud - Radicado {{radicado}}",
                "cuerpo": "Estimado usuario,\n\nEn atención a su solicitud con radicado {{radicado}}, adjuntamos la respuesta correspondiente.\n\nPuede consultar su documento apostillado en: {{enlace_consulta}}\n\nCordialmente,\nEquipo de Tecnología"
            }),
            'tipoDato': 'JSON',
            'descripcion': 'Plantilla de correo para respuestas tipo Postilla/Apostilla'
        },
        {
            'clave': 'PLANTILLA_CORREO_FALLA',
            'valor': json.dumps({
                "asunto": "RE: Respuesta a su solicitud - Radicado {{radicado}}",
                "cuerpo": "Estimado usuario,\n\nEn atención a su solicitud con radicado {{radicado}}, le informamos que no fue posible procesar su requerimiento debido a una falla técnica o falta de información.\n\nPor favor comuníquese con nosotros para más información.\n\nCordialmente,\nEquipo de Tecnología"
            }),
            'tipoDato': 'JSON',
            'descripcion': 'Plantilla de correo para respuestas tipo Falla/No disponibilidad'
        },
        {
            'clave': 'PLANTILLA_VARIABLES',
            'valor': json.dumps([
                "radicado", "fecha_vencimiento", "peticionario_nombre",
                "peticionario_correo", "tipo_tramite", "id_consulta_1",
                "id_consulta_2", "enlace_consulta", "responsable", "fecha_respuesta"
            ]),
            'tipoDato': 'JSON',
            'descripcion': 'Variables disponibles para plantillas'
        },
    ]
    
    count = 0
    for config_data in configuraciones:
        existing = db.query(Configuracion).filter_by(clave=config_data['clave']).first()
        if not existing:
            config = Configuracion(**config_data)
            db.add(config)
            count += 1
    
    db.commit()
    print(f"      ✅ {count} configuraciones insertadas ({len(configuraciones) - count} ya existían)")


def seed_all():
    """Ejecutar todas las seeds"""
    print("🌱 Iniciando inserción de datos iniciales (seeds)...")
    
    # Verificar conexión
    print("\n📊 Verificando conexión a base de datos...")
    if not verify_connection():
        print("❌ Error: No se pudo conectar a la base de datos")
        return False
    
    print("✅ Conexión exitosa")
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        print("\n📝 Insertando datos base...\n")
        
        # Catálogos (en orden)
        seed_estado_caso(db)
        seed_semaforo(db)
        seed_tipo_pdf(db)
        seed_estado_envio(db)
        seed_tipo_adjunto(db)
        seed_tipo_accion(db)
        
        # Usuarios
        seed_usuarios(db)
        
        # Configuración
        seed_configuracion(db)
        
        print("\n" + "=" * 70)
        print("✅ SEEDS COMPLETADAS EXITOSAMENTE")
        print("=" * 70)
        print("\n📋 Datos insertados:")
        print("   ✓ Estados de Caso (8)")
        print("   ✓ Semáforos (4)")
        print("   ✓ Tipos de PDF (3)")
        print("   ✓ Estados de Envío (3)")
        print("   ✓ Tipos de Adjunto (3)")
        print("   ✓ Tipos de Acción (14)")
        print("   ✓ Usuarios (5)")
        print("   ✓ Configuraciones (8)")
        print("\n👤 Usuarios creados:")
        print("   - admin@entidad.gov.co (Administrador)")
        print("   - juan.perez@entidad.gov.co")
        print("   - maria.garcia@entidad.gov.co")
        print("   - carlos.lopez@entidad.gov.co")
        print("   - ana.martinez@entidad.gov.co")
        print("\n🔑 Password para todos: temporal123")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la inserción de seeds: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("  SISTEMA PQR - INSERCIÓN DE DATOS INICIALES")
    print("=" * 70)
    
    confirm = input("\n¿Deseas insertar los datos iniciales? (s/n): ").strip().lower()
    
    if confirm == 's':
        seed_all()
    else:
        print("❌ Operación cancelada")
    
    print("\n" + "=" * 70)
