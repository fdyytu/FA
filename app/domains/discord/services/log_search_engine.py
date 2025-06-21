from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import re

from ..models.command_log import CommandLog

class LogSearchEngine:
    """Search engine untuk log data dengan indexing dan fast retrieval"""
    
    def __init__(self):
        # Index untuk fast search
        self.command_index: Dict[str, Set[int]] = defaultdict(set)
        self.user_index: Dict[str, Set[int]] = defaultdict(set)
        self.guild_index: Dict[str, Set[int]] = defaultdict(set)
        self.text_index: Dict[str, Set[int]] = defaultdict(set)
        self.date_index: Dict[str, Set[int]] = defaultdict(set)
        
        # Cache untuk logs yang sudah di-index
        self.indexed_logs: Dict[int, CommandLog] = {}
        self.last_index_update = datetime.now()
        
    def index_log(self, log: CommandLog):
        """Index single log untuk fast search"""
        log_id = log.id
        
        # Index berdasarkan command
        if log.command:
            self.command_index[log.command.lower()].add(log_id)
            
        # Index berdasarkan user
        if log.user_id:
            self.user_index[str(log.user_id)].add(log_id)
            
        # Index berdasarkan guild
        if log.guild_id:
            self.guild_index[str(log.guild_id)].add(log_id)
            
        # Index berdasarkan text content (command, response, error)
        text_content = []
        if log.command:
            text_content.append(log.command)
        if log.response:
            text_content.append(log.response)
        if log.error_message:
            text_content.append(log.error_message)
            
        for text in text_content:
            words = self._extract_words(text)
            for word in words:
                self.text_index[word.lower()].add(log_id)
                
        # Index berdasarkan tanggal
        if log.timestamp:
            date_key = log.timestamp.strftime('%Y-%m-%d')
            self.date_index[date_key].add(log_id)
            
        # Simpan log di cache
        self.indexed_logs[log_id] = log
        
    def bulk_index_logs(self, logs: List[CommandLog]):
        """Index multiple logs sekaligus"""
        for log in logs:
            self.index_log(log)
        self.last_index_update = datetime.now()
        
    def search_by_command(self, command: str) -> List[CommandLog]:
        """Search logs berdasarkan command"""
        log_ids = self.command_index.get(command.lower(), set())
        return [self.indexed_logs[log_id] for log_id in log_ids if log_id in self.indexed_logs]
        
    def search_by_user(self, user_id: str) -> List[CommandLog]:
        """Search logs berdasarkan user_id"""
        log_ids = self.user_index.get(str(user_id), set())
        return [self.indexed_logs[log_id] for log_id in log_ids if log_id in self.indexed_logs]
        
    def search_by_text(self, search_term: str) -> List[CommandLog]:
        """Search logs berdasarkan text content"""
        words = self._extract_words(search_term)
        matching_log_ids = set()
        
        for word in words:
            word_matches = self.text_index.get(word.lower(), set())
            if not matching_log_ids:
                matching_log_ids = word_matches.copy()
            else:
                matching_log_ids = matching_log_ids.intersection(word_matches)
                
        return [self.indexed_logs[log_id] for log_id in matching_log_ids if log_id in self.indexed_logs]
        
    def search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[CommandLog]:
        """Search logs berdasarkan rentang tanggal"""
        matching_log_ids = set()
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            date_key = current_date.strftime('%Y-%m-%d')
            date_matches = self.date_index.get(date_key, set())
            matching_log_ids.update(date_matches)
            current_date += timedelta(days=1)
            
        return [self.indexed_logs[log_id] for log_id in matching_log_ids if log_id in self.indexed_logs]
        
    def _extract_words(self, text: str) -> List[str]:
        """Extract words dari text untuk indexing"""
        if not text:
            return []
        # Remove special characters dan split berdasarkan whitespace
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 2]  # Skip kata pendek
        
    def get_index_stats(self) -> Dict[str, Any]:
        """Return statistik index"""
        return {
            "total_indexed_logs": len(self.indexed_logs),
            "command_terms": len(self.command_index),
            "text_terms": len(self.text_index),
            "users": len(self.user_index),
            "guilds": len(self.guild_index),
            "last_update": self.last_index_update.isoformat()
        }

# Global instance
log_search_engine = LogSearchEngine()
