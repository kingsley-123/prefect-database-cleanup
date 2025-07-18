"""
Tests for Prefect Database Cleanup

Simple tests that prove our code works.
"""

import pytest
import tempfile
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path

from prefect_cleanup import PrefectCleanup, DatabaseMonitor


class TestPrefectCleanup:
    """Test the main cleanup functionality."""
    
    def setup_method(self):
        """Create a test database for each test."""
        # Create temporary database
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_file.close()  # Close file handle to avoid Windows permission issues
        self.db_url = f"sqlite:///{self.db_file.name}"
        
        # Create test tables and data
        self._create_test_data()
        
    def teardown_method(self):
        """Clean up after each test."""
        # Give a moment for connections to close
        time.sleep(0.1)
        try:
            Path(self.db_file.name).unlink(missing_ok=True)
        except PermissionError:
            # On Windows, sometimes the file is still locked
            pass
        
    def _create_test_data(self):
        """Create test database with sample data."""
        conn = sqlite3.connect(self.db_file.name)
        cursor = conn.cursor()
        
        # Create all tables that cleanup expects (simplified Prefect schema)
        tables_to_create = [
            """CREATE TABLE log (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                message TEXT
            )""",
            """CREATE TABLE flow_run (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                name TEXT
            )""",
            """CREATE TABLE task_run (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                name TEXT
            )""",
            """CREATE TABLE task_run_state (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                state_type TEXT
            )""",
            """CREATE TABLE flow_run_state (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                state_type TEXT
            )""",
            """CREATE TABLE events (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                event_type TEXT
            )""",
            """CREATE TABLE event_resources (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                resource_id TEXT
            )""",
            """CREATE TABLE artifact (
                id INTEGER PRIMARY KEY,
                created TIMESTAMP,
                artifact_type TEXT
            )"""
        ]
        
        # Create all tables
        for table_sql in tables_to_create:
            cursor.execute(table_sql)
        
        # Add test data - some old, some new
        old_date = datetime.now() - timedelta(days=60)
        new_date = datetime.now() - timedelta(days=10)
        
        # Old data (should be cleaned)
        cursor.execute("INSERT INTO log (created, message) VALUES (?, ?)", 
                      (old_date, "Old log entry"))
        cursor.execute("INSERT INTO flow_run (created, name) VALUES (?, ?)", 
                      (old_date, "Old flow run"))
        
        # New data (should be kept)
        cursor.execute("INSERT INTO log (created, message) VALUES (?, ?)", 
                      (new_date, "New log entry"))
        cursor.execute("INSERT INTO flow_run (created, name) VALUES (?, ?)", 
                      (new_date, "New flow run"))
        
        conn.commit()
        conn.close()
        
    def test_cleanup_removes_old_data(self):
        """Test that cleanup removes old data but keeps recent data."""
        cleanup = PrefectCleanup(database_url=self.db_url)
        
        # Run cleanup (keep last 30 days)
        stats = cleanup.run(days=30)
        
        # Should have removed 1 log and 1 flow_run (the old ones)
        assert stats.get('log', 0) >= 1, "Should remove old log entries"
        assert stats.get('flow_run', 0) >= 1, "Should remove old flow runs"
        
        # Verify new data still exists
        conn = sqlite3.connect(self.db_file.name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM log")
        remaining_logs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM flow_run") 
        remaining_flows = cursor.fetchone()[0]
        
        conn.close()
        
        assert remaining_logs >= 1, "Should keep recent log entries"
        assert remaining_flows >= 1, "Should keep recent flow runs"
        
    def test_database_monitor(self):
        """Test database monitoring functionality."""
        monitor = DatabaseMonitor(database_url=self.db_url)
        
        health = monitor.health_check()
        
        # Check that health check returns expected fields
        assert 'table_counts' in health
        assert 'total_records' in health
        assert 'needs_cleanup' in health
        assert 'recommendation' in health
        assert 'status' in health
        
        # Should detect our test data
        assert health['total_records'] > 0
        
    def test_size_summary(self):
        """Test human-readable size summary."""
        monitor = DatabaseMonitor(database_url=self.db_url)
        
        summary = monitor.size_summary()
        
        # Should be a readable string
        assert isinstance(summary, str)
        assert 'Database Status' in summary
        assert 'Total Records' in summary


# Simple test runner
if __name__ == "__main__":
    # Run tests manually if pytest isn't available
    test = TestPrefectCleanup()
    
    print("Running tests...")
    
    test.setup_method()
    test.test_cleanup_removes_old_data()
    test.teardown_method()
    print("Cleanup test passed")
    
    test.setup_method()
    test.test_database_monitor()
    test.teardown_method()
    print("Monitor test passed")
    
    test.setup_method()
    test.test_size_summary()
    test.teardown_method()
    print("Summary test passed")
    
    print("All tests passed!")