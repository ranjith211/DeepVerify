import sqlite3

conn = sqlite3.connect('deepverify.db')
cursor = conn.cursor()

try:
    # Check existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Add password_hash column
    if 'password_hash' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        print("✓ Added password_hash column")
    else:
        print("✓ password_hash column already exists")
    
    # Add kyc_status column
    if 'kyc_status' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN kyc_status TEXT DEFAULT 'not_started'")
        print("✓ Added kyc_status column")
    else:
        print("✓ kyc_status column already exists")
    
    conn.commit()
    print("\n✓ Authentication migration completed successfully!")
    
except Exception as e:
    conn.rollback()
    print(f"✗ Error during migration: {e}")
finally:
    conn.close()
