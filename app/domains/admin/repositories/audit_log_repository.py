"""
Repository untuk audit log
Dipecah dari admin_repository.py untuk meningkatkan maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Tuple

from app.common.logging.admin_logger import admin_logger
from app.domains.admin.models.admin import AdminAuditLog


class AuditLogRepository:
    """
    Repository untuk audit log - Single Responsibility: Data access untuk audit log
    """
    
    def __init__(self, db: Session):
        self.db = db
        admin_logger.info("AuditLogRepository initialized")
    
    def create_log(
        self,
        admin_id: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        old_values: Optional[str] = None,
        new_values: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AdminAuditLog:
        """Buat log audit baru"""
        try:
            admin_logger.info(f"Membuat audit log - admin: {admin_id}, action: {action}, resource: {resource}")
            
            audit_log = AdminAuditLog(
                admin_id=admin_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)
            
            admin_logger.info(f"Audit log berhasil dibuat dengan ID: {audit_log.id}")
            return audit_log
            
        except Exception as e:
            admin_logger.error(f"Error saat membuat audit log", e, {
                "admin_id": admin_id, "action": action, "resource": resource
            })
            self.db.rollback()
            raise
    
    def get_logs_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None
    ) -> Tuple[List[AdminAuditLog], int]:
        """Ambil audit log dengan pagination dan filter"""
        try:
            admin_logger.info(f"Mengambil audit logs dengan pagination - skip: {skip}, limit: {limit}")
            query = self.db.query(AdminAuditLog)
            
            if admin_id:
                admin_logger.info(f"Menerapkan filter admin_id: {admin_id}")
                query = query.filter(AdminAuditLog.admin_id == admin_id)
            
            if action:
                admin_logger.info(f"Menerapkan filter action: {action}")
                query = query.filter(AdminAuditLog.action == action)
            
            if resource:
                admin_logger.info(f"Menerapkan filter resource: {resource}")
                query = query.filter(AdminAuditLog.resource == resource)
            
            total = query.count()
            logs = query.order_by(desc(AdminAuditLog.created_at)).offset(skip).limit(limit).all()
            
            admin_logger.info(f"Ditemukan {len(logs)} audit logs dari total {total}")
            return logs, total
            
        except Exception as e:
            admin_logger.error("Error saat mengambil audit logs dengan pagination", e, {
                "skip": skip, "limit": limit, "admin_id": admin_id, 
                "action": action, "resource": resource
            })
            raise
