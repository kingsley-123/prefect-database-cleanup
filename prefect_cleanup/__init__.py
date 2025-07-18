"""
Prefect Database Cleanup

Simple, powerful database cleanup for Prefect deployments.
Save storage costs and keep your database healthy.

Usage:
    from prefect_cleanup import PrefectCleanup
    
    # Simple cleanup
    cleanup = PrefectCleanup()
    cleanup.run(days=30)  # Keep last 30 days
    
    # With monitoring
    from prefect_cleanup import DatabaseMonitor
    monitor = DatabaseMonitor()
    if monitor.health_check()['needs_cleanup']:
        cleanup.run(days=30)
"""

from .cleanup_manager import PrefectCleanup
from .monitoring import DatabaseMonitor  
from .backup_handler import BackupHandler
from .retention_policies import RetentionPolicy, get_policy

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Simple, powerful database cleanup for Prefect deployments"

# Simple convenience function for quick cleanup
def quick_cleanup(days: int = 30, backup: bool = True) -> dict:
    """
    One-line cleanup for busy people.
    
    Args:
        days: Keep data from last N days
        backup: Create backup before cleanup
        
    Returns:
        Cleanup statistics
    """
    cleanup = PrefectCleanup()
    
    if backup:
        backup_handler = BackupHandler()
        backup_path = backup_handler.create()
        print(f"✅ Backup created: {backup_path}")
    
    stats = cleanup.run(days=days)
    print(f"✅ Cleanup completed: {sum(stats.values())} records removed")
    
    return stats


# Export main classes for easy import
__all__ = [
    "PrefectCleanup",
    "DatabaseMonitor", 
    "BackupHandler",
    "RetentionPolicy",
    "get_policy",
    "quick_cleanup"
]