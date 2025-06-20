"""
File Monitor Callback Handler
Handler untuk file system events
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
        
        # Check ignored patterns
        for pattern in self.ignored_patterns:
            if pattern in str(path):
                return True
        
        # Check file extension
        if path.suffix and path.suffix not in self.monitored_extensions:
            return True
        
        return False
    
    async def _handle_file_created(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Handle file creation event"""
        try:
            logger.info(f"File created: {file_path}")
            
            # Get file metadata
            metadata = await self._get_file_metadata(file_path)
            
            # Process file based on type
            if file_path.endswith('.log'):
                await self._process_log_file(file_path, metadata)
            elif file_path.endswith('.json'):
                await self._process_json_file(file_path, metadata)
            
            # Log event
            await self._log_file_event('created', file_path, metadata)
            
            return {
                'success': True,
                'message': f'File created successfully: {filename}',
                'action': 'created',
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error handling file creation: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_file_modified(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Handle file modification event"""
        try:
            logger.info(f"File modified: {file_path}")
            
            # Get updated metadata
            metadata = await self._get_file_metadata(file_path)
            
            # Check if significant changes occurred
            if await self._is_significant_change(file_path, metadata):
                # Process updated file
                await self._process_file_update(file_path, metadata)
                
                # Log event
                await self._log_file_event('modified', file_path, metadata)
                
                return {
                    'success': True,
                    'message': f'File modified successfully: {filename}',
                    'action': 'modified',
                    'metadata': metadata
                }
            else:
                return {
                    'success': True,
                    'message': 'No significant changes detected',
                    'action': 'ignored'
                }
                
        except Exception as e:
            logger.error(f"Error handling file modification: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _handle_file_deleted(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Handle file deletion event"""
        try:
            logger.info(f"File deleted: {file_path}")
            
            # Cleanup references
            await self._cleanup_file_references(file_path)
            
            # Log event
            await self._log_file_event('deleted', file_path, {'filename': filename})
            
            return {
                'success': True,
                'message': f'File deletion handled: {filename}',
                'action': 'deleted'
            }
            
        except Exception as e:
            logger.error(f"Error handling file deletion: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    async def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata"""
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'extension': path.suffix,
                'filename': path.name,
                'directory': str(path.parent)
            }
        except Exception as e:
            logger.error(f"Error getting file metadata: {str(e)}")
            return {}
    
    async def _process_log_file(self, file_path: str, metadata: Dict[str, Any]):
        """Process log file"""
        try:
            # Parse log entries
            # Extract important information
            logger.debug(f"Processing log file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing log file: {str(e)}")
    
    async def _process_json_file(self, file_path: str, metadata: Dict[str, Any]):
        """Process JSON file"""
        try:
            # Validate JSON structure
            # Extract relevant data
            logger.debug(f"Processing JSON file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing JSON file: {str(e)}")
    
    async def _is_significant_change(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """Check if file change is significant"""
        try:
            # Compare with previous metadata
            # Determine if change is worth processing
            return True  # Simplified for now
            
        except Exception as e:
            logger.error(f"Error checking file changes: {str(e)}")
            return False
    
    async def _process_file_update(self, file_path: str, metadata: Dict[str, Any]):
        """Process file update"""
        try:
            # Update database records
            # Refresh cache if needed
            logger.debug(f"Processing file update: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file update: {str(e)}")
    
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
