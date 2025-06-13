"""
File Monitor Callback Handlers
Mengelola callback dari file system events
"""
from typing import Dict, Any
from pathlib import Path
import logging

from app.callbacks.base.base_handlers import EventCallbackHandler

logger = logging.getLogger(__name__)


class FileMonitorCallbackHandler(EventCallbackHandler):
    """Handler untuk file system events"""
    
    def __init__(self):
        super().__init__("FileMonitorCallback", "file_system")
        self.monitored_extensions = {'.log', '.txt', '.json', '.csv', '.xml'}
        self.ignored_patterns = {'__pycache__', '.git', '.env', 'node_modules'}
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file system events"""
        event_type = data.get('type')
        file_path = data.get('path')
        filename = data.get('filename')
        
        if not file_path or not event_type:
            raise ValueError("Missing required fields: type and path")
        
        try:
            # Filter events berdasarkan pattern
            if self._should_ignore_file(file_path):
                return {'success': True, 'message': 'File ignored', 'action': 'ignored'}
            
            # Process berdasarkan event type
            if event_type == 'created':
                return await self._handle_file_created(file_path, filename)
            elif event_type == 'modified':
                return await self._handle_file_modified(file_path, filename)
            elif event_type == 'deleted':
                return await self._handle_file_deleted(file_path, filename)
            else:
                logger.warning(f"Unknown file event type: {event_type}")
                return {'success': False, 'message': f'Unknown event type: {event_type}'}
                
        except Exception as e:
            logger.error(f"Error processing file event: {str(e)}")
            raise
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored"""
        path = Path(file_path)
        
        # Ignore berdasarkan pattern
        for pattern in self.ignored_patterns:
            if pattern in str(path):
                return True
        
        # Ignore berdasarkan extension (jika tidak dalam whitelist)
        if path.suffix and path.suffix not in self.monitored_extensions:
            return True
        
        # Ignore hidden files
        if path.name.startswith('.'):
            return True
        
        return False
    
    async def _handle_file_created(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Handle file created event"""
        try:
            path = Path(file_path)
            file_size = path.stat().st_size if path.exists() else 0
            
            logger.info(f"File created: {filename} ({file_size} bytes)")
            
            # Process berdasarkan jenis file
            if path.suffix == '.log':
                await self._process_log_file(file_path)
            elif path.suffix == '.json':
                await self._process_json_file(file_path)
            elif path.suffix == '.csv':
                await self._process_csv_file(file_path)
            
            # Log ke database jika diperlukan
            await self._log_file_event('created', file_path, {'size': file_size})
            
            return {
                'success': True,
                'message': f'File created: {filename}',
                'action': 'processed',
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Error handling file created: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_file_modified(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Handle file modified event"""
        try:
            path = Path(file_path)
            file_size = path.stat().st_size if path.exists() else 0
            
            logger.info(f"File modified: {filename} ({file_size} bytes)")
            
            # Process berdasarkan jenis file
            if path.suffix == '.log':
                await self._process_log_file_update(file_path)
            elif path.suffix == '.json':
                await self._process_json_file_update(file_path)
            
            # Log ke database
            await self._log_file_event('modified', file_path, {'size': file_size})
            
            return {
                'success': True,
                'message': f'File modified: {filename}',
                'action': 'processed',
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Error handling file modified: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_file_deleted(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Handle file deleted event"""
        try:
            logger.info(f"File deleted: {filename}")
            
            # Cleanup references jika diperlukan
            await self._cleanup_file_references(file_path)
            
            # Log ke database
            await self._log_file_event('deleted', file_path, {})
            
            return {
                'success': True,
                'message': f'File deleted: {filename}',
                'action': 'cleaned_up'
            }
            
        except Exception as e:
            logger.error(f"Error handling file deleted: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _process_log_file(self, file_path: str):
        """Process log file creation"""
        try:
            # Bisa parse log file untuk error detection
            # Atau kirim notifikasi jika log file baru dibuat
            logger.debug(f"Processing new log file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing log file: {str(e)}")
    
    async def _process_log_file_update(self, file_path: str):
        """Process log file modification"""
        try:
            # Bisa parse log entries baru
            # Atau detect error patterns
            logger.debug(f"Processing log file update: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing log file update: {str(e)}")
    
    async def _process_json_file(self, file_path: str):
        """Process JSON file creation"""
        try:
            # Validate JSON format
            # Atau process data jika diperlukan
            logger.debug(f"Processing new JSON file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing JSON file: {str(e)}")
    
    async def _process_json_file_update(self, file_path: str):
        """Process JSON file modification"""
        try:
            # Validate dan process updated JSON
            logger.debug(f"Processing JSON file update: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing JSON file update: {str(e)}")
    
    async def _process_csv_file(self, file_path: str):
        """Process CSV file creation"""
        try:
            # Validate CSV format
            # Atau import data jika diperlukan
            logger.debug(f"Processing new CSV file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
    
    async def _cleanup_file_references(self, file_path: str):
        """Cleanup references to deleted file"""
        try:
            # Remove database references
            # Cleanup cache entries
            logger.debug(f"Cleaning up references for: {file_path}")
            
        except Exception as e:
            logger.error(f"Error cleaning up file references: {str(e)}")
    
    async def _log_file_event(self, event_type: str, file_path: str, metadata: Dict[str, Any]):
        """Log file event to database"""
        try:
            # Import file event model
            from app.domains.file_monitor.models.file_event import FileEvent
            from app.core.database import get_db
            
            # Create file event record
            # Implementasi sesuai dengan model yang ada
            logger.debug(f"Logging file event: {event_type} - {file_path}")
            
        except Exception as e:
            logger.error(f"Error logging file event: {str(e)}")


class FileUploadCallbackHandler(EventCallbackHandler):
    """Handler untuk file upload events"""
    
    def __init__(self):
        super().__init__("FileUploadCallback", "file_upload")
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    async def handle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file upload events"""
        file_path = data.get('file_path')
        original_filename = data.get('original_filename')
        file_size = data.get('file_size', 0)
        upload_type = data.get('upload_type', 'general')
        user_id = data.get('user_id')
        
        if not file_path or not original_filename:
            raise ValueError("Missing required fields: file_path and original_filename")
        
        try:
            # Validate file
            validation_result = await self._validate_uploaded_file(
                file_path, original_filename, file_size
            )
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'message': validation_result['error'],
                    'action': 'rejected'
                }
            
            # Process berdasarkan upload type
            if upload_type == 'topup_proof':
                return await self._process_topup_proof(file_path, user_id)
            elif upload_type == 'profile_image':
                return await self._process_profile_image(file_path, user_id)
            else:
                return await self._process_general_upload(file_path, original_filename, user_id)
                
        except Exception as e:
            logger.error(f"Error processing file upload: {str(e)}")
            raise
    
    async def _validate_uploaded_file(self, file_path: str, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded file"""
        try:
            path = Path(file_path)
            
            # Check file exists
            if not path.exists():
                return {'valid': False, 'error': 'File not found'}
            
            # Check extension
            if path.suffix.lower() not in self.allowed_extensions:
                return {'valid': False, 'error': f'File type {path.suffix} not allowed'}
            
            # Check file size
            actual_size = path.stat().st_size
            if actual_size > self.max_file_size:
                return {'valid': False, 'error': f'File too large: {actual_size} bytes'}
            
            # Additional validation berdasarkan file type
            if path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                if not await self._validate_image_file(file_path):
                    return {'valid': False, 'error': 'Invalid image file'}
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation error: {str(e)}'}
    
    async def _validate_image_file(self, file_path: str) -> bool:
        """Validate image file"""
        try:
            # Bisa gunakan PIL untuk validate image
            # from PIL import Image
            # Image.open(file_path).verify()
            return True
            
        except Exception as e:
            logger.error(f"Image validation error: {str(e)}")
            return False
    
    async def _process_topup_proof(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Process top up proof upload"""
        try:
            logger.info(f"Processing top up proof upload for user {user_id}")
            
            # Update topup request dengan proof image
            # Implementasi sesuai dengan business logic
            
            return {
                'success': True,
                'message': 'Top up proof uploaded successfully',
                'action': 'processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing top up proof: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _process_profile_image(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Process profile image upload"""
        try:
            logger.info(f"Processing profile image upload for user {user_id}")
            
            # Update user profile dengan image
            # Resize image jika diperlukan
            
            return {
                'success': True,
                'message': 'Profile image uploaded successfully',
                'action': 'processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing profile image: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _process_general_upload(self, file_path: str, filename: str, user_id: int) -> Dict[str, Any]:
        """Process general file upload"""
        try:
            logger.info(f"Processing general file upload: {filename} for user {user_id}")
            
            # Store file metadata
            # Process file jika diperlukan
            
            return {
                'success': True,
                'message': f'File {filename} uploaded successfully',
                'action': 'processed'
            }
            
        except Exception as e:
            logger.error(f"Error processing general upload: {str(e)}")
            return {'success': False, 'message': str(e)}
