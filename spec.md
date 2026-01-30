# EcoStream Technical Specification

## System Overview
EcoStream is a microservices platform for "last-mile" delivery optimization using GenAI.

## Service Map
1. **Order Service (Java/Spring Boot)**
   - Responsibility: CRUD for orders, orchestration.
   - DB: PostgreSQL (Orders), DynamoDB (Real-time tracking).
2. **AI Service (Python/FastAPI)**
   - Responsibility: Delay prediction (Scikit-Learn), Route Analysis.
   - Integration: Amazon Bedrock (GenAI Assistant).

## Core Data Model
- **Order:** { id: UUID, status: Enum, destination: Lat/Lng, priority: Int }
- **Telemetry:** { orderId: UUID, currentCoords: Lat/Lng, timestamp: ISO8601 }

## Integration Contract
- `POST http://localhost:8000/predict/delay`: Accepts order details, returns estimated delay minutes.