#!/usr/bin/env python3
"""
Simple admin login endpoint untuk testing
"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.infrastructure.security.password_handler import PasswordHandler
from app.common.security.auth_security import create_access_token
from sqlalchemy import text

app = FastAPI(title="Simple Admin Login Test")

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    admin_id: str
    username: str
    message: str

@app.post("/login", response_model=LoginResponse)
async def simple_login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Simple admin login untuk testing"""
    try:
        # Query admin dari database
        result = db.execute(text("SELECT * FROM admins WHERE username = :username"), 
                          {"username": login_data.username})
        admin_row = result.fetchone()
        
        if not admin_row:
            raise HTTPException(status_code=401, detail="Username tidak ditemukan")
        
        # Verify password
        password_handler = PasswordHandler()
        stored_hash = admin_row[4]  # hashed_password column
        
        if not password_handler.verify_password(login_data.password, stored_hash):
            raise HTTPException(status_code=401, detail="Password salah")
        
        # Check if active
        is_active = admin_row[5]  # is_active column
        if not is_active:
            raise HTTPException(status_code=401, detail="Admin tidak aktif")
        
        # Create access token
        access_token = create_access_token(
            data={"sub": admin_row[0], "type": "admin"}  # admin_id
        )
        
        return LoginResponse(
            access_token=access_token,
            admin_id=admin_row[0],
            username=admin_row[1],
            message="Login berhasil!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Simple Admin Login Test API"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting simple admin login test server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
