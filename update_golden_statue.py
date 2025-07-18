#!/usr/bin/env python3
"""
Update the Golden Statue auction with a new image URL
"""
import mysql.connector
from mysql.connector import Error

def update_golden_statue_image():
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
        
        print("Updating Golden Statue auction image...")
        
        # First, check the current auction
        cursor.execute("SELECT id, title, image_url FROM auctions WHERE id = 21")
        result = cursor.fetchone()
        
        if result:
            print(f"Found auction: ID={result[0]}, Title='{result[1]}'")
            print(f"Current image URL: {result[2]}")
            
            # Update with new image URL
            new_image_url = 'https://i.postimg.cc/DwPyc6jM/gold.webp'
            cursor.execute("UPDATE auctions SET image_url = %s WHERE id = 21", (new_image_url,))
            connection.commit()
            
            print(f"✅ Successfully updated image URL to: {new_image_url}")
            print(f"Rows affected: {cursor.rowcount}")
            
        else:
            print("❌ No auction found with ID 21")
            
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_golden_statue_image()
