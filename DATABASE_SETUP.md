# Database Setup Instructions

## The Problem
You're getting the error: `Database error during user check: 1049 (42000): Unknown database 'online_auction'`

This means the MySQL database doesn't exist yet. Here's how to fix it:

## Quick Fix (Choose one method)

### Method 1: Use the Automated Setup Script (Recommended)
1. **Run the PowerShell script** (if you're comfortable with PowerShell):
   ```powershell
   .\setup_database.ps1
   ```

2. **OR run the Batch file** (simpler):
   ```cmd
   setup_database.bat
   ```

### Method 2: Manual MySQL Setup
1. **Open MySQL Command Line** or **MySQL Workbench**

2. **Create the database and run the setup script**:
   ```sql
   mysql -u root -p < setup_complete_database.sql
   ```

3. **If you don't have a password**:
   ```sql
   mysql -u root < setup_complete_database.sql
   ```

### Method 3: Step-by-Step Manual Setup
1. **Open MySQL Command Line**:
   ```cmd
   mysql -u root -p
   ```

2. **Create the database**:
   ```sql
   CREATE DATABASE online_auction;
   USE online_auction;
   ```

3. **Run the complete setup script**:
   ```sql
   source setup_complete_database.sql
   ```

4. **Exit MySQL**:
   ```sql
   exit
   ```

## Verify the Setup
After running any of the above methods, test the database:

```cmd
python debug_db.py
```

You should see:
```
=== TESTING DATABASE CONNECTION ===
✓ Database connection successful
✓ MySQL version: 8.0.xx
✓ Current database: online_auction
```

## Update Flask App Configuration
If you use a different MySQL username or password, update the `DB_CONFIG` in `app.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_username',    # Change this if needed
    'password': 'your_mysql_password', # Change this if needed
    'database': 'online_auction'
}
```

## Test Registration
After setup, try registering a user:
1. Run `python app.py`
2. Go to `http://localhost:5000/register`
3. Fill out the form and submit

You should now see detailed debug output instead of the database error.

## Sample Data Included
The setup script includes:
- 5 sample users (john@example.com, jane@example.com, etc.)
- 5 sample auctions
- Sample bids and watchlist entries
- Balance transactions

**Sample login credentials:**
- Email: `john@example.com`
- Password: `password123`

## Common Issues

### Issue: "mysql command not found"
**Solution**: Install MySQL or add it to your PATH
- Download from: https://dev.mysql.com/downloads/installer/

### Issue: "Access denied for user"
**Solution**: Check your MySQL username and password
- Default username is usually `root`
- Use the password you set during MySQL installation

### Issue: "Can't connect to MySQL server"
**Solution**: Make sure MySQL service is running
- Windows: Start MySQL service in Services panel
- Or restart MySQL using MySQL Workbench

## Files Created
- `setup_complete_database.sql` - Complete database setup with sample data
- `setup_database.ps1` - PowerShell setup script
- `setup_database.bat` - Batch file setup script
- `debug_db.py` - Database testing script

Run the setup and your registration should work perfectly!
