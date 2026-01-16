"""
Clean up old control entries that used single-digit format (e.g., GV.OC-1 instead of GV.OC-01)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine
from app.models import Control

def cleanup_old_controls():
    """Remove old-style control entries to keep only NIST CSF 2.0 format."""
    
    with Session(engine) as session:
        # Get all controls
        controls = session.exec(select(Control)).all()
        
        print(f"Total controls in database: {len(controls)}")
        
        # Find controls with old single-digit format (e.g., -1, -2 instead of -01, -02)
        # These would be from the original seed before the full 106 were added
        old_format = []
        for control in controls:
            parts = control.csf_id.split('-')
            if len(parts) == 2:
                # Check if the last part is a single digit (1-9) without leading zero
                if len(parts[1]) == 1 and parts[1].isdigit():
                    old_format.append(control)
        
        print(f"\nFound {len(old_format)} controls with old single-digit format")
        
        if old_format:
            print("\nControls to be removed:")
            for ctrl in old_format[:10]:  # Show first 10
                print(f"  ID {ctrl.id}: {ctrl.csf_id} - {ctrl.name}")
            if len(old_format) > 10:
                print(f"  ... and {len(old_format) - 10} more")
            
            response = input(f"\nDelete these {len(old_format)} old-format controls? (yes/no): ")
            if response.lower() == 'yes':
                for ctrl in old_format:
                    session.delete(ctrl)
                session.commit()
                print(f"\n✓ Deleted {len(old_format)} old controls")
                
                # Verify final count
                remaining = len(session.exec(select(Control)).all())
                print(f"✓ Remaining controls: {remaining}")
            else:
                print("\nCancelled - no changes made")
        else:
            print("\n✓ No old-format controls found - database is clean!")
            
            # Show function breakdown
            from collections import Counter
            controls = session.exec(select(Control)).all()
            funcs = Counter([c.function for c in controls])
            print("\nControls by function:")
            for func, count in sorted(funcs.items()):
                print(f"  {func}: {count}")


if __name__ == "__main__":
    cleanup_old_controls()
