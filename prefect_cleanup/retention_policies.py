"""
Retention Policies for Prefect Database Cleanup

Simple policy definitions that anyone can understand and modify.
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import timedelta


@dataclass
class RetentionPolicy:
    """
    Simple retention policy.
    
    Usage:
        policy = RetentionPolicy.daily()
        policy = RetentionPolicy.custom(days=90)
    """
    days: int
    name: str
    
    @classmethod
    def daily(cls) -> 'RetentionPolicy':
        """Keep last 24 hours only."""
        return cls(days=1, name="daily")
    
    @classmethod 
    def weekly(cls) -> 'RetentionPolicy':
        """Keep last 7 days."""
        return cls(days=7, name="weekly")
        
    @classmethod
    def monthly(cls) -> 'RetentionPolicy':
        """Keep last 30 days."""
        return cls(days=30, name="monthly")
        
    @classmethod
    def quarterly(cls) -> 'RetentionPolicy':
        """Keep last 90 days."""
        return cls(days=90, name="quarterly")
        
    @classmethod
    def custom(cls, days: int, name: str = "custom") -> 'RetentionPolicy':
        """Custom retention period."""
        return cls(days=days, name=name)


# Pre-defined policies for common use cases
POLICIES = {
    "development": RetentionPolicy.daily(),
    "staging": RetentionPolicy.weekly(), 
    "production": RetentionPolicy.monthly(),
    "compliance": RetentionPolicy.quarterly(),
}


def get_policy(name: str) -> RetentionPolicy:
    """Get a predefined policy by name."""
    if name not in POLICIES:
        raise ValueError(f"Unknown policy: {name}. Available: {list(POLICIES.keys())}")
    return POLICIES[name]