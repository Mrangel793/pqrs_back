from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = BackgroundScheduler()


def ingestion_job():
    """Job para ingesta de correos"""
    print(f"[{datetime.now()}] Ejecutando job de ingesta de correos...")
    # Aquí se ejecutará la lógica de ingesta
    # from app.services.ingestion_service import process_emails
    # process_emails()


def escalation_check_job():
    """Job para verificar escalamientos pendientes"""
    print(f"[{datetime.now()}] Verificando escalamientos pendientes...")
    # Lógica para verificar casos que deben escalarse


def cleanup_job():
    """Job para limpieza de archivos temporales"""
    print(f"[{datetime.now()}] Ejecutando limpieza de archivos temporales...")
    # Lógica para eliminar archivos antiguos


def start_scheduler():
    """Iniciar scheduler con jobs programados"""

    # Job de ingesta cada 15 minutos
    scheduler.add_job(
        ingestion_job,
        trigger=CronTrigger(minute="*/15"),
        id="ingestion_job",
        name="Ingesta de correos",
        replace_existing=True
    )

    # Job de verificación de escalamientos cada hora
    scheduler.add_job(
        escalation_check_job,
        trigger=CronTrigger(hour="*"),
        id="escalation_check_job",
        name="Verificación de escalamientos",
        replace_existing=True
    )

    # Job de limpieza diaria a las 2 AM
    scheduler.add_job(
        cleanup_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="cleanup_job",
        name="Limpieza de archivos",
        replace_existing=True
    )

    scheduler.start()
    print("✅ Scheduler iniciado correctamente")


def stop_scheduler():
    """Detener scheduler"""
    scheduler.shutdown()
    print("🛑 Scheduler detenido")
