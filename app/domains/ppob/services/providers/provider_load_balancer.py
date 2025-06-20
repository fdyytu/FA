from typing import List, Optional
import logging

from .provider_config import ProviderConfig, ProviderStatus


class ProviderLoadBalancer:
    """
    Load balancer untuk provider - Single Responsibility: Load balancing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._round_robin_index = 0
    
    def select_provider(
        self, 
        providers: List[ProviderConfig],
        strategy: str = "priority"
    ) -> Optional[ProviderConfig]:
        """
        Pilih provider berdasarkan strategi - Strategy Pattern
        """
        # Filter provider yang aktif dan sehat
        available_providers = [
            p for p in providers 
            if p.is_active and p.status == ProviderStatus.HEALTHY
        ]
        
        if not available_providers:
            self.logger.error("No healthy providers available")
            return None
        
        if strategy == "priority":
            return self._select_by_priority(available_providers)
        elif strategy == "round_robin":
            return self._select_round_robin(available_providers)
        elif strategy == "least_errors":
            return self._select_least_errors(available_providers)
        elif strategy == "random":
            return self._select_random(available_providers)
        else:
            return available_providers[0]
    
    def _select_by_priority(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih berdasarkan prioritas tertinggi (nilai priority terkecil)"""
        return min(providers, key=lambda p: p.priority)
    
    def _select_round_robin(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih berdasarkan round robin"""
        if not providers:
            return None
        
        # Sort providers by priority first for consistent ordering
        sorted_providers = sorted(providers, key=lambda p: p.priority)
        
        # Select using round robin
        selected = sorted_providers[self._round_robin_index % len(sorted_providers)]
        self._round_robin_index += 1
        
        return selected
    
    def _select_least_errors(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih provider dengan error paling sedikit"""
        return min(providers, key=lambda p: p.error_count)
    
    def _select_random(self, providers: List[ProviderConfig]) -> ProviderConfig:
        """Pilih provider secara random"""
        import random
        return random.choice(providers)
    
    def get_available_providers(self, providers: List[ProviderConfig]) -> List[ProviderConfig]:
        """Get list of available providers"""
        return [
            p for p in providers 
            if p.is_active and p.status == ProviderStatus.HEALTHY
        ]
    
    def get_provider_weights(self, providers: List[ProviderConfig]) -> dict:
        """Calculate provider weights based on priority and health"""
        weights = {}
        
        for provider in providers:
            if not provider.is_available():
                weights[provider.name] = 0
                continue
            
            # Higher priority (lower number) gets higher weight
            # Lower error count gets higher weight
            base_weight = 100 - provider.priority
            error_penalty = provider.error_count * 10
            weight = max(1, base_weight - error_penalty)
            
            weights[provider.name] = weight
        
        return weights
    
    def select_weighted_provider(self, providers: List[ProviderConfig]) -> Optional[ProviderConfig]:
        """Select provider based on weighted random selection"""
        import random
        
        available_providers = self.get_available_providers(providers)
        if not available_providers:
            return None
        
        weights = self.get_provider_weights(available_providers)
        total_weight = sum(weights.values())
        
        if total_weight == 0:
            return None
        
        # Weighted random selection
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for provider in available_providers:
            current_weight += weights[provider.name]
            if random_value <= current_weight:
                return provider
        
        # Fallback to first available provider
        return available_providers[0]
    
    def reset_round_robin(self):
        """Reset round robin counter"""
        self._round_robin_index = 0
