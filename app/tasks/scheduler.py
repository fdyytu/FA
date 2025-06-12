from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.database import SessionLocal
from app.services.transaction_service import DailyMutationService
from app.services.notification_service import AdminNotificationService
from app.schemas.notification import NotificationSendRequest, NotificationTypeEnum, NotificationChannelEnum
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

# Konfigurasi Celery
celery_app = Celery(
    "fa_tasks",
    broker=getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=getattr(settings, 'CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Konfigurasi schedule
celery_app.conf.beat_schedule = {
    'generate-daily-mutation': {
        'task': 'app.tasks.scheduler.generate_daily_mutation_task',
        'schedule': crontab(hour=1, minute=0),  # Setiap hari jam 1 pagi
    },
    'send-daily-report': {
        'task': 'app.tasks.scheduler.send_daily_report_task',
        'schedule': crontab(hour=8, minute=0),  # Setiap hari jam 8 pagi
    },
}

celery_app.conf.timezone = 'Asia/Jakarta'

@celery_app.task
def generate_daily_mutation_task():
    """Task untuk generate mutasi harian otomatis"""
    try:
        db = SessionLocal()
        service = DailyMutationService(db)
        
        # Generate untuk kemarin
        yesterday = date.today() - timedelta(days=1)
        mutation = await service.generate_daily_mutation(yesterday)
        
        logger.info(f"Daily mutation generated successfully for {yesterday}")
        
        # Kirim notifikasi ke admin
        admin_service = AdminNotificationService(db)
        notification_request = NotificationSendRequest(
            title="Mutasi Harian Berhasil Dibuat",
            message=f"Mutasi harian untuk tanggal {yesterday} berhasil dibuat.\n"
                   f"Total transaksi: {mutation.total_transactions}\n"
                   f"Total amount: Rp {mutation.total_amount:,.2f}\n"
                   f"Success: {mutation.success_count}, Failed: {mutation.failed_count}",
            notification_type=NotificationTypeEnum.SYSTEM,
            channels=[NotificationChannelEnum.DISCORD, NotificationChannelEnum.EMAIL]
        )
        
        await admin_service.send_admin_notification(notification_request)
        
        db.close()
        return {"status": "success", "date": str(yesterday)}
        
    except Exception as e:
        logger.error(f"Error generating daily mutation: {str(e)}")
        
        # Kirim notifikasi error ke admin
        try:
            db = SessionLocal()
            admin_service = AdminNotificationService(db)
            notification_request = NotificationSendRequest(
                title="Error Generate Mutasi Harian",
                message=f"Terjadi error saat generate mutasi harian: {str(e)}",
                notification_type=NotificationTypeEnum.SYSTEM,
                channels=[NotificationChannelEnum.DISCORD, NotificationChannelEnum.EMAIL]
            )
            
            await admin_service.send_admin_notification(notification_request)
            db.close()
        except:
            pass
        
        return {"status": "error", "message": str(e)}

@celery_app.task
def send_daily_report_task():
    """Task untuk kirim laporan harian ke admin"""
    try:
        db = SessionLocal()
        
        # Ambil data mutasi kemarin
        yesterday = date.today() - timedelta(days=1)
        service = DailyMutationService(db)
        
        mutations = await service.get_daily_mutations(yesterday, yesterday)
        
        if mutations:
            mutation = mutations[0]
            
            # Format laporan
            report_message = f"""
📊 **LAPORAN HARIAN - {yesterday}**

📈 **Ringkasan Transaksi:**
• Total Transaksi: {mutation.total_transactions:,}
• Total Amount: Rp {float(mutation.total_amount):,.2f}
• Total Fee: Rp {float(mutation.total_fee):,.2f}

✅ **Status Breakdown:**
• Berhasil: {mutation.success_count:,}
• Gagal: {mutation.failed_count:,}
• Pending: {mutation.pending_count:,}

📊 **Success Rate:** {(mutation.success_count / mutation.total_transactions * 100) if mutation.total_transactions > 0 else 0:.1f}%

---
Laporan otomatis dari sistem FA
            """.strip()
            
            # Kirim ke admin
            admin_service = AdminNotificationService(db)
            notification_request = NotificationSendRequest(
                title=f"Laporan Harian - {yesterday}",
                message=report_message,
                notification_type=NotificationTypeEnum.SYSTEM,
                channels=[NotificationChannelEnum.DISCORD, NotificationChannelEnum.EMAIL]
            )
            
            await admin_service.send_admin_notification(notification_request)
            
            logger.info(f"Daily report sent successfully for {yesterday}")
        else:
            logger.warning(f"No mutation data found for {yesterday}")
        
        db.close()
        return {"status": "success", "date": str(yesterday)}
        
    except Exception as e:
        logger.error(f"Error sending daily report: {str(e)}")
        return {"status": "error", "message": str(e)}

@celery_app.task
def test_notification_task(title: str, message: str):
    """Task untuk test notifikasi"""
    try:
        db = SessionLocal()
        admin_service = AdminNotificationService(db)
        
        notification_request = NotificationSendRequest(
            title=title,
            message=message,
            notification_type=NotificationTypeEnum.SYSTEM,
            channels=[NotificationChannelEnum.DISCORD]
        )
        
        await admin_service.send_admin_notification(notification_request)
        
        db.close()
        return {"status": "success", "title": title}
        
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return {"status": "error", "message": str(e)}
