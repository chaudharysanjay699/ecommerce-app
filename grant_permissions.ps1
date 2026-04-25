# Connect to AWS RDS PostgreSQL and grant permissions
# Replace MASTER_USER with your RDS master username (e.g., postgres or admin)

$MASTER_USER = "postgres"  # <-- Change this to your RDS master user
$DB_HOST = "vidharthi-store.cn6ms82i6v4t.ap-south-1.rds.amazonaws.com"
$DB_NAME = "vidharthi_store"
$DB_PORT = "5432"

Write-Host "Connecting to RDS database as $MASTER_USER..." -ForegroundColor Cyan
Write-Host "You will be prompted for the master user password." -ForegroundColor Yellow
Write-Host ""

# Run the SQL file using psql
psql -h $DB_HOST -p $DB_PORT -U $MASTER_USER -d $DB_NAME -f fix_permissions.sql

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Permissions granted successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now run: alembic upgrade head" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[ERROR] Failed to grant permissions." -ForegroundColor Red
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. psql is installed (install PostgreSQL client tools)" -ForegroundColor Yellow
    Write-Host "  2. You have the correct master user password" -ForegroundColor Yellow
    Write-Host "  3. The RDS security group allows your IP address" -ForegroundColor Yellow
}
