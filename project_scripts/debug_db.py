#!/usr/bin/env python3
"""
Debug script to test database connectivity and registration functionality
"""
import mysql.connector
import mysql.connector.errorcode
from datetime import datetime
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'online_auction'
}

def test_db_connection():
    """Test database connection"""
    try:
        print("=== TESTING DATABASE CONNECTION ===")
        conn = mysql.connector.connect(**DB_CONFIG)
        print("✓ Database connection successful")
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✓ MySQL version: {version[0]}")
        
        cursor.execute("SELECT DATABASE()")
        database = cursor.fetchone()
        print(f"✓ Current database: {database[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        # If database does not exist, attempt to create it
        if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print(f"✗ Database '{DB_CONFIG['database']}' not found. Attempting to create it...")
            try:
                # Connect without specifying database
                tmp_cfg = DB_CONFIG.copy()
                tmp_cfg.pop('database')
                conn2 = mysql.connector.connect(**tmp_cfg)
                cursor2 = conn2.cursor()
                cursor2.execute(f"CREATE DATABASE `{DB_CONFIG['database']}`;")
                print(f"✓ Database '{DB_CONFIG['database']}' created successfully.")
                cursor2.close()
                conn2.close()
                print("Please re-run this script to verify setup.")
                print("Now run 'setup_complete_database.sql' or execute setup_database.bat to create tables and sample data.")
                sys.exit(1)
            except Exception as e2:
                print(f"✗ Failed to create database: {e2}")
        else:
            print(f"✗ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_table_structure():
    """Test table structure"""
    try:
        print("\n=== TESTING TABLE STRUCTURE ===")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        print("Users table columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} {'(NOT NULL)' if col[2] == 'NO' else ''}")
        
        # Check if balance_transactions table exists
        cursor.execute("SHOW TABLES LIKE 'balance_transactions'")
        if cursor.fetchone():
            print("\n✓ balance_transactions table exists")
        else:
            print("\n✗ balance_transactions table missing")
            
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        # If tables missing, prompt to load schema
        if e.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:
            print(f"✗ Tables not found in database. Please run 'setup_complete_database.sql' or 'setup_database.bat' to create tables.")
            sys.exit(1)
        print(f"✗ Table structure check failed: {e}")
        return False

def test_sample_insert():
    """Test sample data insertion"""
    try:
        print("\n=== TESTING SAMPLE DATA INSERTION ===")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Try to insert a test user
        test_user = {
            'name': 'Test User',
            'email': f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}@example.com',
            'password_hash': 'test123',
            'gov_id_last4': '1234',
            'phone': '555-0123',
            'balance': 1000.00,
            'is_verified': True,
            'created_at': datetime.now()
        }
        
        print(f"Inserting test user: {test_user['name']} ({test_user['email']})")
        
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, gov_id_last4, phone, balance, is_verified, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_user['name'],
            test_user['email'],
            test_user['password_hash'],
            test_user['gov_id_last4'],
            test_user['phone'],
            test_user['balance'],
            test_user['is_verified'],
            test_user['created_at']
        ))
        
        user_id = cursor.lastrowid
        print(f"✓ Test user inserted successfully with ID: {user_id}")
        
        # Try to insert a balance transaction
        cursor.execute("""
            INSERT INTO balance_transactions (user_id, transaction_type, amount, description)
            VALUES (%s, %s, %s, %s)
        """, (user_id, 'recharge', 1000.00, 'Test transaction'))
        
        transaction_id = cursor.lastrowid
        print(f"✓ Test transaction inserted successfully with ID: {transaction_id}")
        
        conn.commit()
        
        # Clean up - delete test data
        cursor.execute("DELETE FROM balance_transactions WHERE id = %s", (transaction_id,))
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        
        print("✓ Test data cleaned up")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ Sample data insertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def check_existing_data():
    """Check existing data in tables"""
    try:
        print("\n=== CHECKING EXISTING DATA ===")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check users count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Users in database: {user_count}")
        
        # Check balance transactions count
        cursor.execute("SELECT COUNT(*) FROM balance_transactions")
        transaction_count = cursor.fetchone()[0]
        print(f"Balance transactions in database: {transaction_count}")
        
        # Show sample users
        cursor.execute("SELECT id, name, email, balance, created_at FROM users LIMIT 5")
        users = cursor.fetchall()
        print("\nSample users:")
        for user in users:
            print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Balance: ${user[3]:.2f}, Created: {user[4]}")
        
        cursor.close()
        conn.close()
        return True
        
    except mysql.connector.Error as e:
        print(f"✗ Data check failed: {e}")
        return False

def main():
    """Main test function"""
    print("BidMaster Database Debug Script")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_db_connection,
        test_table_structure,
        test_sample_insert,
        check_existing_data
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with unexpected error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    if all(results):
        print("✓ All tests passed! Database is working correctly.")
        print("\nYou can now run the Flask application:")
        print("python app.py")
    else:
        print("✗ Some tests failed. Please check the output above.")
        print("\nCommon issues:")
        print("1. Make sure MySQL is running")
        print("2. Check database credentials in DB_CONFIG")
        print("3. Ensure the 'online_auction' database exists")
        print("4. Run the database_updates.sql script")

if __name__ == "__main__":
    main()
