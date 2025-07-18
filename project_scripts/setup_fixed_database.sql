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
    end_time TIMESTAMP NULL,
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
    FOREIGN KEY (auction_id) REFERENCES auctions(id) ON DELETE CASCADE,
    FOREIGN KEY (bidder_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create watchlist table
CREATE TABLE IF NOT EXISTS watchlist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    auction_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (auction_id) REFERENCES auctions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_watchlist (user_id, auction_id)
);

-- Create user_sessions table for login management
CREATE TABLE IF NOT EXISTS user_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    session_token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create balance_transactions table to track balance changes
CREATE TABLE IF NOT EXISTS balance_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    transaction_type ENUM('deposit', 'withdraw', 'bid_placed', 'bid_refund', 'auction_won', 'auction_sold') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    auction_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (auction_id) REFERENCES auctions(id) ON DELETE SET NULL
);

-- Insert sample users
INSERT INTO users (name, email, password_hash, phone, balance, gov_id_last4, is_verified) VALUES
('John Smith', 'john@example.com', 'hashed_password_1', '555-0101', 2500.00, '1234', TRUE),
('Emma Johnson', 'emma@example.com', 'hashed_password_2', '555-0102', 1800.00, '5678', TRUE),
('Michael Brown', 'michael@example.com', 'hashed_password_3', '555-0103', 3200.00, '9012', TRUE),
('Sarah Davis', 'sarah@example.com', 'hashed_password_4', '555-0104', 1500.00, '3456', TRUE);

-- Insert sample auctions
INSERT INTO auctions (title, description, starting_price, current_bid, category, condition_status, seller_id, end_time, status, total_bids, image_url) VALUES
('Vintage Rolex Submariner', 'A pristine 1965 Rolex Submariner with original box and papers. This rare timepiece features the iconic Mercedes hands and gilt dial. Serviced in 2023 with genuine Rolex parts.', 2500.00, 2600.00, 'Watches', 'Excellent', 1, '2025-01-25 18:00:00', 'active', 4, 'https://images.unsplash.com/photo-1548068330-8b3e0d5e4b7d?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3'),
('MacBook Pro 16-inch M2', 'Brand new MacBook Pro 16-inch with M2 Max chip, 32GB RAM, 1TB SSD. Still in original packaging with full warranty. Perfect for professionals and creators.', 3200.00, 3400.00, 'Electronics', 'New', 2, '2025-01-26 20:00:00', 'active', 6, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3'),
('Original Abstract Painting', 'Large canvas abstract expressionist painting by emerging artist. Acrylic on canvas, 48x36 inches. Signed and dated. Perfect centerpiece for modern home or office.', 800.00, 850.00, 'Art', 'Excellent', 3, '2025-01-24 16:00:00', 'active', 3, 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3'),
('Diamond Tennis Bracelet', 'Stunning 18K white gold tennis bracelet with 3 carats of brilliant cut diamonds. Professionally appraised and certified. Includes original box and certificate.', 4500.00, 4700.00, 'Jewelry', 'Excellent', 4, '2025-01-27 19:00:00', 'active', 8, 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3'),
('1967 Ford Mustang Fastback', 'Classic American muscle car, fully restored. 289 V8 engine, 4-speed manual transmission. New paint, chrome, and interior. Numbers matching, documentation included.', 35000.00, 36500.00, 'Automotive', 'Restored', 1, '2025-01-28 15:00:00', 'active', 12, 'https://images.unsplash.com/photo-1494905998402-395d579af36f?q=80&w=1000&auto=format&fit=crop&ixlib=rb-4.0.3');

-- Insert sample bids
INSERT INTO bids (auction_id, bidder_id, bid_amount) VALUES
(1, 2, 2600.00),
(2, 3, 3400.00),
(3, 4, 850.00),
(4, 1, 4700.00),
(5, 2, 36500.00);

-- Insert sample watchlist entries
INSERT INTO watchlist (user_id, auction_id) VALUES
(1, 2),
(1, 3),
(2, 4),
(3, 1),
(4, 5);

-- Insert sample balance transactions
INSERT INTO balance_transactions (user_id, transaction_type, amount, description, auction_id) VALUES
(1, 'deposit', 1000.00, 'Initial deposit', NULL),
(2, 'deposit', 800.00, 'Initial deposit', NULL),
(3, 'deposit', 1200.00, 'Initial deposit', NULL),
(4, 'deposit', 500.00, 'Initial deposit', NULL),
(2, 'bid_placed', -2600.00, 'Bid placed on Vintage Rolex Submariner', 1),
(3, 'bid_placed', -3400.00, 'Bid placed on MacBook Pro 16-inch M2', 2),
(4, 'bid_placed', -850.00, 'Bid placed on Original Abstract Painting', 3),
(1, 'bid_placed', -4700.00, 'Bid placed on Diamond Tennis Bracelet', 4),
(2, 'bid_placed', -36500.00, 'Bid placed on 1967 Ford Mustang Fastback', 5);
