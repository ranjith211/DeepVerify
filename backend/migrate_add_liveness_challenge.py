"""
Migration script to add liveness_challenge column to verification_logs table
"""

import sqlite3
import os

DB_PATH = "./deepverify.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(verification_logs)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'liveness_challenge' in columns:
            print("✓ Column 'liveness_challenge' already exists")
        else:
            # Add the new column
            cursor.execute("""
                ALTER TABLE verification_logs 
                ADD COLUMN liveness_challenge TEXT
            """)
            conn.commit()
            print("✓ Added 'liveness_challenge' column to verification_logs table")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Running migration: Add liveness_challenge column")
    migrate()
    print("Migration complete!")
