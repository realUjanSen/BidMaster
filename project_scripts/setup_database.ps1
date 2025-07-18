# BidMaster Database Setup Script for Windows
# This script will create the database and set up all necessary tables

Write-Host "BidMaster Database Setup" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check if MySQL is installed and accessible
try {
    $mysqlVersion = mysql --version
    Write-Host "MySQL found: $mysqlVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: MySQL not found in PATH. Please install MySQL or add it to your PATH." -ForegroundColor Red
    Write-Host "You can download MySQL from: https://dev.mysql.com/downloads/installer/" -ForegroundColor Yellow
    exit 1
}

# Prompt for MySQL credentials
Write-Host "`nEnter MySQL credentials:" -ForegroundColor Yellow
$mysqlUser = Read-Host "MySQL username (default: root)"
if ([string]::IsNullOrEmpty($mysqlUser)) {
    $mysqlUser = "root"
}

$mysqlPassword = Read-Host "MySQL password (press Enter if no password)" -AsSecureString
$mysqlPasswordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword))

# Test MySQL connection
Write-Host "`nTesting MySQL connection..." -ForegroundColor Yellow
try {
    if ([string]::IsNullOrEmpty($mysqlPasswordText)) {
        $testCmd = "mysql -u $mysqlUser -e `"SELECT 'Connection successful' as status;`""
    } else {
        $testCmd = "mysql -u $mysqlUser -p$mysqlPasswordText -e `"SELECT 'Connection successful' as status;`""
    }
    
    $result = Invoke-Expression $testCmd
    Write-Host "MySQL connection successful!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Could not connect to MySQL. Please check your credentials." -ForegroundColor Red
    exit 1
}

# Run the database setup script
Write-Host "`nSetting up BidMaster database..." -ForegroundColor Yellow
try {
    if ([string]::IsNullOrEmpty($mysqlPasswordText)) {
        $setupCmd = "mysql -u $mysqlUser < setup_complete_database.sql"
    } else {
        $setupCmd = "mysql -u $mysqlUser -p$mysqlPasswordText < setup_complete_database.sql"
    }
    
    Invoke-Expression $setupCmd
    Write-Host "Database setup completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to set up database. Please check the error message above." -ForegroundColor Red
    exit 1
}

# Test the database
Write-Host "`nTesting database setup..." -ForegroundColor Yellow
try {
    if ([string]::IsNullOrEmpty($mysqlPasswordText)) {
        $testCmd = "mysql -u $mysqlUser -D online_auction -e `"SHOW TABLES;`""
    } else {
        $testCmd = "mysql -u $mysqlUser -p$mysqlPasswordText -D online_auction -e `"SHOW TABLES;`""
    }
    
    $tables = Invoke-Expression $testCmd
    Write-Host "Database tables created:" -ForegroundColor Green
    Write-Host $tables -ForegroundColor Cyan
} catch {
    Write-Host "WARNING: Could not verify database setup." -ForegroundColor Yellow
}

# Update the Flask app configuration if needed
Write-Host "`nUpdating Flask app configuration..." -ForegroundColor Yellow
$appPyPath = "app.py"
if (Test-Path $appPyPath) {
    $appContent = Get-Content $appPyPath -Raw
    
    # Update DB_CONFIG if password is provided
    if (![string]::IsNullOrEmpty($mysqlPasswordText)) {
        $newConfig = @"
DB_CONFIG = {
    'host': 'localhost',
    'user': '$mysqlUser',
    'password': '$mysqlPasswordText',
    'database': 'online_auction'
}
"@
        
        # Replace the existing DB_CONFIG
        $appContent = $appContent -replace "DB_CONFIG = \{[^}]+\}", $newConfig
        Set-Content -Path $appPyPath -Value $appContent
        Write-Host "Flask app configuration updated with your MySQL credentials." -ForegroundColor Green
    } else {
        Write-Host "No password provided, keeping existing configuration." -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: app.py not found. Please manually update your database configuration." -ForegroundColor Yellow
}

Write-Host "`n" + "="*50 -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "="*50 -ForegroundColor Green
Write-Host "Your BidMaster database is now ready!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Test the database with: python debug_db.py" -ForegroundColor Cyan
Write-Host "2. Start the Flask app with: python app.py" -ForegroundColor Cyan
Write-Host "3. Open your browser to: http://localhost:5000" -ForegroundColor Cyan
Write-Host "`nSample login credentials:" -ForegroundColor Yellow
Write-Host "Email: john@example.com" -ForegroundColor Cyan
Write-Host "Password: password123" -ForegroundColor Cyan
