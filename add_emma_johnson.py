#!/usr/bin/env python3
"""
Add Emma Johnson as a demo user with a high-value bid
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def add_emma_johnson():
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
        
        print("Adding Emma Johnson as demo user...")
        
        # Check if Emma Johnson already exists
        cursor.execute("SELECT id FROM users WHERE email = 'emma.johnson@email.com'")
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("Emma Johnson already exists, updating her bid...")
            emma_id = existing_user[0]
        else:
            # Create Emma Johnson user
            emma_data = (
                'Emma Johnson',
                'emma.johnson@email.com', 
                'emma123',  # password
                '5678',     # gov_id_last4
                '555-0123', # phone
                50000.00,   # balance
                True,       # is_verified
                datetime.now()  # created_at
            )
            
            user_query = """
            INSERT INTO users (name, email, password_hash, gov_id_last4, phone, balance, is_verified, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(user_query, emma_data)
            emma_id = cursor.lastrowid
            print(f"✓ Created Emma Johnson with ID: {emma_id}")
        
        # Get the Ford Mustang auction (highest value)
        cursor.execute("SELECT id FROM auctions WHERE title LIKE '%Ford Mustang%' ORDER BY id DESC LIMIT 1")
        mustang_auction = cursor.fetchone()
        
        if mustang_auction:
            auction_id = mustang_auction[0]
            
            # Add Emma's high bid
            bid_data = (auction_id, emma_id, 36500.00)
            cursor.execute("INSERT INTO bids (auction_id, bidder_id, bid_amount) VALUES (%s, %s, %s)", bid_data)
            
            # Update the auction's current bid
            cursor.execute("UPDATE auctions SET current_bid = %s WHERE id = %s", (36500.00, auction_id))
            
            print(f"✓ Added Emma's bid of $36,500 on Ford Mustang auction")
        
        connection.commit()
        print("✓ Emma Johnson added successfully!")
        
    except Error as e:
        print(f"✗ Error adding Emma Johnson: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ Database connection closed")

if __name__ == "__main__":
    add_emma_johnson()
