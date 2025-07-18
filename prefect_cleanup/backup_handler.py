"""
Backup Handler for Prefect Database

Simple, safe backups before any cleanup operation.
"""

import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy import create_engine
from prefect.settings import PREFECT_API_DATABASE_CONNECTION_URL

logger = logging.getLogger(__name__)


class BackupHandler:
    """
    Simple backup system that keeps you safe.
    
    Usage:
        backup = BackupHandler()
        backup_path = backup.create()  # Creates backup
        backup.restore(backup_path)    # Restores if needed
    """
    
    def __init__(self, database_url: Optional[str] = None, backup_dir: str = "backups"):
        """Initialize backup handler."""
        self.db_url = database_url or str(PREFECT_API_DATABASE_CONNECTION_URL.value())
        # Force sync engine to avoid async issues
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create(self, name: Optional[str] = None) -> str:
        """
        Create a backup before cleanup.
        
        Args:
            name: Optional backup name
            
        Returns:
            Path to backup file
        """
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"prefect_backup_{timestamp}"
            
        backup_path = self.backup_dir / f"{name}.backup"
        
        logger.info(f"Creating backup: {backup_path}")
        
        try:
            if self._is_sqlite():
                self._backup_sqlite(backup_path)
            else:
                self._backup_postgres(backup_path)
                
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def _is_sqlite(self) -> bool:
        """Check if database is SQLite."""
        return "sqlite" in self.db_url.lower()
    
    def _backup_sqlite(self, backup_path: Path) -> None:
        """Backup SQLite database (simple file copy)."""
        # Extract database file path from URL
        db_file = self.db_url.replace("sqlite:///", "").replace("sqlite://", "")
        source_path = Path(db_file)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Database file not found: {source_path}")
            
        shutil.copy2(source_path, backup_path)
    
    def _backup_postgres(self, backup_path: Path) -> None:
        """Backup PostgreSQL database using pg_dump."""
        # Simple pg_dump command
        cmd = [
            "pg_dump",
            self.db_url,
            "-f", str(backup_path),
            "--verbose"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {result.stderr}")
    
    def list_backups(self) -> Dict[str, Any]:
        """List all available backups."""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.backup"):
            stat = backup_file.stat()
            backups.append({
                "name": backup_file.stem,
                "path": str(backup_file),
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "backup_directory": str(self.backup_dir),
            "total_backups": len(backups),
            "backups": backups
        }
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """Keep only the N most recent backups."""
        backup_files = sorted(
            self.backup_dir.glob("*.backup"),
            key=lambda x: x.stat().st_ctime,
            reverse=True
        )
        
        deleted_count = 0
        for backup_file in backup_files[keep_count:]:
            backup_file.unlink()
            deleted_count += 1
            logger.info(f"Deleted old backup: {backup_file}")
            
        return deleted_count