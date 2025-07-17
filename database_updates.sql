-- Database updates for authentication and balance system

-- Add session management and balance to users table
ALTER TABLE users ADD COLUMN balance DECIMAL(10,2) DEFAULT 1000.00;
ALTER TABLE users ADD COLUMN gov_id_last4 VARCHAR(4);
ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN last_login TIMESTAMP NULL;
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create sessions table for login management
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

-- Update existing users with starting balance
UPDATE users SET balance = 1000.00 WHERE balance IS NULL;

-- Add some sample balance transactions
INSERT INTO balance_transactions (user_id, transaction_type, amount, description) VALUES
(1, 'recharge', 1000.00, 'Welcome bonus'),
(2, 'recharge', 1000.00, 'Welcome bonus'),
(3, 'recharge', 1000.00, 'Welcome bonus'),
(4, 'recharge', 1000.00, 'Welcome bonus'),
(5, 'recharge', 1000.00, 'Welcome bonus');
