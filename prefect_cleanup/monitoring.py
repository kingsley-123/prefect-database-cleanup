"""
Database Monitoring for Prefect

Simple monitoring that tells you what you need to know.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, text
from prefect.settings import PREFECT_API_DATABASE_CONNECTION_URL

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """
    Simple database monitoring.
    
    Usage:
        monitor = DatabaseMonitor()
        stats = monitor.health_check()
        if stats['needs_cleanup']:
            print("Time to clean up!")
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize monitor with database connection."""
        self.db_url = database_url or str(PREFECT_API_DATABASE_CONNECTION_URL.value())
        # Force sync engine to avoid async issues
        self.engine = create_engine(self.db_url, future=True)
        
    def health_check(self) -> Dict[str, Any]:
        """
        Simple health check that tells you everything important.
        
        Returns:
            Dict with size, recommendations, and alerts
        """
        with self.engine.connect() as conn:
            # Get row counts for main tables
            tables = {
                "logs": "log",
                "flow_runs": "flow_run", 
                "task_runs": "task_run",
                "events": "events"
            }
            
            counts = {}
            for name, table in tables.items():
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    counts[name] = result.scalar()
                except Exception as e:
                    counts[name] = f"Error: {e}"
            
            # Calculate total records
            total_records = sum(v for v in counts.values() if isinstance(v, int))
            
            # Simple recommendations
            needs_cleanup = total_records > 100000  # 100k records
            is_large = total_records > 500000      # 500k records
            
            recommendation = self._get_recommendation(total_records)
            
        return {
            "timestamp": datetime.now().isoformat(),
            "table_counts": counts,
            "total_records": total_records,
            "needs_cleanup": needs_cleanup,
            "is_large": is_large,
            "recommendation": recommendation,
            "status": "healthy" if not needs_cleanup else "attention_needed"
        }
    
    def _get_recommendation(self, total_records: int) -> str:
        """Get simple, actionable recommendation."""
        if total_records < 10000:
            return "Database is small and healthy"
        elif total_records < 100000:
            return "Database is growing but fine"
        elif total_records < 500000:
            return "Consider monthly cleanup (30 days retention)"
        elif total_records < 1000000:
            return "Recommend weekly cleanup (7 days retention)"
        else:
            return "URGENT: Database is very large, cleanup immediately"
    
    def size_summary(self) -> str:
        """Get a human-readable size summary."""
        health = self.health_check()
        total = health["total_records"]
        status = health["status"]
        rec = health["recommendation"]
        
        return f"""
Database Status: {status.upper()}
Total Records: {total:,}
Recommendation: {rec}

Table Breakdown:
{chr(10).join(f"  {name}: {count:,}" if isinstance(count, int) else f"  {name}: {count}" for name, count in health["table_counts"].items())}
        """.strip()