from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
from datetime import datetime, timedelta
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Add template context processor for datetime functions
@app.context_processor
def inject_datetime():
    return {
        'now': datetime.now,
        'timedelta': timedelta,
        'datetime': datetime
    }

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'online_auction'
}

def get_db_connection():
    try:
        print("Attempting to connect to database...")
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Database connection successful")
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        raise e
    except Exception as e:
        print(f"Unexpected database connection error: {e}")
        raise e

def get_current_user():
    """Get current logged-in user from session"""
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return user
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
    return None

def login_required(f):
    """Decorator to require login for certain routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            # Store the intended destination
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def create_user_session(user_id):
    """Create a new user session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Insert session
        cursor.execute("""
            INSERT INTO user_sessions (user_id, session_token, expires_at) 
            VALUES (%s, %s, %s)
        """, (user_id, session_token, expires_at))
        
        # Update last login
        cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", 
                      (datetime.now(), user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Set session variables
        session['user_id'] = user_id
        session['session_token'] = session_token
        
        return True
    except Exception as e:
        print(f"Error creating session: {e}")
        return False

def add_balance_transaction(user_id, transaction_type, amount, description, auction_id=None):
    """Add a balance transaction record"""
    try:
        print(f"Adding balance transaction: user={user_id}, type={transaction_type}, amount=${amount:.2f}, desc='{description}'")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO balance_transactions (user_id, transaction_type, amount, description, auction_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, transaction_type, amount, description, auction_id))
        
        transaction_id = cursor.lastrowid
        print(f"Transaction record created with ID: {transaction_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"MySQL error adding balance transaction: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error adding balance transaction: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_user_balance(user_id, amount, operation='add'):
    """Update user balance (add or subtract)"""
    try:
        print(f"Updating balance for user {user_id}: {operation} ${amount:.2f}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current balance first
        cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        current_balance = cursor.fetchone()
        
        if current_balance:
            current_balance = current_balance[0]
            print(f"Current balance: ${current_balance:.2f}")
            
            if operation == 'add':
                new_balance = float(current_balance) + float(amount)
                cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
            else:
                new_balance = float(current_balance) - float(amount)
                if new_balance < 0:
                    print(f"Warning: Balance would be negative: ${new_balance:.2f}")
                cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, user_id))
            
            print(f"New balance: ${new_balance:.2f}")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            print(f"Error: User {user_id} not found")
            cursor.close()
            conn.close()
            return False
            
    except mysql.connector.Error as e:
        print(f"MySQL error updating balance: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error updating balance: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_all_users():
    """Fetch all users from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def get_all_auctions():
    """Fetch all auctions with seller information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT a.*, u.name as seller_name, w.name as winner_name 
        FROM auctions a 
        LEFT JOIN users u ON a.seller_id = u.id 
        LEFT JOIN users w ON a.winner_id = w.id 
        ORDER BY a.created_at DESC
        """
        cursor.execute(query)
        auctions = cursor.fetchall()
        
        # Add calculated fields
        for auction in auctions:
            # Calculate time left
            if auction['end_time'] and auction['status'] == 'active':
                time_left = auction['end_time'] - datetime.now()
                if time_left.total_seconds() > 0:
                    days = time_left.days
                    hours = time_left.seconds // 3600
                    auction['time_left'] = f"{days}d {hours}h"
                else:
                    auction['time_left'] = "Ended"
            else:
                auction['time_left'] = None
                
            # Calculate watchers count (mock data for now)
            auction['watchers_count'] = auction.get('total_bids', 0) // 2
        
        cursor.close()
        conn.close()
        return auctions
    except Exception as e:
        print(f"Error fetching auctions: {e}")
        return []

def get_auction_by_id(auction_id):
    """Fetch specific auction with seller and bid information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get auction details
        auction_query = """
        SELECT a.*, u.name as seller_name, w.name as winner_name 
        FROM auctions a 
        LEFT JOIN users u ON a.seller_id = u.id 
        LEFT JOIN users w ON a.winner_id = w.id 
        WHERE a.id = %s
        """
        cursor.execute(auction_query, (auction_id,))
        auction = cursor.fetchone()
        
        if auction:
            # Get recent bids for this auction
            bid_query = """
            SELECT b.*, u.name as bidder_name 
            FROM bids b 
            JOIN users u ON b.bidder_id = u.id 
            WHERE b.auction_id = %s 
            ORDER BY b.bid_time DESC 
            LIMIT 10
            """
            cursor.execute(bid_query, (auction_id,))
            auction['recent_bids'] = cursor.fetchall()
            
            # Calculate time left
            if auction['end_time']:
                time_left = auction['end_time'] - datetime.now()
                if time_left.total_seconds() > 0:
                    days = time_left.days
                    hours = time_left.seconds // 3600
                    auction['time_left'] = f"{days}d {hours}h"
                else:
                    auction['time_left'] = "Ended"
            else:
                auction['time_left'] = "No end date"
            
            # Add missing fields expected by template
            auction['badge'] = auction['status'].upper()
            auction['badge_color'] = 'success' if auction['status'] == 'active' else 'secondary'
            
            # Set current bid to starting price if no bids yet
            if not auction['current_bid']:
                auction['current_bid'] = auction['starting_price']
            
            # Add mock specifications and condition data
            auction['specifications'] = {
                'Category': auction['category'] or 'General',
                'Condition': auction['condition_status'] or 'Good',
                'Starting Price': f"${auction['starting_price']:,.2f}",
                'Auction ID': f"#{auction['id']}"
            }
            
            auction['condition'] = {
                'Overall': auction['condition_status'] or 'Good',
                'Authenticity': 'Verified',
                'Documentation': 'Complete'
            }
        
        cursor.close()
        conn.close()
        return auction
    except Exception as e:
        print(f"Error fetching auction {auction_id}: {e}")
        return None

def get_all_bids():
    """Fetch all bids with auction and bidder information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT b.*, a.title as auction_title, u.name as bidder_name 
        FROM bids b 
        JOIN auctions a ON b.auction_id = a.id 
        JOIN users u ON b.bidder_id = u.id 
        ORDER BY b.bid_time DESC
        """
        cursor.execute(query)
        bids = cursor.fetchall()
        cursor.close()
        conn.close()
        return bids
    except Exception as e:
        print(f"Error fetching bids: {e}")
        return []

def get_all_watchlist():
    """Fetch all watchlist entries with user and auction information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT w.*, u.name as user_name, a.title as auction_title, a.current_bid 
        FROM watchlist w 
        JOIN users u ON w.user_id = u.id 
        JOIN auctions a ON w.auction_id = a.id 
        ORDER BY w.created_at DESC
        """
        cursor.execute(query)
        watchlist = cursor.fetchall()
        cursor.close()
        conn.close()
        return watchlist
    except Exception as e:
        print(f"Error fetching watchlist: {e}")
        return []

@app.route('/')
def home():
    # Get statistics for homepage
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Get active auctions count
        cursor.execute("SELECT COUNT(*) as count FROM auctions WHERE status = 'active'")
        active_auctions_count = cursor.fetchone()['count']
        # Get total users count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        # Get total bids
        cursor.execute("SELECT COUNT(*) as count FROM bids")
        total_bids = cursor.fetchone()['count']
        # Get total value
        cursor.execute("SELECT SUM(current_bid) as total_value FROM auctions WHERE status = 'active'")
        total_value = cursor.fetchone()['total_value'] or 0
        # Get featured auctions (highest bid auctions)
        cursor.execute("""
            SELECT a.*, u.name as seller_name 
            FROM auctions a 
            LEFT JOIN users u ON a.seller_id = u.id 
            WHERE a.status = 'active' 
            ORDER BY a.current_bid DESC 
            LIMIT 3
        """)
        featured_auctions = cursor.fetchall()
        # Get recent auctions (newest)
        cursor.execute("""
            SELECT a.*, u.name as seller_name 
            FROM auctions a 
            LEFT JOIN users u ON a.seller_id = u.id 
            WHERE a.status = 'active' 
            ORDER BY a.created_at DESC 
            LIMIT 6
        """)
        recent_auctions = cursor.fetchall()
        # Add time left calculation
        for auction in featured_auctions + recent_auctions:
            if auction['end_time']:
                time_left = auction['end_time'] - datetime.now()
                if time_left.total_seconds() > 0:
                    days = time_left.days
                    hours = time_left.seconds // 3600
                    auction['time_left'] = f"{days}d {hours}h"
                else:
                    auction['time_left'] = "Ended"
            else:
                auction['time_left'] = None
        cursor.close()
        conn.close()
        current_user = get_current_user()
        statistics = {
            'total_auctions': active_auctions_count,
            'total_users': total_users,
            'total_bids': total_bids,
            'total_value': total_value
        }
        return render_template('index.html', 
                             featured_auctions=featured_auctions,
                             recent_auctions=recent_auctions,
                             statistics=statistics,
                             current_user=current_user)
    except Exception as e:
        print(f"Error rendering home page: {e}")
        return render_template('index.html', statistics={'total_auctions': 0, 'total_users': 0, 'total_bids': 0, 'total_value': 0}, featured_auctions=[], recent_auctions=[], current_user=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("=== LOGIN DEBUG START ===")
        
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        print(f"Login attempt for email: {email}")
        print(f"Password length: {len(password) if password else 0}")
        print(f"Remember me: {remember}")
        
        # Basic validation
        if not email or not password:
            print("Login failed: Missing email or password")
            flash('Please enter both email and password.', 'error')
            print("=== LOGIN DEBUG END (validation failed) ===")
            return render_template('login.html')
        
        try:
            print("Attempting database connection...")
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            print(f"Searching for user with email: {email}")
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                print(f"User found: {user['name']} (ID: {user['id']})")
                print(f"User balance: ${user['balance']:.2f}")
                print(f"User verified: {user['is_verified']}")
                
                # Check password
                if user['password_hash'] == password:
                    print("Password matches!")
                    
                    # Create session
                    print("Creating user session...")
                    session_created = create_user_session(user['id'])
                    
                    if session_created:
                        print("Session created successfully")
                        
                        # Welcome back message
                        first_name = user['name'].split()[0]
                        flash(f'Welcome back, {first_name}! You have ${user["balance"]:.2f} in your account.', 'success')
                        
                        # Redirect to intended page or home
                        next_page = request.args.get('next')
                        if next_page:
                            print(f"Redirecting to intended page: {next_page}")
                            cursor.close()
                            conn.close()
                            print("=== LOGIN DEBUG END (success with redirect) ===")
                            return redirect(next_page)
                        else:
                            print("Redirecting to home page")
                            cursor.close()
                            conn.close()
                            print("=== LOGIN DEBUG END (success to home) ===")
                            return redirect(url_for('home'))
                    else:
                        print("Failed to create session")
                        flash('Login failed due to session error. Please try again.', 'error')
                else:
                    print("Password does not match")
                    flash('Invalid email or password. Please check your credentials and try again.', 'error')
            else:
                print("No user found with this email")
                flash('Invalid email or password. Please check your credentials and try again.', 'error')
                
            cursor.close()
            conn.close()
            print("=== LOGIN DEBUG END (failed) ===")
                
        except mysql.connector.Error as e:
            print(f"MySQL database error during login: {e}")
            flash(f'Database error during login: {str(e)}', 'error')
            print("=== LOGIN DEBUG END (mysql error) ===")
            
        except Exception as e:
            print(f"Unexpected login error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Login failed with error: {str(e)}', 'error')
            print("=== LOGIN DEBUG END (unexpected error) ===")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("=== REGISTRATION DEBUG START ===")
        
        # Get form data
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        name = f"{first_name} {last_name}"
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        gov_id_last4 = request.form.get('gov_id_last4')
        phone = request.form.get('phone')
        
        # Debug form data
        print(f"Registration attempt for: {name} ({email})")
        print(f"Form data received:")
        print(f"  - First Name: '{first_name}'")
        print(f"  - Last Name: '{last_name}'")
        print(f"  - Email: '{email}'")
        print(f"  - Password: {'*' * len(password) if password else 'None'}")
        print(f"  - Confirm Password: {'*' * len(confirm_password) if confirm_password else 'None'}")
        print(f"  - Gov ID Last 4: '{gov_id_last4}'")
        print(f"  - Phone: '{phone}'")
        
        # Detailed validation with debugging
        validation_errors = []
        
        # Check required fields
        if not first_name or not first_name.strip():
            validation_errors.append("First name is required")
        if not last_name or not last_name.strip():
            validation_errors.append("Last name is required")
        if not email or not email.strip():
            validation_errors.append("Email is required")
        if not password:
            validation_errors.append("Password is required")
        if not confirm_password:
            validation_errors.append("Password confirmation is required")
        
        # Password validation
        if password and confirm_password:
            if password != confirm_password:
                validation_errors.append("Passwords do not match")
            if len(password) < 6:
                validation_errors.append("Password must be at least 6 characters long")
        
        # Gov ID validation
        if not gov_id_last4:
            validation_errors.append("Government ID last 4 digits are required")
        elif len(gov_id_last4) != 4:
            validation_errors.append("Government ID must be exactly 4 digits")
        elif not gov_id_last4.isdigit():
            validation_errors.append("Government ID must contain only numbers")
        
        # Email format validation
        if email and '@' not in email:
            validation_errors.append("Email must contain @ symbol")
        
        print(f"Validation errors: {validation_errors}")
        
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            print("=== REGISTRATION DEBUG END (validation failed) ===")
            return render_template('register.html')
        
        # Check for existing user
        try:
            print("Checking for existing user...")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, email FROM users WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if existing_user:
                print(f"User already exists with email: {email}")
                flash('An account with this email address already exists. Please use a different email or try logging in.', 'error')
                print("=== REGISTRATION DEBUG END (user exists) ===")
                return render_template('register.html')
            
            print("No existing user found, proceeding with registration...")
            
        except Exception as e:
            print(f"Error checking existing user: {e}")
            flash(f'Database error during user check: {str(e)}', 'error')
            print("=== REGISTRATION DEBUG END (db check error) ===")
            return render_template('register.html')
        
        # Attempt to create user
        try:
            print("Attempting to create new user...")
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Log the exact query being executed
            insert_query = """
                INSERT INTO users (name, email, password_hash, gov_id_last4, phone, balance, is_verified, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_values = (name, email, password, gov_id_last4, phone, 1000.00, True, datetime.now())
            
            print(f"Executing query: {insert_query}")
            print(f"With values: {(name, email, '[PASSWORD]', gov_id_last4, phone, 1000.00, True, 'NOW()')}")
            
            cursor.execute(insert_query, insert_values)
            user_id = cursor.lastrowid
            
            print(f"User created successfully with ID: {user_id}")
            
            # Add welcome bonus transaction
            print("Adding welcome bonus transaction...")
            transaction_success = add_balance_transaction(user_id, 'recharge', 1000.00, 'Welcome bonus - new user registration')
            
            if transaction_success:
                print("Welcome bonus transaction added successfully")
            else:
                print("Warning: Welcome bonus transaction failed")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"Registration completed successfully for user: {name}")
            flash(f'🎉 Registration successful, {first_name}! Your account has been created with a $1000 welcome bonus. Please log in to start bidding.', 'success')
            print("=== REGISTRATION DEBUG END (success) ===")
            return redirect(url_for('login'))
            
        except mysql.connector.IntegrityError as e:
            print(f"Database integrity error: {e}")
            error_msg = str(e)
            
            if 'email' in error_msg.lower():
                flash('An account with this email address already exists. Please use a different email or try logging in.', 'error')
            elif 'gov_id_last4' in error_msg.lower():
                flash('An account with these government ID digits already exists. Please verify your information.', 'error')
            else:
                flash(f'Registration failed due to duplicate information. Database error: {error_msg}', 'error')
            
            print("=== REGISTRATION DEBUG END (integrity error) ===")
            
        except mysql.connector.Error as e:
            print(f"MySQL database error: {e}")
            flash(f'Database error during registration: {str(e)}', 'error')
            print("=== REGISTRATION DEBUG END (mysql error) ===")
            
        except Exception as e:
            print(f"Unexpected registration error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Registration failed with error: {str(e)}', 'error')
            print("=== REGISTRATION DEBUG END (unexpected error) ===")
    
    return render_template('register.html')

@app.route('/my-auctions')
@login_required
def my_auctions():
    current_user = get_current_user()
    auctions = get_all_auctions()
    
    # Filter auctions by current user
    user_auctions = [a for a in auctions if a['seller_id'] == current_user['id']]
    active_auctions = [a for a in user_auctions if a['status'] == 'active']
    sold_auctions = [a for a in user_auctions if a['status'] == 'ended' and a['winner_id']]
    draft_auctions = [a for a in user_auctions if a['status'] == 'draft']
    
    return render_template('my-auctions.html', 
                         active_auctions=active_auctions,
                         sold_auctions=sold_auctions,
                         draft_auctions=draft_auctions,
                         current_user=current_user)

@app.route('/create-auction', methods=['GET', 'POST'])
@login_required
def create_auction():
    current_user = get_current_user()
    
    if request.method == 'POST':
        print("=== CREATE AUCTION DEBUG START ===")
        
        title = request.form.get('title')
        description = request.form.get('description')
        starting_price_str = request.form.get('starting_price')
        category = request.form.get('category')
        condition = request.form.get('condition')
        duration_days_str = request.form.get('duration_days', '7')
        image_url = request.form.get('image_url')
        
        print(f"Create auction attempt by user: {current_user['name']} (ID: {current_user['id']})")
        print(f"Form data:")
        print(f"  - Title: '{title}'")
        print(f"  - Description: '{description[:100]}...' ({len(description)} chars)")
        print(f"  - Starting Price: '{starting_price_str}'")
        print(f"  - Category: '{category}'")
        print(f"  - Condition: '{condition}'")
        print(f"  - Duration: '{duration_days_str}'")
        print(f"  - Image URL: '{image_url}'")
        
        # Validation with detailed error messages
        validation_errors = []
        
        if not title or not title.strip():
            validation_errors.append("Title is required")
        elif len(title.strip()) < 3:
            validation_errors.append("Title must be at least 3 characters long")
            
        if not description or not description.strip():
            validation_errors.append("Description is required")
        elif len(description.strip()) < 10:
            validation_errors.append("Description must be at least 10 characters long")
            
        if not starting_price_str:
            validation_errors.append("Starting price is required")
        else:
            try:
                starting_price = float(starting_price_str)
                if starting_price <= 0:
                    validation_errors.append("Starting price must be greater than 0")
                elif starting_price > 1000000:
                    validation_errors.append("Starting price cannot exceed $1,000,000")
            except ValueError:
                validation_errors.append("Starting price must be a valid number")
                starting_price = 0
        
        if not category:
            validation_errors.append("Category is required")
        if not condition:
            validation_errors.append("Condition is required")
        if not image_url:
            validation_errors.append("Image URL is required")
        elif not image_url.startswith(('http://', 'https://')):
            validation_errors.append("Image URL must start with http:// or https://")
            
        try:
            duration_days = int(duration_days_str)
            if duration_days < 1:
                validation_errors.append("Duration must be at least 1 day")
            elif duration_days > 30:
                validation_errors.append("Duration cannot exceed 30 days")
        except ValueError:
            validation_errors.append("Duration must be a valid number")
            duration_days = 7
        
        print(f"Validation errors: {validation_errors}")
        
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            print("=== CREATE AUCTION DEBUG END (validation failed) ===")
            return render_template('create-auction.html', current_user=current_user)
        
        try:
            print("Attempting to create auction in database...")
            conn = get_db_connection()
            cursor = conn.cursor()
            
            end_time = datetime.now() + timedelta(days=duration_days)
            
            print(f"Auction will end at: {end_time}")
            
            insert_query = """
                INSERT INTO auctions (title, description, starting_price, category, condition_status, 
                                    seller_id, start_time, end_time, status, image_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_values = (title, description, starting_price, category, condition, current_user['id'], 
                           datetime.now(), end_time, 'active', image_url)
            
            print(f"Executing query: {insert_query}")
            print(f"With values: {insert_values}")
            
            cursor.execute(insert_query, insert_values)
            auction_id = cursor.lastrowid
            
            print(f"Auction created successfully with ID: {auction_id}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash(f'🎉 Auction "{title}" created successfully! Your auction is now live and will run for {duration_days} days. Good luck!', 'success')
            print("=== CREATE AUCTION DEBUG END (success) ===")
            return redirect(url_for('auction_details', auction_id=auction_id))
            
        except mysql.connector.Error as e:
            print(f"MySQL database error during auction creation: {e}")
            flash(f'Database error while creating auction: {str(e)}', 'error')
            print("=== CREATE AUCTION DEBUG END (mysql error) ===")
            
        except Exception as e:
            print(f"Unexpected error during auction creation: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Failed to create auction: {str(e)}', 'error')
            print("=== CREATE AUCTION DEBUG END (unexpected error) ===")
    
    return render_template('create-auction.html', current_user=current_user)

@app.route('/auction/<int:auction_id>')
def auction_details(auction_id):
    current_user = get_current_user()
    auction = get_auction_by_id(auction_id)
    
    if not auction:
        flash('Auction not found', 'error')
        return redirect(url_for('all_auctions'))
    
    return render_template('auction.html', auction=auction, current_user=current_user)

@app.route('/auctions')
def all_auctions():
    auctions = get_all_auctions()
    current_user = get_current_user()
    return render_template('all-auctions.html', auctions=auctions, current_user=current_user)

@app.route('/users')
def all_users():
    """Admin page to view all users"""
    users = get_all_users()
    return render_template('users.html', users=users)

@app.route('/debug/users')
def debug_users():
    """Debug route to show all users with passwords"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, password_hash as password, balance, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format for easy viewing
        output = "<h1>All Users in Database</h1><table border='1' style='border-collapse: collapse; width: 100%;'>"
        output += "<tr><th>ID</th><th>Name</th><th>Email</th><th>Password</th><th>Balance</th><th>Created</th></tr>"
        
        for user in users:
            output += f"<tr><td>{user['id']}</td><td>{user['name']}</td><td>{user['email']}</td><td>{user['password']}</td><td>${user['balance']:.2f}</td><td>{user['created_at']}</td></tr>"
        
        output += "</table>"
        return output
    except Exception as e:
        return f"<h1>Error</h1><p>Could not fetch users: {str(e)}</p>"

@app.route('/debug/bids')
def debug_bids():
    """Debug route to show all bids with user names"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.*, u.name as bidder_name, u.email as bidder_email, 
                   a.title as auction_title, a.current_bid
            FROM bids b 
            JOIN users u ON b.bidder_id = u.id 
            JOIN auctions a ON b.auction_id = a.id 
            ORDER BY b.bid_time DESC
        """)
        bids = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format for easy viewing
        output = "<h1>All Bids in Database</h1><table border='1' style='border-collapse: collapse; width: 100%;'>"
        output += "<tr><th>Bid ID</th><th>Bidder Name</th><th>Bidder Email</th><th>Auction</th><th>Bid Amount</th><th>Bid Time</th></tr>"
        
        for bid in bids:
            output += f"<tr><td>{bid['id']}</td><td>{bid['bidder_name']}</td><td>{bid['bidder_email']}</td><td>{bid['auction_title']}</td><td>${bid['bid_amount']:.2f}</td><td>{bid['bid_time']}</td></tr>"
        
        output += "</table>"
        return output
    except Exception as e:
        return f"<h1>Error</h1><p>Could not fetch bids: {str(e)}</p>"

@app.route('/debug/auctions')
def debug_auctions():
    """Debug route to show all auctions with dates"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, title, start_time, end_time, status, current_bid, starting_price
            FROM auctions 
            ORDER BY end_time
        """)
        auctions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format for easy viewing
        output = "<h1>All Auctions in Database</h1><table border='1' style='border-collapse: collapse; width: 100%;'>"
        output += "<tr><th>ID</th><th>Title</th><th>Start Time</th><th>End Time</th><th>Status</th><th>Starting Price</th><th>Current Bid</th></tr>"
        
        for auction in auctions:
            current_bid = f"${auction['current_bid']:.2f}" if auction['current_bid'] is not None else "None"
            starting_price = f"${auction['starting_price']:.2f}" if auction['starting_price'] is not None else "None"
            
            output += f"<tr><td>{auction['id']}</td><td>{auction['title']}</td><td>{auction['start_time']}</td><td>{auction['end_time']}</td><td>{auction['status']}</td><td>{starting_price}</td><td>{current_bid}</td></tr>"
        
        output += "</table>"
        return output
    except Exception as e:
        return f"<h1>Error</h1><p>Could not fetch auctions: {str(e)}</p>"

@app.route('/bids')
def all_bids():
    """Admin page to view all bids"""
    bids = get_all_bids()
    return render_template('bids.html', bids=bids)

@app.route('/watchlist')
def all_watchlist():
    """Admin page to view all watchlist entries"""
    watchlist = get_all_watchlist()
    return render_template('watchlist.html', watchlist=watchlist)

@app.route('/api/place-bid', methods=['POST'])
@login_required
def place_bid():
    """API endpoint to place a bid"""
    current_user = get_current_user()
    
    print("=== PLACE BID DEBUG START ===")
    print(f"Bid attempt by user: {current_user['name']} (ID: {current_user['id']})")
    print(f"User balance: ${current_user['balance']:.2f}")
    
    conn = None
    
    try:
        auction_id = request.json.get('auction_id')
        bid_amount_str = request.json.get('bid_amount')
        
        print(f"Auction ID: {auction_id}")
        print(f"Bid amount string: '{bid_amount_str}'")
        
        try:
            bid_amount = float(bid_amount_str)
            print(f"Parsed bid amount: ${bid_amount:.2f}")
        except (ValueError, TypeError):
            print("Invalid bid amount format")
            return jsonify({'success': False, 'message': 'Invalid bid amount'}), 400
        
        conn = get_db_connection()
        
        # Get auction details
        print(f"Getting auction details for ID: {auction_id}")
        cursor1 = conn.cursor(dictionary=True)
        cursor1.execute("SELECT * FROM auctions WHERE id = %s", (auction_id,))
        auction = cursor1.fetchone()
        cursor1.close()
        
        if not auction:
            print("Auction not found")
            return jsonify({'success': False, 'message': 'Auction not found'}), 404
        
        print(f"Auction found: '{auction['title']}'")
        print(f"Auction status: {auction['status']}")
        print(f"Auction end time: {auction['end_time']}")
        print(f"Current bid: ${auction['current_bid'] or auction['starting_price']:.2f}")
        print(f"Seller ID: {auction['seller_id']}")
        
        # Check if auction is active
        if auction['status'] != 'active':
            print("Auction is not active")
            return jsonify({'success': False, 'message': 'This auction is no longer active'}), 400
        
        # Check if auction has ended
        if auction['end_time'] and auction['end_time'] < datetime.now():
            print("Auction has ended")
            return jsonify({'success': False, 'message': 'This auction has ended'}), 400
        
        # Check if bid amount is higher than current bid
        current_bid = auction['current_bid'] or auction['starting_price']
        if bid_amount <= current_bid:
            print(f"Bid amount ${bid_amount:.2f} is not higher than current bid ${current_bid:.2f}")
            return jsonify({'success': False, 'message': f'Your bid must be higher than the current bid of ${current_bid:.2f}'}), 400
        
        # Check if user has enough balance
        if float(current_user['balance']) < float(bid_amount):
            needed = float(bid_amount) - float(current_user['balance'])
            print(f"Insufficient balance. Need ${needed:.2f} more")
            return jsonify({'success': False, 'message': f'Insufficient balance. You need ${needed:.2f} more. Visit the Balance page to add funds.'}), 400
        
        # Check if user is not bidding on their own auction
        if auction['seller_id'] == current_user['id']:
            print("User trying to bid on their own auction")
            return jsonify({'success': False, 'message': 'You cannot bid on your own auction'}), 400
        
        # Refund previous bidder if exists
        print("Checking for previous bidder to refund...")
        cursor2 = conn.cursor(dictionary=True)
        cursor2.execute("""
            SELECT bidder_id, bid_amount FROM bids 
            WHERE auction_id = %s AND bid_amount = %s
            LIMIT 1
        """, (auction_id, current_bid))
        previous_bid = cursor2.fetchone()
        cursor2.close()
        
        if previous_bid and previous_bid['bidder_id'] != current_user['id']:
            print(f"Refunding previous bidder {previous_bid['bidder_id']} amount ${previous_bid['bid_amount']:.2f}")
            
            # Get current balance of previous bidder
            cursor3 = conn.cursor()
            cursor3.execute("SELECT balance FROM users WHERE id = %s", (previous_bid['bidder_id'],))
            prev_balance_result = cursor3.fetchone()
            cursor3.close()
            
            if prev_balance_result:
                prev_current_balance = prev_balance_result[0]
                prev_new_balance = float(prev_current_balance) + float(previous_bid['bid_amount'])
                
                # Update previous bidder's balance
                cursor4 = conn.cursor()
                cursor4.execute("UPDATE users SET balance = %s WHERE id = %s", 
                             (prev_new_balance, previous_bid['bidder_id']))
                cursor4.close()
                
                # Add refund transaction for previous bidder
                cursor5 = conn.cursor()
                cursor5.execute("""
                    INSERT INTO balance_transactions (user_id, transaction_type, amount, description, auction_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (previous_bid['bidder_id'], 'refund', previous_bid['bid_amount'], 
                      f'Refund: Outbid on "{auction["title"]}"', auction_id))
                cursor5.close()
                
                print("Previous bidder refunded successfully")
            else:
                print("Previous bidder not found, skipping refund")
        else:
            print("No previous bidder to refund")
        
        # Deduct bid amount from current user's balance
        print(f"Deducting ${bid_amount:.2f} from user balance...")
        new_balance = float(current_user['balance']) - float(bid_amount)
        cursor6 = conn.cursor()
        cursor6.execute("UPDATE users SET balance = %s WHERE id = %s", 
                      (new_balance, current_user['id']))
        cursor6.close()
        
        # Add bid transaction for current user
        print("Adding bid transaction...")
        cursor7 = conn.cursor()
        cursor7.execute("""
            INSERT INTO balance_transactions (user_id, transaction_type, amount, description, auction_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user['id'], 'bid', bid_amount, 
              f'Bid placed on "{auction["title"]}"', auction_id))
        cursor7.close()
        
        # Insert new bid
        print("Inserting new bid record...")
        cursor8 = conn.cursor()
        cursor8.execute("INSERT INTO bids (auction_id, bidder_id, bid_amount) VALUES (%s, %s, %s)",
                      (auction_id, current_user['id'], bid_amount))
        bid_id = cursor8.lastrowid
        cursor8.close()
        print(f"Bid record created with ID: {bid_id}")
        
        # Update auction current bid and bid count
        print("Updating auction current bid...")
        cursor9 = conn.cursor()
        cursor9.execute("UPDATE auctions SET current_bid = %s, total_bids = total_bids + 1 WHERE id = %s",
                      (bid_amount, auction_id))
        cursor9.close()
        
        # Commit all changes
        conn.commit()
        
        print(f"Bid placed successfully! New balance: ${new_balance:.2f}")
        print("=== PLACE BID DEBUG END (success) ===")
        
        return jsonify({
            'success': True, 
            'message': f'Congratulations! Your bid of ${bid_amount:.2f} has been placed successfully. You are now the highest bidder!',
            'new_balance': new_balance
        })
        
    except ValueError as e:
        print(f"ValueError in bid: {e}")
        return jsonify({'success': False, 'message': 'Invalid bid amount'}), 400
    except mysql.connector.Error as e:
        print(f"MySQL error in bid: {e}")
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected bid error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'message': f'Failed to place bid: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/add-to-watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    """API endpoint to add auction to watchlist"""
    current_user = get_current_user()
    
    try:
        auction_id = request.json.get('auction_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if already in watchlist
        cursor.execute("SELECT id FROM watchlist WHERE user_id = %s AND auction_id = %s", 
                      (current_user['id'], auction_id))
        existing = cursor.fetchone()
        
        if existing:
            return jsonify({'success': False, 'message': 'Already in watchlist'})
        
        # Add to watchlist
        cursor.execute("INSERT INTO watchlist (user_id, auction_id) VALUES (%s, %s)",
                      (current_user['id'], auction_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Added to watchlist successfully'})
    except Exception as e:
        print(f"Watchlist error: {e}")
        return jsonify({'success': False, 'message': 'Error adding to watchlist'}), 400

@app.route('/api/recharge-balance', methods=['POST'])
@login_required
def recharge_balance():
    """API endpoint to add balance (free recharge feature)"""
    current_user = get_current_user()
    
    print("=== BALANCE RECHARGE DEBUG START ===")
    print(f"Recharge attempt by user: {current_user['name']} (ID: {current_user['id']})")
    print(f"Current balance: ${current_user['balance']:.2f}")
    
    try:
        amount_str = request.json.get('amount', 0)
        print(f"Requested amount: '{amount_str}'")
        
        try:
            amount = float(amount_str)
            print(f"Parsed amount: {amount}")
        except (ValueError, TypeError):
            print("Invalid amount format")
            return jsonify({'success': False, 'message': 'Please enter a valid amount'}), 400
        
        if amount <= 0:
            print("Amount is zero or negative")
            return jsonify({'success': False, 'message': 'Please enter an amount greater than $0'}), 400
            
        if amount > 10000:
            print("Amount exceeds maximum limit")
            return jsonify({'success': False, 'message': 'Maximum recharge amount is $10,000 per transaction'}), 400
        
        print(f"Attempting to add ${amount:.2f} to user balance...")
        
        # Add balance
        balance_updated = update_user_balance(current_user['id'], amount, 'add')
        if not balance_updated:
            print("Failed to update user balance")
            return jsonify({'success': False, 'message': 'Failed to update balance. Please try again.'}), 500
        
        print("Balance updated successfully, adding transaction record...")
        
        # Add transaction record
        transaction_added = add_balance_transaction(current_user['id'], 'recharge', abs(float(amount)), f'Free balance recharge of ${amount:.2f}')
        if not transaction_added:
            print("Warning: Failed to add transaction record")
        
        new_balance = float(current_user['balance']) + float(amount)
        print(f"New balance: ${new_balance:.2f}")
        
        print("=== BALANCE RECHARGE DEBUG END (success) ===")
        
        return jsonify({
            'success': True, 
            'message': f'🎉 Successfully added ${amount:.2f} to your account! Your new balance is ${new_balance:.2f}',
            'new_balance': new_balance
        })
        
    except ValueError as e:
        print(f"ValueError in recharge: {e}")
        return jsonify({'success': False, 'message': 'Please enter a valid amount'}), 400
    except mysql.connector.Error as e:
        print(f"MySQL error in recharge: {e}")
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        print(f"Unexpected recharge error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Failed to process recharge: {str(e)}'}), 500

@app.route('/balance')
@login_required
def balance_page():
    """Balance management page"""
    current_user = get_current_user()
    
    # Get balance transaction history
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT bt.*, a.title as auction_title 
            FROM balance_transactions bt 
            LEFT JOIN auctions a ON bt.auction_id = a.id 
            WHERE bt.user_id = %s 
            ORDER BY bt.created_at DESC 
            LIMIT 50
        """, (current_user['id'],))
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        transactions = []
    
    return render_template('balance.html', current_user=current_user, transactions=transactions)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/admin/edit-auction/<int:auction_id>', methods=['GET', 'POST'])
def edit_auction_admin(auction_id):
    """Admin page to edit auction details"""
    if request.method == 'POST':
        try:
            new_end_time = request.form.get('end_time')
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE auctions 
                SET end_time = %s 
                WHERE id = %s
            """, (new_end_time, auction_id))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Auction end time updated successfully!', 'success')
            return redirect(url_for('all_auctions'))
        except Exception as e:
            flash(f'Error updating auction: {str(e)}', 'error')
    
    # Get auction details
    auction = get_auction_by_id(auction_id)
    if not auction:
        flash('Auction not found', 'error')
        return redirect(url_for('all_auctions'))
    
    return render_template('edit_auction_admin.html', auction=auction)

@app.route('/admin')
def admin_panel():
    """Comprehensive admin panel for managing auctions and users"""
    auctions = get_all_auctions()
    users = get_all_users()
    return render_template('admin.html', auctions=auctions, users=users)

@app.route('/admin/update-auction/<int:auction_id>', methods=['POST'])
def update_auction_admin(auction_id):
    """Update auction details via admin panel"""
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        starting_price = float(request.form.get('starting_price'))
        end_time = request.form.get('end_time')
        status = request.form.get('status')
        image_url = request.form.get('image_url')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE auctions 
            SET title = %s, description = %s, starting_price = %s, 
                end_time = %s, status = %s, image_url = %s
            WHERE id = %s
        """, (title, description, starting_price, end_time, status, image_url, auction_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Auction updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/delete-auction/<int:auction_id>', methods=['DELETE'])
def delete_auction_admin(auction_id):
    """Delete auction via admin panel"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First delete related bids
        cursor.execute("DELETE FROM bids WHERE auction_id = %s", (auction_id,))
        
        # Then delete the auction
        cursor.execute("DELETE FROM auctions WHERE id = %s", (auction_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Auction deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
if __name__ == "__main__":
    print("Starting Flask app in debug mode...")
    app.run(debug=True)