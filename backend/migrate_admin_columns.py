import sqlite3
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('deepverify.db')
cursor = conn.cursor()

try:
    # Check if columns exist
    cursor.execute("PRAGMA table_info(verification_logs)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add admin_status column if it doesn't exist
    if 'admin_status' not in columns:
        cursor.execute("ALTER TABLE verification_logs ADD COLUMN admin_status TEXT")
        print("✓ Added admin_status column")
    else:
        print("✓ admin_status column already exists")
    
    # Add admin_notes column if it doesn't exist
    if 'admin_notes' not in columns:
        cursor.execute("ALTER TABLE verification_logs ADD COLUMN admin_notes TEXT")
        print("✓ Added admin_notes column")
    else:
        print("✓ admin_notes column already exists")
    
    conn.commit()
    print("\n✓ Database migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"✗ Error during migration: {e}")
finally:
    conn.close()
