from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.product import Product, ProductStock
from app.schemas.product import ProductCreate, ProductUpdate, ProductStockCreate
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """Buat produk baru"""
        # Cek apakah kode produk sudah ada
        existing_product = self.db.query(Product).filter(Product.code == product_data.code).first()
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Produk dengan kode {product_data.code} sudah ada"
            )
        
        product = Product(**product_data.dict())
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Ambil produk berdasarkan ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()
    
    def get_product_by_code(self, code: str) -> Optional[Product]:
        """Ambil produk berdasarkan kode"""
        return self.db.query(Product).filter(Product.code == code).first()
    
    def get_all_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Ambil semua produk"""
        return self.db.query(Product).offset(skip).limit(limit).all()
    
    def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        """Update produk"""
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Hapus produk"""
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        self.db.delete(product)
        self.db.commit()
        return True

class ProductStockService:
    def __init__(self, db: Session):
        self.db = db
    
    def add_stock_from_file(self, product_id: int, file: UploadFile, notes: Optional[str] = None) -> ProductStock:
        """Tambah stock dari file upload"""
        # Validasi produk
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produk tidak ditemukan"
            )
        
        # Validasi file
        if not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File harus berformat .txt"
            )
        
        try:
            # Baca isi file
            content = file.file.read().decode('utf-8')
            
            # Hitung jumlah baris (stock)
            lines = content.strip().split('\n')
            quantity = len([line for line in lines if line.strip()])  # hitung baris yang tidak kosong
            
            # Buat record stock baru
            stock_data = ProductStockCreate(
                product_id=product_id,
                quantity=quantity,
                file_name=file.filename,
                file_content=content,
                notes=notes
            )
            
            stock = ProductStock(**stock_data.dict())
            self.db.add(stock)
            
            # Update total stock produk (jika ada field total_stock di model Product)
            # Untuk sekarang kita hanya simpan record stock
            
            self.db.commit()
            self.db.refresh(stock)
            
            logger.info(f"Stock added for product {product_id}: {quantity} items from file {file.filename}")
            return stock
            
        except Exception as e:
            logger.error(f"Error processing file upload: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses file: {str(e)}"
            )
    
    def get_product_stocks(self, product_id: int) -> List[ProductStock]:
        """Ambil semua stock untuk produk tertentu"""
        return self.db.query(ProductStock).filter(ProductStock.product_id == product_id).all()
    
    def get_total_stock(self, product_id: int) -> int:
        """Hitung total stock untuk produk"""
        stocks = self.get_product_stocks(product_id)
        return sum(stock.quantity for stock in stocks)
    
    def delete_stock(self, stock_id: int) -> bool:
        """Hapus record stock"""
        stock = self.db.query(ProductStock).filter(ProductStock.id == stock_id).first()
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock tidak ditemukan"
            )
        
        self.db.delete(stock)
        self.db.commit()
        return True
