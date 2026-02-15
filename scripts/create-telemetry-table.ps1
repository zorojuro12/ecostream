# Script to create DynamoDB Local telemetry table for EcoStream
# Table: ecostream-telemetry-local
# Endpoint: http://localhost:9000

Write-Host "Creating DynamoDB Local table: ecostream-telemetry-local" -ForegroundColor Cyan

aws dynamodb create-table `
    --table-name ecostream-telemetry-local `
    --attribute-definitions AttributeName=orderId,AttributeType=S AttributeName=timestamp,AttributeType=N `
    --key-schema AttributeName=orderId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE `
    --billing-mode PAY_PER_REQUEST `
    --endpoint-url http://localhost:9000 `
    --region us-east-1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Table created successfully!" -ForegroundColor Green
} else {
    Write-Host "Error creating table. It may already exist." -ForegroundColor Yellow
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Yellow
}
