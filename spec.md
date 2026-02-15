# EcoStream Technical Specification

## System Overview
EcoStream is a microservices platform for "last-mile" delivery optimization using GenAI.

## Service Map
1. **Order Service (Java/Spring Boot)**
   - Responsibility: CRUD for orders, orchestration.
   - Port: 8082
   - DB: PostgreSQL (Orders), DynamoDB (Real-time tracking).
2. **AI Service (Python/FastAPI)**
   - Responsibility: Delay prediction (Scikit-Learn), Route Analysis.
   - Port: 5050 (5000–5035 often in Windows excluded range)
   - Integration: Amazon Bedrock (GenAI Assistant).
3. **DynamoDB Local**
   - Port: 9000 (external, 8000 internal)

## Core Data Model
- **Order:** { id: UUID, status: Enum, destination: Lat/Lng, priority: Int }
- **Telemetry:** { orderId: UUID, currentCoords: Lat/Lng, timestamp: ISO8601 }

## Integration Contract
- `POST http://localhost:5050/predict/delay`: Accepts order details, returns estimated delay minutes.