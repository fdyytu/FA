from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from ..models.command_log import CommandLog
from ..repositories.command_log_repository import CommandLogRepository

class LogFilterService:
    """Service untuk advanced filtering dan search bot logs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = CommandLogRepository(db)
        
    async def filter_logs(self, filters: Dict[str, Any]) -> List[CommandLog]:
        """Filter logs berdasarkan kriteria yang diberikan"""
        query = self.db.query(CommandLog)
        
        # Filter berdasarkan user_id
        if filters.get('user_id'):
            query = query.filter(CommandLog.user_id == filters['user_id'])
            
        # Filter berdasarkan guild_id
        if filters.get('guild_id'):
            query = query.filter(CommandLog.guild_id == filters['guild_id'])
            
        # Filter berdasarkan command
        if filters.get('command'):
            query = query.filter(CommandLog.command.ilike(f"%{filters['command']}%"))
            
        # Filter berdasarkan status (success/error)
        if filters.get('status'):
            if filters['status'] == 'success':
                query = query.filter(CommandLog.error_message.is_(None))
            elif filters['status'] == 'error':
                query = query.filter(CommandLog.error_message.isnot(None))
                
        # Filter berdasarkan rentang waktu
        if filters.get('start_date'):
            start_date = datetime.fromisoformat(filters['start_date'])
            query = query.filter(CommandLog.timestamp >= start_date)
            
        if filters.get('end_date'):
            end_date = datetime.fromisoformat(filters['end_date'])
            query = query.filter(CommandLog.timestamp <= end_date)
            
        # Filter berdasarkan execution time
        if filters.get('min_execution_time'):
            query = query.filter(CommandLog.execution_time >= filters['min_execution_time'])
            
        if filters.get('max_execution_time'):
            query = query.filter(CommandLog.execution_time <= filters['max_execution_time'])
            
        # Sorting
        sort_by = filters.get('sort_by', 'timestamp')
        sort_order = filters.get('sort_order', 'desc')
        
        if hasattr(CommandLog, sort_by):
            column = getattr(CommandLog, sort_by)
            if sort_order == 'asc':
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
                
        # Pagination
        limit = filters.get('limit', 100)
        offset = filters.get('offset', 0)
        
        return query.offset(offset).limit(limit).all()
        
    async def search_logs(self, search_term: str, search_fields: List[str] = None) -> List[CommandLog]:
        """Search logs berdasarkan term tertentu"""
        if not search_fields:
            search_fields = ['command', 'response', 'error_message']
            
        query = self.db.query(CommandLog)
        search_conditions = []
        
        for field in search_fields:
            if hasattr(CommandLog, field):
                column = getattr(CommandLog, field)
                search_conditions.append(column.ilike(f"%{search_term}%"))
                
        if search_conditions:
            query = query.filter(or_(*search_conditions))
            
        return query.order_by(desc(CommandLog.timestamp)).limit(50).all()
