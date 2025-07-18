#!/usr/bin/env python3
"""
Fix auction dates - set all auctions to end in late July 2025
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import random

def fix_auction_dates():
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
        
        print("Fixing auction dates...")
        
        # Get all auctions
        cursor.execute("SELECT id, title, start_time, end_time FROM auctions")
        auctions = cursor.fetchall()
        
        print(f"Found {len(auctions)} auctions to fix")
        
        # July 2025 end dates (25th to 31st)
        july_dates = [
            "2025-07-25 18:00:00",
            "2025-07-26 19:00:00", 
            "2025-07-27 20:00:00",
            "2025-07-28 17:00:00",
            "2025-07-29 21:00:00",
            "2025-07-30 16:00:00",
            "2025-07-31 19:30:00"
        ]
        
        # Update each auction with a random July end date
        for auction in auctions:
            auction_id = auction[0]
            title = auction[1]
            
            # Pick a random end date from July 2025
            new_end_date = random.choice(july_dates)
            
            # Set start time to current time (July 17, 2025)
            new_start_date = "2025-07-17 10:00:00"
            
            # Update the auction
            cursor.execute("""
                UPDATE auctions 
                SET start_time = %s, end_time = %s, status = 'active'
                WHERE id = %s
            """, (new_start_date, new_end_date, auction_id))
            
            print(f"✓ Updated '{title}' - ends {new_end_date}")
        
        connection.commit()
        print("✓ All auction dates fixed successfully!")
        
        # Show the updated auctions
        cursor.execute("SELECT id, title, start_time, end_time, status FROM auctions ORDER BY end_time")
        updated_auctions = cursor.fetchall()
        
        print("\n=== UPDATED AUCTIONS ===")
        for auction in updated_auctions:
            print(f"ID {auction[0]}: {auction[1]}")
            print(f"  Starts: {auction[2]}")
            print(f"  Ends: {auction[3]}")
            print(f"  Status: {auction[4]}")
            print()
        
    except Error as e:
        print(f"✗ Error fixing auction dates: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ Database connection closed")

if __name__ == "__main__":
    fix_auction_dates()
