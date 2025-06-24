"""
Logging system untuk pemecahan file admin refactoring
"""
import logging
import datetime
from typing import Dict, List

class RefactoringLogger:
    """Logger khusus untuk tracking pemecahan file"""
    
    def __init__(self):
        self.logger = logging.getLogger('admin_refactoring')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('admin_refactoring.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.split_files = []
    
    def log_file_split(self, original_file: str, original_lines: int, split_files: List[Dict[str, int]]):
        """Log pemecahan file"""
        timestamp = datetime.datetime.now().isoformat()
        
        self.logger.info(f"=== PEMECAHAN FILE ===")
        self.logger.info(f"File asli: {original_file} ({original_lines} baris)")
        self.logger.info(f"Dipecah menjadi {len(split_files)} file:")
        
        total_new_lines = 0
        for file_info in split_files:
            filename = file_info['filename']
            lines = file_info['lines']
            total_new_lines += lines
            self.logger.info(f"  - {filename}: {lines} baris")
        
        self.logger.info(f"Total baris setelah pemecahan: {total_new_lines}")
        self.logger.info(f"Efisiensi: {((original_lines - total_new_lines) / original_lines * 100):.1f}% pengurangan")
        self.logger.info(f"Timestamp: {timestamp}")
        self.logger.info("=" * 50)
        
        # Store for tracking
        self.split_files.append({
            'original_file': original_file,
            'original_lines': original_lines,
            'split_files': split_files,
            'timestamp': timestamp
        })
    
    def get_summary(self) -> Dict:
        """Get summary of all splits"""
        return {
            'total_splits': len(self.split_files),
            'splits': self.split_files
        }

# Global instance
refactoring_logger = RefactoringLogger()
