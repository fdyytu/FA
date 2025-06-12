from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.responses.api_response import APIResponse

T = TypeVar('T')  # Model type
S = TypeVar('S')  # Service type
CreateSchema = TypeVar('CreateSchema')
UpdateSchema = TypeVar('UpdateSchema')
ResponseSchema = TypeVar('ResponseSchema')

class BaseController(ABC, Generic[T, S, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Base controller class yang mengimplementasikan Open/Closed Principle.
    Controller dapat di-extend tanpa memodifikasi kode yang sudah ada.
    """
    
    def __init__(self, service: S, router_prefix: str, tags: List[str]):
        self.service = service
        self.router = APIRouter(prefix=router_prefix, tags=tags)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup default CRUD routes"""
        self.router.add_api_route(
            "/", 
            self.create_item, 
            methods=["POST"], 
            response_model=APIResponse[ResponseSchema]
        )
        self.router.add_api_route(
            "/{item_id}", 
            self.get_item, 
            methods=["GET"], 
            response_model=APIResponse[ResponseSchema]
        )
        self.router.add_api_route(
            "/", 
            self.get_items, 
            methods=["GET"], 
            response_model=APIResponse[List[ResponseSchema]]
        )
        self.router.add_api_route(
            "/{item_id}", 
            self.update_item, 
            methods=["PUT"], 
            response_model=APIResponse[ResponseSchema]
        )
        self.router.add_api_route(
            "/{item_id}", 
            self.delete_item, 
            methods=["DELETE"], 
            response_model=APIResponse[dict]
        )
    
    @abstractmethod
    async def create_item(self, item_data: CreateSchema) -> APIResponse[ResponseSchema]:
        """Buat item baru"""
        pass
    
    @abstractmethod
    async def get_item(self, item_id: int) -> APIResponse[ResponseSchema]:
        """Ambil item berdasarkan ID"""
        pass
    
    @abstractmethod
    async def get_items(self, skip: int = 0, limit: int = 100) -> APIResponse[List[ResponseSchema]]:
        """Ambil semua items dengan pagination"""
        pass
    
    @abstractmethod
    async def update_item(self, item_id: int, item_data: UpdateSchema) -> APIResponse[ResponseSchema]:
        """Update item"""
        pass
    
    @abstractmethod
    async def delete_item(self, item_id: int) -> APIResponse[dict]:
        """Hapus item"""
        pass
    
    def _handle_not_found(self, item_id: Any, item_name: str = "Item"):
        """Helper method untuk handle item not found"""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{item_name} dengan ID {item_id} tidak ditemukan"
        )
    
    def _handle_validation_error(self, message: str):
        """Helper method untuk handle validation error"""
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
