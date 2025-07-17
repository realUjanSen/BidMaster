import mysql.connector
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'online_auction'
}

def check_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=== CHECKING DATABASE CONTENT ===")
        
        # Check auctions
        cursor.execute("SELECT id, title, status, seller_id FROM auctions ORDER BY id")
        auctions = cursor.fetchall()
        print(f"\nAUCTIONS ({len(auctions)} total):")
        for auction in auctions:
            print(f"  ID: {auction['id']}, Title: '{auction['title']}', Status: {auction['status']}, Seller: {auction['seller_id']}")
        
        # Check users
        cursor.execute("SELECT id, name, email FROM users ORDER BY id")
        users = cursor.fetchall()
        print(f"\nUSERS ({len(users)} total):")
        for user in users:
            print(f"  ID: {user['id']}, Name: '{user['name']}', Email: {user['email']}")
        
        # Check bids
        cursor.execute("SELECT COUNT(*) as count FROM bids")
        bid_count = cursor.fetchone()
        print(f"\nBIDS: {bid_count['count']} total")
        
        # Check watchlist
        cursor.execute("SELECT COUNT(*) as count FROM watchlist")
        watchlist_count = cursor.fetchone()
        print(f"WATCHLIST: {watchlist_count['count']} total")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_database()
