"""Background Tasks untuk Discord - Async processing untuk heavy operations"""
import logging
from typing import Dict, Any, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    def __init__(self, max_workers: int = 4):
        """Initialize background task manager dengan thread pool"""
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.running_tasks = {}
        self.task_results = {}
        self.lock = threading.Lock()

    def submit_task(self, task_id: str, func: Callable, *args, **kwargs) -> bool:
        """Submit task untuk background processing"""
        try:
            with self.lock:
                if task_id in self.running_tasks:
                    logger.warning(f"Task {task_id} already running")
                    return False
                future = self.executor.submit(self._execute_task, task_id, func, *args, **kwargs)
                self.running_tasks[task_id] = {'future': future, 'started_at': datetime.now(), 'status': 'running'}
                logger.info(f"Task {task_id} submitted for background processing")
                return True
        except Exception as e:
            logger.error(f"Failed to submit task {task_id}: {e}")
            return False
    def _execute_task(self, task_id: str, func: Callable, *args, **kwargs) -> Any:
        """Execute task dan simpan hasil"""
        try:
            result = func(*args, **kwargs)
            with self.lock:
                self.task_results[task_id] = {'result': result, 'status': 'completed', 'completed_at': datetime.now()}
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
            return result
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            with self.lock:
                self.task_results[task_id] = {'error': str(e), 'status': 'failed', 'completed_at': datetime.now()}
                if task_id in self.running_tasks:
                    del self.running_tasks[task_id]
            raise

# Global task manager instance
task_manager = BackgroundTaskManager()
