-- Complete database setup script for BidMaster Online Auction
-- Run this script to create the database and all necessary tables

-- Create the database
CREATE DATABASE IF NOT EXISTS online_auction;
USE online_auction;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    balance DECIMAL(10,2) DEFAULT 1000.00,
    gov_id_last4 VARCHAR(4),
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create auctions table
CREATE TABLE IF NOT EXISTS auctions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    starting_price DECIMAL(10,2) NOT NULL,
    current_bid DECIMAL(10,2) DEFAULT NULL,
    category VARCHAR(50),
    condition_status VARCHAR(50),
    seller_id INT NOT NULL,
    winner_id INT DEFAULT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status ENUM('draft', 'active', 'ended', 'cancelled') DEFAULT 'active',
    total_bids INT DEFAULT 0,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id)
);

-- Create bids table
CREATE TABLE IF NOT EXISTS bids (
    id INT PRIMARY KEY AUTO_INCREMENT,
    auction_id INT NOT NULL,
    bidder_id INT NOT NULL,
    bid_amount DECIMAL(10,2) NOT NULL,
    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (bidder_id) REFERENCES users(id)
);

-- Create watchlist table
CREATE TABLE IF NOT EXISTS watchlist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    auction_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    UNIQUE KEY unique_watch (user_id, auction_id)
);

-- Create user_sessions table for login management
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_session (session_token)
);

-- Create balance_transactions table to track balance changes
CREATE TABLE IF NOT EXISTS balance_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    transaction_type ENUM('recharge', 'bid', 'refund', 'earning') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    auction_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (auction_id) REFERENCES auctions(id)
);

-- Insert sample users
INSERT INTO users (name, email, password_hash, phone, gov_id_last4, is_verified, balance) VALUES
('John Doe', 'john@example.com', 'password123', '555-0101', '1234', TRUE, 1000.00),
('Jane Smith', 'jane@example.com', 'password123', '555-0102', '5678', TRUE, 1500.00),
('Bob Johnson', 'bob@example.com', 'password123', '555-0103', '9012', TRUE, 2000.00),
('Alice Brown', 'alice@example.com', 'password123', '555-0104', '3456', TRUE, 1200.00),
('Charlie Wilson', 'charlie@example.com', 'password123', '555-0105', '7890', TRUE, 1800.00);

-- Insert sample auctions
INSERT INTO auctions (title, description, starting_price, current_bid, category, condition_status, seller_id, end_time, status, total_bids, image_url) VALUES
('Vintage Rolex Submariner', 'Authentic 1970s Rolex Submariner in excellent condition. This iconic timepiece features the classic black dial and bezel, automatic movement, and original bracelet. Comes with original box and papers. Service history available.', 2500.00, 2750.00, 'Watches', 'Excellent', 1, DATE_ADD(NOW(), INTERVAL 5 DAY), 'active', 3, 'https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=500&h=400&fit=crop&crop=center'),
('MacBook Pro 16-inch M2', 'Brand new MacBook Pro 16-inch with M2 Max chip, 32GB unified memory, and 1TB SSD. Space Gray finish. Still sealed in original packaging with full warranty. Perfect for professionals and content creators.', 1800.00, 1950.00, 'Electronics', 'New', 2, DATE_ADD(NOW(), INTERVAL 3 DAY), 'active', 5, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&h=400&fit=crop&crop=center'),
('Abstract Oil Painting', 'Original abstract oil painting from renowned artist Maria Rodriguez, created in 2020. Features vibrant blues and golds with textured brushwork. Professionally framed and ready to hang. Certificate of authenticity included.', 1200.00, 1350.00, 'Art', 'Excellent', 3, DATE_ADD(NOW(), INTERVAL 7 DAY), 'active', 2, 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=500&h=400&fit=crop&crop=center'),
('2 Carat Diamond Ring', '2.01 carat round brilliant diamond engagement ring in platinum setting. GIA certified (E color, VS1 clarity). Classic 6-prong setting with micro-pave band. Appraisal value $8,500. Perfect for proposals or investment.', 3500.00, 3500.00, 'Jewelry', 'Excellent', 4, DATE_ADD(NOW(), INTERVAL 4 DAY), 'active', 0, 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&h=400&fit=crop&crop=center'),
('1967 Mustang GT Parts', 'Rare and authentic parts for 1967 Ford Mustang GT. Includes original 390 V8 engine components, interior door panels, dashboard pieces, and chrome trim. Perfect for restoration projects. All parts guaranteed authentic.', 800.00, 850.00, 'Automotive', 'Good', 5, DATE_ADD(NOW(), INTERVAL 2 DAY), 'active', 1, 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=500&h=400&fit=crop&crop=center');

-- Insert sample bids
INSERT INTO bids (auction_id, bidder_id, bid_amount) VALUES
(1, 2, 2600.00),
(1, 3, 2700.00),
(1, 4, 2750.00),
(2, 1, 1850.00),
(2, 3, 1900.00),
(2, 4, 1950.00),
(3, 1, 1250.00),
(3, 2, 1350.00),
(5, 1, 850.00);

-- Insert sample watchlist entries
INSERT INTO watchlist (user_id, auction_id) VALUES
(1, 2),
(1, 3),
(2, 1),
(2, 4),
(3, 1),
(3, 2),
(4, 3),
(4, 5),
(5, 1),
(5, 4);

-- Insert sample balance transactions
INSERT INTO balance_transactions (user_id, transaction_type, amount, description) VALUES
(1, 'recharge', 1000.00, 'Welcome bonus'),
(2, 'recharge', 1500.00, 'Welcome bonus'),
(3, 'recharge', 2000.00, 'Welcome bonus'),
(4, 'recharge', 1200.00, 'Welcome bonus'),
(5, 'recharge', 1800.00, 'Welcome bonus'),
(2, 'bid', 2600.00, 'Bid placed on "Vintage Rolex Watch"'),
(3, 'bid', 2700.00, 'Bid placed on "Vintage Rolex Watch"'),
(4, 'bid', 2750.00, 'Bid placed on "Vintage Rolex Watch"'),
(1, 'bid', 1850.00, 'Bid placed on "MacBook Pro 2023"'),
(3, 'bid', 1900.00, 'Bid placed on "MacBook Pro 2023"'),
(4, 'bid', 1950.00, 'Bid placed on "MacBook Pro 2023"');

-- Show confirmation
SELECT 'Database setup complete!' as message;
SELECT 'Users created:', COUNT(*) as count FROM users;
SELECT 'Auctions created:', COUNT(*) as count FROM auctions;
SELECT 'Bids created:', COUNT(*) as count FROM bids;
SELECT 'Watchlist entries:', COUNT(*) as count FROM watchlist;
SELECT 'Balance transactions:', COUNT(*) as count FROM balance_transactions;
