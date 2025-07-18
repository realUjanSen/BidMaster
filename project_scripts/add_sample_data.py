#!/usr/bin/env python3
"""
Add sample data to the database
"""
import mysql.connector
from mysql.connector import Error

def add_sample_data():
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
        
        print("Adding sample data...")
        
        # Get user IDs that were actually created
        cursor.execute("SELECT id FROM users ORDER BY id")
        user_ids = [row[0] for row in cursor.fetchall()]
        print(f"Found user IDs: {user_ids}")
        
        if len(user_ids) >= 4:
            # Insert sample auctions using actual user IDs
            auctions_data = [
                ('Vintage Rolex Submariner', 'A pristine 1965 Rolex Submariner with original box and papers. This rare timepiece features the iconic Mercedes hands and gilt dial. Serviced in 2023 with genuine Rolex parts.', 2500.00, 2600.00, 'Watches', 'Excellent', user_ids[0], '2025-01-25 18:00:00', 'active', 4, 'https://via.placeholder.com/600x400/007bff/ffffff?text=Rolex+Submariner'),
                ('MacBook Pro 16-inch M2', 'Brand new MacBook Pro 16-inch with M2 Max chip, 32GB RAM, 1TB SSD. Still in original packaging with full warranty. Perfect for professionals and creators.', 3200.00, 3400.00, 'Electronics', 'New', user_ids[1], '2025-01-26 20:00:00', 'active', 6, 'https://via.placeholder.com/600x400/28a745/ffffff?text=MacBook+Pro+M2'),
                ('Original Abstract Painting', 'Large canvas abstract expressionist painting by emerging artist. Acrylic on canvas, 48x36 inches. Signed and dated. Perfect centerpiece for modern home or office.', 800.00, 850.00, 'Art', 'Excellent', user_ids[2], '2025-01-24 16:00:00', 'active', 3, 'https://via.placeholder.com/600x400/6f42c1/ffffff?text=Abstract+Painting'),
                ('Diamond Tennis Bracelet', 'Stunning 18K white gold tennis bracelet with 3 carats of brilliant cut diamonds. Professionally appraised and certified. Includes original box and certificate.', 4500.00, 4700.00, 'Jewelry', 'Excellent', user_ids[3], '2025-01-27 19:00:00', 'active', 8, 'https://via.placeholder.com/600x400/ffc107/000000?text=Diamond+Bracelet'),
                ('1967 Ford Mustang Fastback', 'Classic American muscle car, fully restored. 289 V8 engine, 4-speed manual transmission. New paint, chrome, and interior. Numbers matching, documentation included.', 35000.00, 36500.00, 'Automotive', 'Restored', user_ids[0], '2025-01-28 15:00:00', 'active', 12, 'https://via.placeholder.com/600x400/dc3545/ffffff?text=Ford+Mustang')
            ]
            
            auction_query = """
            INSERT INTO auctions (title, description, starting_price, current_bid, category, condition_status, seller_id, end_time, status, total_bids, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(auction_query, auctions_data)
            print(f"✓ Inserted {len(auctions_data)} sample auctions")
            
            # Get auction IDs that were created
            cursor.execute("SELECT id FROM auctions ORDER BY id")
            auction_ids = [row[0] for row in cursor.fetchall()]
            print(f"Created auction IDs: {auction_ids}")
            
            if len(auction_ids) >= 5:
                # Insert sample bids using actual IDs
                bids_data = [
                    (auction_ids[0], user_ids[1], 2600.00),  # User 2 bids on auction 1
                    (auction_ids[1], user_ids[2], 3400.00),  # User 3 bids on auction 2  
                    (auction_ids[2], user_ids[3], 850.00),   # User 4 bids on auction 3
                    (auction_ids[3], user_ids[0], 4700.00),  # User 1 bids on auction 4
                    (auction_ids[4], user_ids[1], 36500.00)  # User 2 bids on auction 5
                ]
                
                bid_query = "INSERT INTO bids (auction_id, bidder_id, bid_amount) VALUES (%s, %s, %s)"
                cursor.executemany(bid_query, bids_data)
                print(f"✓ Inserted {len(bids_data)} sample bids")
            
            connection.commit()
            print("✓ Sample data added successfully!")
            
        else:
            print("✗ Not enough users in database to create sample auctions")
            
    except Error as e:
        print(f"✗ Error adding sample data: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ Database connection closed")

if __name__ == "__main__":
    add_sample_data()
