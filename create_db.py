import MySQLdb

# Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',  # Default XAMPP password
}

try:
    # Connect to MySQL Server
    db = MySQLdb.connect(**db_config)
    cursor = db.cursor()
    
    # Create Database
    cursor.execute("CREATE DATABASE IF NOT EXISTS hotelerie_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("Database 'hotelerie_db' created or already exists.")
    
except Exception as e:
    print(f"Error creating database: {e}")
finally:
    if 'db' in locals():
        db.close()
