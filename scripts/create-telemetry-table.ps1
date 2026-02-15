# Script to create DynamoDB Local telemetry table for EcoStream
# Table: ecostream-telemetry-local
# Endpoint: http://localhost:9000
# Idempotent: exits 0 if table already exists.

$tableName = "ecostream-telemetry-local"
$endpoint = "http://localhost:9000"

# Check if table already exists
aws dynamodb describe-table --table-name $tableName --endpoint-url $endpoint --region us-east-1 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Table '$tableName' already exists. Ready for telemetry." -ForegroundColor Green
    exit 0
}

Write-Host "Creating DynamoDB Local table: $tableName" -ForegroundColor Cyan

aws dynamodb create-table `
    --table-name $tableName `
    --attribute-definitions AttributeName=orderId,AttributeType=S AttributeName=timestamp,AttributeType=N `
    --key-schema AttributeName=orderId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url $endpoint `
    --region us-east-1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Table created successfully!" -ForegroundColor Green
} else {
    Write-Host "Error creating table. It may already exist." -ForegroundColor Yellow
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Yellow
    exit $LASTEXITCODE
}
