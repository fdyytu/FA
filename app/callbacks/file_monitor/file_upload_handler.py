"""
File Upload Callback Handler
Handler untuk file upload events
"""
from typing import Dict, Any
from pathlib import Path
import logging

from app.callbacks.base.base_handlers import EventCallbackHandler

logger = logging.getLogger(__name__)


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
                    'message': validation_result['message'],
                    'action': 'rejected'
                }
            
            # Process upload based on type
            if upload_type == 'profile_image':
                return await self._handle_profile_image_upload(file_path, user_id)
            elif upload_type == 'document':
                return await self._handle_document_upload(file_path, original_filename, user_id)
            else:
                return await self._handle_general_upload(file_path, original_filename, user_id)
                
        except Exception as e:
            logger.error(f"Error processing file upload: {str(e)}")
            raise
    
    async def _validate_uploaded_file(self, file_path: str, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate uploaded file"""
        try:
            path = Path(file_path)
            
            # Check file extension
            if path.suffix.lower() not in self.allowed_extensions:
                return {
                    'valid': False,
                    'message': f'File type not allowed: {path.suffix}'
                }
            
            # Check file size
            if file_size > self.max_file_size:
                return {
                    'valid': False,
                    'message': f'File too large: {file_size} bytes (max: {self.max_file_size})'
                }
            
            # Check if file exists
            if not path.exists():
                return {
                    'valid': False,
                    'message': 'Uploaded file not found'
                }
            
            # Additional security checks
            security_check = await self._security_scan_file(file_path)
            if not security_check['safe']:
                return {
                    'valid': False,
                    'message': f'Security check failed: {security_check["reason"]}'
                }
            
            return {'valid': True, 'message': 'File validation passed'}
            
        except Exception as e:
            logger.error(f"Error validating file: {str(e)}")
            return {'valid': False, 'message': f'Validation error: {str(e)}'}
    
    async def _security_scan_file(self, file_path: str) -> Dict[str, Any]:
        """Perform security scan on uploaded file"""
        try:
            # Basic security checks
            path = Path(file_path)
            
            # Check for suspicious file names
            suspicious_patterns = ['..', '/', '\\', '<script>', '<?php']
            for pattern in suspicious_patterns:
                if pattern in path.name:
                    return {'safe': False, 'reason': f'Suspicious filename pattern: {pattern}'}
            
            # Check file content (basic)
            if path.suffix.lower() in {'.txt', '.json', '.csv'}:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1024)  # Read first 1KB
                        if '<script>' in content.lower() or '<?php' in content.lower():
                            return {'safe': False, 'reason': 'Suspicious content detected'}
                except:
                    pass  # Binary files will fail to read as text
            
            return {'safe': True, 'reason': 'Security scan passed'}
            
        except Exception as e:
            logger.error(f"Error in security scan: {str(e)}")
            return {'safe': False, 'reason': f'Security scan error: {str(e)}'}
    
    async def _handle_profile_image_upload(self, file_path: str, user_id: int) -> Dict[str, Any]:
        """Handle profile image upload"""
        try:
            # Resize image if needed
            processed_path = await self._process_profile_image(file_path)
            
            # Update user profile
            await self._update_user_profile_image(user_id, processed_path)
            
            # Log upload
            await self._log_upload_event('profile_image', file_path, user_id)
            
            return {
                'success': True,
                'message': 'Profile image uploaded successfully',
                'action': 'profile_updated',
                'file_path': processed_path
            }
            
        except Exception as e:
            logger.error(f"Error handling profile image upload: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_document_upload(self, file_path: str, filename: str, user_id: int) -> Dict[str, Any]:
        """Handle document upload"""
        try:
            # Store document metadata
            document_id = await self._store_document_metadata(file_path, filename, user_id)
            
            # Extract text content if possible
            await self._extract_document_content(file_path, document_id)
            
            # Log upload
            await self._log_upload_event('document', file_path, user_id)
            
            return {
                'success': True,
                'message': 'Document uploaded successfully',
                'action': 'document_stored',
                'document_id': document_id
            }
            
        except Exception as e:
            logger.error(f"Error handling document upload: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_general_upload(self, file_path: str, filename: str, user_id: int) -> Dict[str, Any]:
        """Handle general file upload"""
        try:
            # Store file metadata
            file_id = await self._store_file_metadata(file_path, filename, user_id)
            
            # Log upload
            await self._log_upload_event('general', file_path, user_id)
            
            return {
                'success': True,
                'message': 'File uploaded successfully',
                'action': 'file_stored',
                'file_id': file_id
            }
            
        except Exception as e:
            logger.error(f"Error handling general upload: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _process_profile_image(self, file_path: str) -> str:
        """Process profile image (resize, optimize)"""
        try:
            # Image processing logic
            # For now, return original path
            logger.debug(f"Processing profile image: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error processing profile image: {str(e)}")
            raise
    
    async def _update_user_profile_image(self, user_id: int, image_path: str):
        """Update user profile image in database"""
        try:
            # Database update logic
            logger.debug(f"Updating profile image for user {user_id}: {image_path}")
            
        except Exception as e:
            logger.error(f"Error updating user profile image: {str(e)}")
            raise
    
    async def _store_document_metadata(self, file_path: str, filename: str, user_id: int) -> int:
        """Store document metadata in database"""
        try:
            # Database storage logic
            logger.debug(f"Storing document metadata: {filename}")
            return 1  # Mock document ID
            
        except Exception as e:
            logger.error(f"Error storing document metadata: {str(e)}")
            raise
    
    async def _extract_document_content(self, file_path: str, document_id: int):
        """Extract text content from document"""
        try:
            # Content extraction logic
            logger.debug(f"Extracting content from document: {file_path}")
            
        except Exception as e:
            logger.error(f"Error extracting document content: {str(e)}")
    
    async def _store_file_metadata(self, file_path: str, filename: str, user_id: int) -> int:
        """Store general file metadata"""
        try:
            # Database storage logic
            logger.debug(f"Storing file metadata: {filename}")
            return 1  # Mock file ID
            
        except Exception as e:
            logger.error(f"Error storing file metadata: {str(e)}")
            raise
    
    async def _log_upload_event(self, upload_type: str, file_path: str, user_id: int):
        """Log upload event"""
        try:
            # Logging logic
            logger.info(f"Upload event: {upload_type} - {file_path} - User: {user_id}")
            
        except Exception as e:
            logger.error(f"Error logging upload event: {str(e)}")
