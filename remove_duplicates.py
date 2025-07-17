#!/usr/bin/env python3
"""
Remove duplicate auctions - keep only the first 5 unique auctions
"""
import mysql.connector
from mysql.connector import Error

def remove_duplicate_auctions():
    try:
        # Database connection
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'online_auction'
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("Removing duplicate auctions...")
        
        # Delete duplicate auctions (keep IDs 11-15, remove 16-20)
        cursor.execute("DELETE FROM bids WHERE auction_id IN (16, 17, 18, 19, 20)")
        cursor.execute("DELETE FROM auctions WHERE id IN (16, 17, 18, 19, 20)")
        
        connection.commit()
        print("✓ Removed duplicate auctions (IDs 16-20)")
        
        # Show remaining auctions
        cursor.execute("SELECT id, title FROM auctions ORDER BY id")
        auctions = cursor.fetchall()
        print(f"\nRemaining auctions ({len(auctions)}):")
        for auction in auctions:
            print(f"ID {auction[0]}: {auction[1]}")
        
    except Error as e:
        print(f"✗ Error removing duplicates: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ Database connection closed")

if __name__ == "__main__":
    remove_duplicate_auctions()
