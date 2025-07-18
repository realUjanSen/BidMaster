#!/usr/bin/env python3
"""
Database setup script - runs the SQL setup file
"""
import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        # Read the SQL setup file
        with open('setup_fixed_database.sql', 'r') as file:
            sql_script = file.read()
        
        # Database connection parameters (without database name first)
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
        }
        
        print("Connecting to MySQL server...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Split the SQL script into individual statements
        statements = sql_script.split(';')
        
        print("Executing SQL statements...")
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✓ Executed statement {i+1}")
                except Error as e:
                    print(f"✗ Error in statement {i+1}: {e}")
                    print(f"Statement was: {statement[:100]}...")
        
        # Commit the changes
        connection.commit()
        print("✓ Database setup completed successfully!")
        
        # Test the setup
        cursor.execute("USE online_auction")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if sample data was inserted
        cursor.execute("SELECT COUNT(*) FROM auctions")
        auction_count = cursor.fetchone()[0]
        print(f"✓ Inserted {auction_count} sample auctions")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Inserted {user_count} sample users")
        
    except Error as e:
        print(f"✗ Database setup error: {e}")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ Database connection closed")

if __name__ == "__main__":
    setup_database()
