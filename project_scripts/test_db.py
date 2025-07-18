#!/usr/bin/env python3
"""
Simple database connection test
"""
import mysql.connector
from mysql.connector import Error

def test_database_connection():
    try:
        # Database connection parameters
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Empty password
            'database': 'online_auction'
        }
        
        print("Testing database connection...")
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            print("✓ Successfully connected to MySQL database")
            
            cursor = connection.cursor()
            
            # Test if database exists
            cursor.execute("SHOW DATABASES LIKE 'online_auction'")
            result = cursor.fetchone()
            
            if result:
                print("✓ Database 'online_auction' exists")
                
                # Test if tables exist
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print(f"✓ Found {len(tables)} tables in database:")
                for table in tables:
                    print(f"  - {table[0]}")
                    
                # Test if auctions table has image_url column
                cursor.execute("DESCRIBE auctions")
                columns = cursor.fetchall()
                print("\n✓ Auctions table structure:")
                for column in columns:
                    print(f"  - {column[0]}: {column[1]}")
                    
                # Test if we have sample data
                cursor.execute("SELECT COUNT(*) FROM auctions")
                auction_count = cursor.fetchone()[0]
                print(f"\n✓ Total auctions in database: {auction_count}")
                
                if auction_count > 0:
                    cursor.execute("SELECT title, image_url FROM auctions LIMIT 3")
                    auctions = cursor.fetchall()
                    print("\n✓ Sample auctions:")
                    for auction in auctions:
                        print(f"  - {auction[0]}: {auction[1][:50]}...")
                        
            else:
                print("✗ Database 'online_auction' does not exist")
                
        else:
            print("✗ Failed to connect to MySQL database")
            
    except Error as e:
        print(f"✗ Database connection error: {e}")
        return
        
    finally:
        try:
            if 'connection' in locals() and connection.is_connected():
                cursor.close()
                connection.close()
                print("\n✓ Database connection closed")
        except:
            pass

if __name__ == "__main__":
    test_database_connection()
