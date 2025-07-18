"""
Prefect Database Cleanup Manager

Simple, powerful database cleanup for Prefect deployments.
Inspired by Stripe's philosophy: minimal code, maximum impact.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from sqlalchemy import create_engine, text
from prefect.settings import PREFECT_API_DATABASE_CONNECTION_URL

logger = logging.getLogger(__name__)


class PrefectCleanup:
    """
    Dead simple Prefect database cleanup.
    
    Usage:
        cleanup = PrefectCleanup()
        cleanup.run(days=30)  # Keep last 30 days
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize with database connection."""
        self.db_url = database_url or str(PREFECT_API_DATABASE_CONNECTION_URL.value())
        # Force sync engine to avoid async issues
        self.engine = create_engine(self.db_url, future=True)
        
    def run(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old data. Keep only last N days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Dict with cleanup statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        logger.info(f"Cleaning data older than {cutoff_date}")
        
        stats = {}
        
        # Clean tables in correct order (respecting foreign keys)
        tables = [
            "log",
            "task_run_state", 
            "task_run",
            "flow_run_state",
            "flow_run",
            "event_resources",
            "events",
            "artifact"
        ]
        
        with self.engine.connect() as conn:
            for table in tables:
                result = conn.execute(
                    text(f"DELETE FROM {table} WHERE created < :cutoff"),
                    {"cutoff": cutoff_date}
                )
                stats[table] = result.rowcount
                
            conn.commit()
            
        logger.info(f"Cleanup completed: {stats}")
        return stats
        
    def size(self) -> Dict[str, int]:
        """Get database size statistics."""
        with self.engine.connect() as conn:
            # This works for both SQLite and PostgreSQL
            tables = ["log", "task_run", "flow_run", "events", "artifact"]
            stats = {}
            
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                stats[table] = result.scalar()
                
        return stats