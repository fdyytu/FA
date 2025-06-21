"""Pagination Service untuk Discord - Efficient data loading"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
import math

class PaginationService:
    def __init__(self, db_session: Session):
        """Initialize pagination service dengan database session"""
        self.db = db_session
        self.default_page_size = 20
        self.max_page_size = 100

    def paginate_query(self, query, page: int = 1, page_size: int = None) -> Dict[str, Any]:
        """Paginate SQLAlchemy query dengan cursor-based pagination"""
        if page_size is None:
            page_size = self.default_page_size
        page_size = min(page_size, self.max_page_size)
        page = max(1, page)
        
        total_count = query.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        
        return {
            'items': items,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1,
                'next_page': page + 1 if page < total_pages else None,
                'prev_page': page - 1 if page > 1 else None
            }
        }

    def paginate_logs(self, model_class, filters: Dict = None, 
                     page: int = 1, page_size: int = None) -> Dict[str, Any]:
        """Paginate command logs dengan filtering"""
        query = self.db.query(model_class)
        if filters:
            for key, value in filters.items():
                if hasattr(model_class, key) and value is not None:
                    query = query.filter(getattr(model_class, key) == value)
        if hasattr(model_class, 'timestamp'):
            query = query.order_by(desc(model_class.timestamp))
        return self.paginate_query(query, page, page_size)
