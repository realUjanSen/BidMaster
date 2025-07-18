#!/usr/bin/env python3
"""
Fix auction images - update all auctions with proper working image URLs
"""
import mysql.connector
from mysql.connector import Error

def fix_auction_images():
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
        
        print("Fixing auction images...")
        
        # Get all auctions
        cursor.execute("SELECT id, title, image_url FROM auctions ORDER BY id")
        auctions = cursor.fetchall()
        
        print(f"Found {len(auctions)} auctions to fix")
        
        # High-quality image URLs for each auction type
        image_mappings = {
            'Vintage Rolex Submariner': 'https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=600&h=400&fit=crop&crop=center',
            'MacBook Pro 16-inch M2': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&h=400&fit=crop&crop=center',
            'Original Abstract Painting': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=600&h=400&fit=crop&crop=center',
            'Diamond Tennis Bracelet': 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&h=400&fit=crop&crop=center',
            '1967 Ford Mustang Fastback': 'https://images.unsplash.com/photo-1494976997100-8ed7a0c18d44?w=600&h=400&fit=crop&crop=center'
        }
        
        # Update each auction with proper image URL
        for auction in auctions:
            auction_id = auction[0]
            title = auction[1]
            current_image = auction[2]
            
            # Find the right image based on title
            new_image_url = None
            for key, url in image_mappings.items():
                if key in title:
                    new_image_url = url
                    break
            
            # Fallback to a generic image if no match found
            if not new_image_url:
                new_image_url = 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=600&h=400&fit=crop&crop=center'
            
            # Update the auction
            cursor.execute("""
                UPDATE auctions 
                SET image_url = %s
                WHERE id = %s
            """, (new_image_url, auction_id))
            
            print(f"✓ Updated '{title}' image")
            print(f"  Old: {current_image}")
            print(f"  New: {new_image_url}")
            print()
        
        connection.commit()
        print("✓ All auction images fixed successfully!")
        
    except Error as e:
        print(f"✗ Error fixing auction images: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("✓ Database connection closed")

if __name__ == "__main__":
    fix_auction_images()
