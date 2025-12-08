"""
Migration script to add rejection_reason column to verification_logs
"""
import sqlite3
from pathlib import Path

def migrate_database():
    db_path = Path(__file__).parent / "deepverify.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(verification_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add rejection_reason column if it doesn't exist
        if 'rejection_reason' not in columns:
            print("Adding rejection_reason column...")
            cursor.execute("""
                ALTER TABLE verification_logs 
                ADD COLUMN rejection_reason TEXT
            """)
            print("✓ Added rejection_reason column")
            
            # Migrate existing admin_notes to rejection_reason for rejected submissions
            print("Migrating existing rejection notes...")
            cursor.execute("""
                UPDATE verification_logs 
                SET rejection_reason = admin_notes 
                WHERE admin_status = 'rejected' AND admin_notes IS NOT NULL
            """)
            rows_updated = cursor.rowcount
            print(f"✓ Migrated {rows_updated} existing rejection(s)")
            
            # Clear admin_notes for rejected submissions (keep only short admin note)
            cursor.execute("""
                UPDATE verification_logs 
                SET admin_notes = 'Rejected - see rejection_reason for details' 
                WHERE admin_status = 'rejected' AND rejection_reason IS NOT NULL
            """)
            
        else:
            print("✓ rejection_reason column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Adding rejection_reason Column")
    print("="*60)
    migrate_database()
