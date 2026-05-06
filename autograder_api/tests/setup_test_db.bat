@echo off
echo Creating test database...

set /p DB_USER="Enter MySQL user (default: root): "
set /p DB_PASS="Enter MySQL password (default: password): "

if "%DB_USER%"=="" set DB_USER=root
if "%DB_PASS%"=="" set DB_PASS=password

mysql -u %DB_USER% -p%DB_PASS% -e "CREATE DATABASE IF NOT EXISTS autograder_test;"

echo Test database created successfully!
echo.
echo To run tests, use:
echo   python -m pytest tests\ -v