"""
Migration script to add detailed analysis columns to verification
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
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(verification_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add document_analysis column if it doesn't exist
        if 'document_analysis' not in columns:
            print("Adding document_analysis column...")
            cursor.execute("""
                ALTER TABLE verification_logs 
                ADD COLUMN document_analysis TEXT
            """)
            print("✓ Added document_analysis column")
        else:
            print("✓ document_analysis column already exists")
        
        # Add liveness_analysis column if it doesn't exist
        if 'liveness_analysis' not in columns:
            print("Adding liveness_analysis column...")
            cursor.execute("""
                ALTER TABLE verification_logs 
                ADD COLUMN liveness_analysis TEXT
            """)
            print("✓ Added liveness_analysis column")
        else:
            print("✓ liveness_analysis column already exists")
        
        # Add compliance_analysis column if it doesn't exist
        if 'compliance_analysis' not in columns:
            print("Adding compliance_analysis column...")
            cursor.execute("""
                ALTER TABLE verification_logs 
                ADD COLUMN compliance_analysis TEXT
            """)
            print("✓ Added compliance_analysis column")
        else:
            print("✓ compliance_analysis column already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*60)
    print("Database Migration: Adding Analysis Columns")
    print("="*60)
    migrate_database()
