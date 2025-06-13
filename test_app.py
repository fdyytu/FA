#!/usr/bin/env python3
"""
Script untuk menguji aplikasi FA sebelum deployment ke Railway
"""
import asyncio
import httpx
import uvicorn
import multiprocessing
import time
import os
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def start_server():
    """Start the FastAPI server"""
    os.environ["DATABASE_URL"] = "sqlite:///./test_fa.db"
    os.environ["DEBUG"] = "True"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

async def test_endpoints():
    """Test the main endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("🔍 Testing /health endpoint...")
            response = await client.get(f"{base_url}/health")
            print(f"Health check: {response.status_code} - {response.json()}")
            
            # Test API docs
            print("🔍 Testing /docs endpoint...")
            response = await client.get(f"{base_url}/docs")
            print(f"API Docs: {response.status_code}")
            
            # Test API v1 endpoints
            print("🔍 Testing API v1 endpoints...")
            response = await client.get(f"{base_url}/api/v1/")
            print(f"API v1: {response.status_code}")
            
            print("✅ All tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

def main():
    """Main test function"""
    print("🚀 Starting FA Application Test...")
    
    # Start server in separate process
    server_process = multiprocessing.Process(target=start_server)
    server_process.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Run tests
        result = asyncio.run(test_endpoints())
        
        if result:
            print("🎉 Application is ready for Railway deployment!")
        else:
            print("⚠️ Application has issues that need to be fixed")
            
    finally:
        # Clean up
        server_process.terminate()
        server_process.join()
        
        # Remove test database
        test_db = Path("test_fa.db")
        if test_db.exists():
            test_db.unlink()

if __name__ == "__main__":
    main()
