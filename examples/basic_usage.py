"""
Basic Usage Examples for Prefect Database Cleanup

Simple examples showing how to clean up your Prefect database
and save storage costs.
"""

from prefect_cleanup import PrefectCleanup, DatabaseMonitor, BackupHandler, quick_cleanup


def example_1_simple_cleanup():
    """Example 1: Simple one-line cleanup."""
    print("=== Example 1: Simple Cleanup ===")
    
    # One line to clean up and backup
    stats = quick_cleanup(days=30, backup=True)
    print(f"Cleaned up {sum(stats.values())} old records")


def example_2_monitoring_first():
    """Example 2: Check database health before cleanup."""
    print("\n=== Example 2: Monitor Then Clean ===")
    
    # Check database health first
    monitor = DatabaseMonitor()
    health = monitor.health_check()
    
    print(f"Database status: {health['status']}")
    print(f"Total records: {health['total_records']:,}")
    print(f"Recommendation: {health['recommendation']}")
    
    # Clean only if needed
    if health['needs_cleanup']:
        print("Cleanup needed! Running cleanup...")
        cleanup = PrefectCleanup()
        stats = cleanup.run(days=30)
        print(f"Cleanup completed: {stats}")
    else:
        print("Database is healthy, no cleanup needed.")


def example_3_advanced_usage():
    """Example 3: Advanced usage with custom settings."""
    print("\n=== Example 3: Advanced Usage ===")
    
    # Create backup first
    backup = BackupHandler()
    backup_path = backup.create(name="before_cleanup")
    print(f"Backup created: {backup_path}")
    
    # Run cleanup with custom retention
    cleanup = PrefectCleanup()
    
    # Keep only last 7 days (aggressive cleanup)
    stats = cleanup.run(days=7)
    print(f"Aggressive cleanup completed: {stats}")
    
    # Show final database size
    final_size = cleanup.size()
    print(f"Final database size: {final_size}")


def example_4_production_workflow():
    """Example 4: Production-ready workflow."""
    print("\n=== Example 4: Production Workflow ===")
    
    try:
        # Step 1: Monitor
        monitor = DatabaseMonitor()
        health = monitor.health_check()
        print(f"Health check: {health['status']}")
        
        # Step 2: Backup (always backup in production!)
        backup = BackupHandler()
        backup_path = backup.create()
        print(f"Backup created: {backup_path}")
        
        # Step 3: Cleanup based on environment
        cleanup = PrefectCleanup()
        
        # Production: keep 30 days
        # Staging: keep 7 days  
        # Development: keep 1 day
        retention_days = 30  # Adjust for your environment
        
        stats = cleanup.run(days=retention_days)
        print(f"Production cleanup completed: {stats}")
        
        # Step 4: Cleanup old backups (keep last 5)
        backup.cleanup_old_backups(keep_count=5)
        print("Old backups cleaned up")
        
        print("Production workflow completed successfully!")
        
    except Exception as e:
        print(f"Error in production workflow: {e}")
        print("Database was backed up and remains unchanged")


if __name__ == "__main__":
    """Run all examples."""
    print("Prefect Database Cleanup - Usage Examples")
    print("=========================================")
    
    # Run all examples
    example_1_simple_cleanup()
    example_2_monitoring_first()
    example_3_advanced_usage()
    example_4_production_workflow()
    
    print("\n All examples completed!")
    print("\nFor your production environment:")
    print("1. Always backup before cleanup")
    print("2. Monitor database health regularly")  
    print("3. Choose appropriate retention period")
    print("4. Test with staging environment first")