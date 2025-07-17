@echo off
echo BidMaster Database Setup
echo =========================
echo.

REM Check if MySQL is available
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: MySQL not found in PATH.
    echo Please install MySQL or add it to your PATH.
    echo Download from: https://dev.mysql.com/downloads/installer/
    pause
    exit /b 1
)

echo MySQL found!
echo.

REM Prompt for credentials
set /p mysql_user="MySQL username (default: root): "
if "%mysql_user%"=="" set mysql_user=root

set /p mysql_password="MySQL password (press Enter if no password): "

echo.
echo Testing MySQL connection...

REM Test connection
if "%mysql_password%"=="" (
    mysql -u %mysql_user% -e "SELECT 'Connection successful' as status;"
) else (
    mysql -u %mysql_user% -p%mysql_password% -e "SELECT 'Connection successful' as status;"
)

if %errorlevel% neq 0 (
    echo ERROR: Could not connect to MySQL. Please check your credentials.
    pause
    exit /b 1
)

echo MySQL connection successful!
echo.

echo Setting up BidMaster database...

REM Run database setup
if "%mysql_password%"=="" (
    mysql -u %mysql_user% < setup_complete_database.sql
) else (
    mysql -u %mysql_user% -p%mysql_password% < setup_complete_database.sql
)

if %errorlevel% neq 0 (
    echo ERROR: Failed to set up database.
    pause
    exit /b 1
)

echo Database setup completed successfully!
echo.

echo Testing database...
if "%mysql_password%"=="" (
    mysql -u %mysql_user% -D online_auction -e "SHOW TABLES;"
) else (
    mysql -u %mysql_user% -p%mysql_password% -D online_auction -e "SHOW TABLES;"
)

echo.
echo ====================================================
echo SETUP COMPLETE!
echo ====================================================
echo Your BidMaster database is now ready!
echo.
echo Next steps:
echo 1. Test the database with: python debug_db.py
echo 2. Start the Flask app with: python app.py
echo 3. Open your browser to: http://localhost:5000
echo.
echo Sample login credentials:
echo Email: john@example.com
echo Password: password123
echo.
pause
