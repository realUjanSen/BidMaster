import mysql.connector
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG_ROOT = {
    'host': 'localhost',
    'user': 'root',
    'password': ''
}

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'online_auction'
}

def create_database():
    """Create the online_auction database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG_ROOT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS online_auction")
        print("✅ Database 'online_auction' created successfully!")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def create_tables():
    """Create all required tables"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        print("✅ Users table created")
        
        # Create auctions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auctions (
            id INT PRIMARY KEY AUTO_INCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            starting_price DECIMAL(10,2) NOT NULL,
            current_bid DECIMAL(10,2) DEFAULT 0,
            category VARCHAR(50),
            condition_status VARCHAR(50),
            image_url VARCHAR(500),
            seller_id INT NOT NULL,
            winner_id INT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            status ENUM('draft', 'active', 'ended', 'cancelled') DEFAULT 'draft',
            total_bids INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id),
            FOREIGN KEY (winner_id) REFERENCES users(id)
        )
        """)
        print("✅ Auctions table created")
        
        # Create bids table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bids (
            id INT PRIMARY KEY AUTO_INCREMENT,
            auction_id INT NOT NULL,
            bidder_id INT NOT NULL,
            bid_amount DECIMAL(10,2) NOT NULL,
            bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (auction_id) REFERENCES auctions(id),
            FOREIGN KEY (bidder_id) REFERENCES users(id)
        )
        """)
        print("✅ Bids table created")
        
        # Create watchlist table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            auction_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (auction_id) REFERENCES auctions(id),
            UNIQUE KEY unique_watch (user_id, auction_id)
        )
        """)
        print("✅ Watchlist table created")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample data into all tables"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert sample users
        users_data = [
            ('John Doe', 'john@email.com', 'password123', '555-0101', '123 Main St, City, State'),
            ('Jane Smith', 'jane@email.com', 'password456', '555-0102', '456 Oak Ave, Town, State'),
            ('Bob Johnson', 'bob@email.com', 'password789', '555-0103', '789 Pine Rd, Village, State'),
            ('Alice Brown', 'alice@email.com', 'passwordabc', '555-0104', '321 Elm St, City, State'),
            ('Charlie Wilson', 'charlie@email.com', 'passworddef', '555-0105', '654 Maple Dr, Town, State')
        ]
        
        cursor.executemany("""
        INSERT INTO users (name, email, password_hash, phone, address) 
        VALUES (%s, %s, %s, %s, %s)
        """, users_data)
        print("✅ Sample users inserted")
        
        # Insert sample auctions
        end_time_1 = datetime.now() + timedelta(days=3, hours=12)
        end_time_2 = datetime.now() + timedelta(days=5, hours=8)
        end_time_3 = datetime.now() + timedelta(days=1, hours=3)
        end_time_4 = datetime.now() + timedelta(days=7, hours=15)
        end_time_5 = datetime.now() + timedelta(days=2, hours=20)
        
        auctions_data = [
            ('Vintage Ford Mustang 1969', 'Classic American muscle car in pristine condition. This beautiful red Mustang has been meticulously maintained and is ready for its next owner.', 
             35000.00, 45000.00, 'Automotive', 'Excellent', 'https://via.placeholder.com/400x300/FF6B6B/ffffff?text=1969+Ford+Mustang', 1, None, datetime.now(), end_time_1, 'active', 12),
             
            ('Dynasty Hermes Bag', 'Authentic vintage Hermes handbag from Dynasty collection. Rare piece in excellent condition with original packaging.', 
             2000.00, 2850.00, 'Fashion', 'Very Good', 'https://via.placeholder.com/400x300/4ECDC4/ffffff?text=Hermes+Bag', 2, None, datetime.now(), end_time_2, 'active', 15),
             
            ('Signed Baseball Collection', 'Authentic signed baseball by legendary Hall of Fame player. Comes with certificate of authenticity.', 
             800.00, 1200.00, 'Sports', 'Mint', 'https://via.placeholder.com/400x300/45B7D1/ffffff?text=Signed+Baseball', 1, None, datetime.now(), end_time_3, 'active', 18),
             
            ('Vintage Abstract Art', 'Original 1960s abstract painting by renowned artist. Perfect centerpiece for any modern home or office.', 
             5000.00, 8500.00, 'Art', 'Good', 'https://via.placeholder.com/400x300/F7DC6F/000000?text=Abstract+Art', 3, None, datetime.now(), end_time_4, 'active', 22),
             
            ('Rolex Submariner Watch', 'Luxury Swiss timepiece in excellent condition. This iconic watch is perfect for collectors and enthusiasts.', 
             8000.00, 12800.00, 'Watches', 'Excellent', 'https://via.placeholder.com/400x300/BB8FCE/ffffff?text=Rolex+Submariner', 2, None, datetime.now(), end_time_5, 'active', 28),
             
            ('Antique Vase Collection', 'Beautiful collection of 19th century porcelain vases. Perfect for collectors of fine antiques.', 
             1500.00, 2100.00, 'Collectibles', 'Very Good', 'https://via.placeholder.com/400x300/85C1E9/ffffff?text=Antique+Vases', 4, 5, datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=1), 'ended', 14),
             
            ('Vintage Guitar Collection', 'Rare 1960s Fender Stratocaster in original condition. A true collector\'s piece for music enthusiasts.', 
             3000.00, 0, 'Music', 'Good', 'https://via.placeholder.com/400x300/F1948A/ffffff?text=Vintage+Guitar', 1, None, datetime.now(), None, 'draft', 0),
             
            ('Classic Comic Books', 'First edition comic books from the Golden Age. Rare collection in mint condition.', 
             500.00, 750.00, 'Collectibles', 'Mint', 'https://via.placeholder.com/400x300/58D68D/ffffff?text=Comic+Books', 3, 2, datetime.now() - timedelta(days=3), datetime.now() - timedelta(days=1), 'ended', 8)
        ]
        
        cursor.executemany("""
        INSERT INTO auctions (title, description, starting_price, current_bid, category, condition_status, 
                            image_url, seller_id, winner_id, start_time, end_time, status, total_bids) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, auctions_data)
        print("✅ Sample auctions inserted")
        
        # Insert sample bids
        bids_data = [
            (1, 2, 36000.00),  # Jane bids on Mustang
            (1, 3, 38000.00),  # Bob bids on Mustang  
            (1, 4, 42000.00),  # Alice bids on Mustang
            (1, 2, 45000.00),  # Jane bids again on Mustang
            
            (2, 1, 2200.00),   # John bids on Hermes bag
            (2, 3, 2500.00),   # Bob bids on Hermes bag
            (2, 1, 2850.00),   # John bids again on Hermes bag
            
            (3, 4, 900.00),    # Alice bids on baseball
            (3, 5, 1100.00),   # Charlie bids on baseball
            (3, 4, 1200.00),   # Alice bids again on baseball
            
            (4, 2, 6000.00),   # Jane bids on art
            (4, 5, 7500.00),   # Charlie bids on art
            (4, 2, 8500.00),   # Jane bids again on art
            
            (5, 1, 9000.00),   # John bids on Rolex
            (5, 3, 11000.00),  # Bob bids on Rolex
            (5, 1, 12800.00),  # John bids again on Rolex
        ]
        
        cursor.executemany("""
        INSERT INTO bids (auction_id, bidder_id, bid_amount) 
        VALUES (%s, %s, %s)
        """, bids_data)
        print("✅ Sample bids inserted")
        
        # Insert sample watchlist entries
        watchlist_data = [
            (1, 2),  # John watches Hermes bag
            (1, 4),  # John watches art
            (2, 1),  # Jane watches Mustang
            (2, 3),  # Jane watches baseball
            (3, 5),  # Bob watches Rolex
            (4, 1),  # Alice watches Mustang
            (5, 2),  # Charlie watches Hermes bag
        ]
        
        cursor.executemany("""
        INSERT INTO watchlist (user_id, auction_id) 
        VALUES (%s, %s)
        """, watchlist_data)
        print("✅ Sample watchlist entries inserted")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error inserting sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Online Auction Database...")
    print("=" * 50)
    
    # Step 1: Create database
    if not create_database():
        return
    
    # Step 2: Create tables
    if not create_tables():
        return
    
    # Step 3: Insert sample data
    if not insert_sample_data():
        return
    
    print("=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\n📊 Summary:")
    print("- Database: online_auction")
    print("- Tables: users, auctions, bids, watchlist")
    print("- Sample data: 5 users, 8 auctions, 16 bids, 7 watchlist entries")
    print("\n🌐 You can now run your Flask app with: python app.py")

if __name__ == "__main__":
    main()
