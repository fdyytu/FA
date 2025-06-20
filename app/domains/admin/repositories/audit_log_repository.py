"""
Audit Log Repository
Repository untuk data access audit log operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from app.domains.admin.models.admin import AdminAuditLog


class AuditLogRepository:
    """
    Repository untuk audit log - Single Responsibility: Data access untuk audit log
    """
    
    def __init__(self, db: Session):
        self.db = db
    
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
        
        return audit_log
    
    def get_logs_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        admin_id: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None
    ) -> tuple[List[AdminAuditLog], int]:
        """Ambil audit log dengan pagination dan filter"""
        query = self.db.query(AdminAuditLog)
        
        if admin_id:
            query = query.filter(AdminAuditLog.admin_id == admin_id)
        
        if action:
            query = query.filter(AdminAuditLog.action == action)
        
        if resource:
            query = query.filter(AdminAuditLog.resource == resource)
        
        total = query.count()
        logs = query.order_by(desc(AdminAuditLog.created_at)).offset(skip).limit(limit).all()
        
        return logs, total
