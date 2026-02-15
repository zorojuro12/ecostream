# Forecast 422 & Dashboard Distance/ETA – Debug Report

**Project:** EcoStream  
**Scope:** Order Service (Java) ↔ AI Forecasting Service (Python) ↔ Dashboard  
**Report date:** February 2025

---

## 1. Summary of Issues

| # | Issue | Impact |
|---|--------|--------|
| 1 | **422 Unprocessable Entity** on `POST /api/forecast/{order_id}` from Java to Python | AI service rejects every forecast request; no Distance/ETA returned. |
| 2 | **Missing body** at Python | Validation error: `"loc": ["body"], "msg": "Field required", "input": null` — FastAPI receives **no request body**. |
| 3 | **Dashboard shows no Distance, ETA, or red dot** | Depends on forecast API; until 422 is fixed, list and detail stay empty for these fields. |
| 4 | **Telemetry 500** (earlier, fixed) | Simulator and Java API payload mismatch; fixed with `TelemetryRequestDTO` and correct fields. |
| 5 | **Dashboard always "—" for Distance/ETA** (earlier, fixed) | Only `getOrderById` was enriched with forecast; fixed by enriching **both** `getAllOrders` and `getOrderById` in `OrderServiceImpl`. |
| 6 | **Python service won’t start** | `ModuleNotFoundError: No module named 'app'` when running uvicorn from wrong directory (e.g. `order-service-java`). **Fix:** Run uvicorn from `services/ai-forecasting-python`. |
| 7 | **Port 5000 in use or forbidden (10013)** | `Errno 10048` (in use) or `10013` (forbidden on Windows). **Fix:** AI service now defaults to **port 5001**; Order service uses `ai.forecasting.base-url=http://localhost:5001`. For 10048, stop the process on the port or use another port. |

The **remaining open problem** is **(1)–(2)**: the Python service still receives **no body** on forecast POSTs, so every request returns 422.

---

## 2. Root Cause (Confirmed by Logs)

- **Debug log** (e.g. `.cursor/debug.log`) and Python 422 handler show:
  - `"validation_errors": [{"type": "missing", "loc": ["body"], "msg": "Field required", "input": null}]`
- So the **HTTP request body is missing** at the Python side (body is `null` when FastAPI tries to parse it).
- All forecast traffic comes from the **Order Service (Java)**; the dashboard only calls `http://localhost:8082/api/orders` and does not call the AI service directly.

---

## 3. What We’ve Already Tried (Java → Python body)

| # | Change | Result |
|---|--------|--------|
| 1 | **Python:** `ForecastRequest` schema with `ConfigDict(populate_by_name=True)` and `Field(..., alias="destinationLatitude")` (and same for longitude) so both snake_case and camelCase are accepted. | 422 unchanged; error is **body missing**, not field names. |
| 2 | **Java:** Introduced `ForecastRequestDTO` (record with `@JsonProperty("destination_latitude")`, etc.) and sent it instead of a `Map`. | 422 unchanged; body still missing at Python. |
| 3 | **Java:** Switched from `postForObject(url, request, ...)` with `HttpEntity<ForecastRequestDTO>` to **`postForObject(url, body, ForecastResponseDTO.class)`** (send DTO only, no `HttpEntity`). | 422 unchanged; body still missing. |
| 4 | **Java:** Switched to **`restTemplate.exchange(url, HttpMethod.POST, entity, ForecastResponseDTO.class)`** with explicit `HttpEntity<ForecastRequestDTO>(body, headers)` and `Content-Type: application/json`. | 422 unchanged; body still missing. |
| 5 | **Java:** **Explicit JSON serialization** — inject `ObjectMapper`, call `objectMapper.writeValueAsString(body)`, send **`HttpEntity<String>(jsonBody, headers)`** so RestTemplate sends a plain JSON string. | 422 still reported; body still missing at Python (user confirmed “still not working”). |

So far, **no Java-side change has made the body appear** at the Python service, which suggests either:

- The **Order service wasn’t restarted** after one or more of these changes (so the old client code was still running), or  
- **RestTemplate / HTTP stack** is not actually writing the body (e.g. converter, client, or OS/network quirk), or  
- We need **runtime proof** of what the server receives (e.g. middleware logging `Content-Length` / raw body).

---

## 4. Instrumentation Added (Still in Place)

- **Python (`app/main.py`):**
  - **422 handler:** On `RequestValidationError`, prints `[FORECAST 422] path= ... validation_errors= ...` and appends one NDJSON line to **`.cursor/debug.log`** with `path`, `validation_errors`, and `timestamp`.
  - **Middleware:** For `POST /api/forecast/...`, appends a line to **`.cursor/debug.log`** with `message: "forecast_request"`, `path`, **`content_length`**, **`content_type`**, and `timestamp` (without reading the body, so it doesn’t consume it).
- **Java:** Earlier telemetry debug logging to `.cursor/debug.log` was added in `OrderServiceImpl` / `TelemetryRepository`; keep or remove per your preference once telemetry is verified.

**Next step with instrumentation:** After **restarting both Order and AI services** and triggering forecast requests (e.g. dashboard refresh), inspect `debug.log`:

- If **`forecast_request`** entries have **`content_length` null or `"0"`** → client (Java) is not sending a body; focus on RestTemplate / client config and restarts.
- If **`content_length` > 0** → body is reaching the server and the issue is likely in how FastAPI/Starlette reads or parses the body.

---

## 5. Relevant Files

| Layer | File | Role |
|-------|------|------|
| Java | `services/order-service-java/.../client/ForecastingClientImpl.java` | Calls `POST /api/forecast/{id}` with JSON body (currently via `ObjectMapper.writeValueAsString` + `HttpEntity<String>`). |
| Java | `services/order-service-java/.../client/ForecastRequestDTO.java` | Request body DTO: `destination_latitude`, `destination_longitude`, `priority`. |
| Java | `services/order-service-java/.../service/OrderServiceImpl.java` | `enrichWithForecast()` calls `forecastingClient.getForecast(...)` for list and detail. |
| Python | `services/ai-forecasting-python/app/main.py` | 422 handler + middleware logging to `debug.log`. |
| Python | `services/ai-forecasting-python/app/api/schemas.py` | `ForecastRequest` (destination_latitude/longitude, priority). |
| Python | `services/ai-forecasting-python/app/api/forecasting_routes.py` | `POST /{order_id}` with `request: ForecastRequest`. |
| Debug | `d:\Personal Projects\ecostream\.cursor\debug.log` | NDJSON log: `forecast_request` (headers) and `forecast_422` (validation errors). |

---

## 6. Ports & Run Commands

| Service | Port | Run from directory | Command |
|---------|------|--------------------|--------|
| Order (Java) | 8082 | `services/order-service-java` | `mvn spring-boot:run` |
| AI (Python) | 5050 | `services/ai-forecasting-python` | `uvicorn app.main:app --host 0.0.0.0 --port 5050` or `.\start-ai-service.ps1` |
| DynamoDB Local | 9000 | — | Table: `ecostream-telemetry-local` |
| PostgreSQL | 5432 | — | For orders DB |
| Dashboard | (dev server) | `services/web-dashboard-ts` | e.g. `npm run dev` |

---

## 7. Recommended Next Steps

1. **Restart both services**, clear or ignore old `.cursor/debug.log`, then trigger forecast requests (e.g. dashboard refresh).
2. **Inspect `debug.log`** for `forecast_request` and `forecast_422` entries and note `content_length` for each POST.
3. If **content_length is missing or 0:**  
   - Ensure the Order service process was fully restarted after the last Java change.  
   - Consider adding a `ClientHttpRequestInterceptor` in Java to log the outgoing request body (or use a debugger) to confirm RestTemplate is writing the JSON.
4. If **content_length > 0:**  
   - Inspect Python body parsing (e.g. read raw body in middleware and log it, then re-inject it for the route if needed) and Content-Type handling.
5. After the 422 is resolved and Distance/ETA and red dot work, **remove or reduce** the temporary debug instrumentation (422 handler log, middleware, and any Java telemetry file logging) as desired.

---

*This report summarizes the forecast 422 investigation and fixes attempted up to the point where explicit JSON body sending was added and middleware logging was introduced for request headers.*
