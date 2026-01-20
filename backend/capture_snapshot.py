#!/usr/bin/env python3
"""
Score Snapshot Capture Script

This script captures a snapshot of the current compliance scores for historical tracking.
Run this script on a schedule (daily, weekly, etc.) to build trend data over time.

Usage:
    python capture_snapshot.py

Schedule with Windows Task Scheduler:
    1. Open Task Scheduler
    2. Create Basic Task
    3. Set trigger (e.g., Daily at midnight)
    4. Action: Start a program
       Program: C:\\path\\to\\python.exe
       Arguments: C:\\path\\to\\nist-csf-tracker\\backend\\capture_snapshot.py
       Start in: C:\\path\\to\\nist-csf-tracker\\backend
"""

from datetime import datetime
from sqlmodel import Session
from app.database import engine
from app.models import ScoreSnapshot, Control, Score
from app.services.scoring_service import ScoringService
from sqlmodel import select


def capture_snapshot():
    """Capture a snapshot of current scores."""
    with Session(engine) as session:
        try:
            print(f"[{datetime.now()}] Capturing score snapshot...")
            
            scoring_service = ScoringService(session)
            
            # Get current metrics
            overall_data = scoring_service.get_overall_score()
            function_rollups = scoring_service.get_function_rollups()
            category_rollups = scoring_service.get_category_rollups()
            score_distribution = scoring_service.get_score_distribution()
            
            # Build function scores dict
            function_scores_dict = {}
            for func in function_rollups:
                function_scores_dict[func["function"]] = round(func["average_score"] * 100)
            
            # Build category scores dict
            category_scores_dict = {}
            for cat in category_rollups:
                category_scores_dict[cat["category"]] = round(cat["average_score"] * 100)
            
            # Create snapshot
            snapshot = ScoreSnapshot(
                snapshot_date=datetime.utcnow(),
                overall_percentage=round(overall_data["average_score"] * 100),
                total_controls=overall_data["total_controls"],
                scored_controls=overall_data["controls_with_evidence"],
                function_scores=function_scores_dict,
                category_scores=category_scores_dict,
                score_distribution=score_distribution
            )
            
            session.add(snapshot)
            session.commit()
            
            print(f"✅ Snapshot captured successfully!")
            print(f"   Overall Score: {snapshot.overall_percentage}%")
            print(f"   Scored Controls: {snapshot.scored_controls}/{snapshot.total_controls}")
            print(f"   Distribution: {score_distribution}")
            
            return snapshot
            
        except Exception as e:
            print(f"❌ Error capturing snapshot: {e}")
            session.rollback()
            raise


def cleanup_old_snapshots(days_to_keep: int = 365):
    """
    Delete snapshots older than specified days.
    Keeps database size manageable for long-running deployments.
    """
    from datetime import timedelta
    
    with Session(engine) as session:
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            statement = select(ScoreSnapshot).where(
                ScoreSnapshot.snapshot_date < cutoff_date
            )
            old_snapshots = session.exec(statement).all()
            
            if old_snapshots:
                print(f"Cleaning up {len(old_snapshots)} old snapshots...")
                for snapshot in old_snapshots:
                    session.delete(snapshot)
                session.commit()
                print(f"✅ Cleanup complete")
            else:
                print("No old snapshots to clean up")
                
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            session.rollback()


if __name__ == "__main__":
    import sys
    
    # Allow cleanup mode via command line
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        print(f"Running cleanup mode (keeping last {days} days)...")
        cleanup_old_snapshots(days)
    else:
        # Normal snapshot mode
        snapshot = capture_snapshot()
        
        # Optional: also run cleanup to keep database size reasonable
        # Uncomment the line below to automatically cleanup on each run
        # cleanup_old_snapshots(365)
