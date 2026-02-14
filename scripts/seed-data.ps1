# Seed test orders for EcoStream (Order Service on port 8082)
# Uses SFU-area coordinates: Burnaby Campus, Vancouver Campus, Metrotown

$baseUrl = "http://localhost:8082/api/orders"
$headers = @{
    "Content-Type" = "application/json"
}

$orders = @(
    @{
        status     = "PENDING"
        destination = @{ latitude = 49.2276; longitude = -123.0076 }  # Metrotown
        priority   = 5
    },
    @{
        status     = "CONFIRMED"
        destination = @{ latitude = 49.2820; longitude = -123.1085 }  # SFU Vancouver Campus
        priority   = 3
    },
    @{
        status     = "PENDING"
        destination = @{ latitude = 49.2781; longitude = -122.9199 }  # SFU Burnaby Campus
        priority   = 7
    }
)

Write-Host "Seeding 3 orders to $baseUrl ..." -ForegroundColor Cyan

foreach ($order in $orders) {
    $body = $order | ConvertTo-Json
    try {
        $response = Invoke-RestMethod -Uri $baseUrl -Method Post -Headers $headers -Body $body
        Write-Host "Created order: $($response.id)" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to create order: $_" -ForegroundColor Red
    }
}

Write-Host "Done. Refresh the dashboard to see orders." -ForegroundColor Cyan
