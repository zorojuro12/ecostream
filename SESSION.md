# EcoStream Session State

## Last Updated
2026-03-31 — Live AWS deployment (Lambda + API Gateway + DynamoDB + S3)

## Priority List (Interview Readiness)

### Active / Remaining
All 8 priorities complete.

### Completed
| # | Task | Date |
|---|------|------|
| 8 | Structured JSON logging (Python) | 2026-03-29 |
| 7 | Add dashboard to CI + component tests | 2026-03-29 |
| 6 | Deploy AI service to real Lambda (minimal SAM) | 2026-03-29 |
| 5 | Wire S3 logger into forecast flow | 2026-03-29 |
| 4 | Spring Boot Actuator + Resilience4j circuit breaker | 2026-03-29 |
| 3 | Live delivery map (Leaflet.js) | 2025-03-25 |
| 2 | Train real ML model on NYC Taxi data | 2025-03-25 |
| 1 | Clean up debug.log instrumentation (Java + Python) | 2025-03-25 |
| — | Fix stale cursor rules, progress.md, duplicate READMEs | 2025-03-25 |
| — | Add SESSION.md, function doc rule, cleanup rule | 2025-03-25 |

### Deprioritized (Don't Matter for Intern Interview)
| Task | Why It Doesn't Matter |
|------|----------------------|
| Full IaC (CDK/SAM for every service) | Weeks of work; interviewers care about understanding concepts, not having full infra deployed. The minimal Lambda deploy (Priority #6) is sufficient. |
| CodeDeploy blue/green deployments | No intern interviewer will probe deployment strategy mechanics. |
| 100% test coverage enforcement in CI | Nice metric, not a differentiator. Having tests matters; coverage gates don't. |
| Ruff in CI pipeline | Formatting enforcement is invisible to interviewers. Local usage is enough. |
| Serverless data pipeline (Kinesis/IoT Core) | High effort, low interview ROI. The synchronous REST telemetry flow works fine. |
| CloudWatch dashboards/alarms as code | Understand concepts for interview; building JSON alarm definitions adds no value. |
| Delay alerts / notification system | Feature scope creep. The assistant chat already provides proactive insights. |

## Active Context
- **Branch:** `feat/cloud-readiness`
- **Just completed:** Live AWS deployment. Lambda + API Gateway + DynamoDB + S3 all verified live in us-east-1.
- **Live endpoint:** `https://pdhwud69fj.execute-api.us-east-1.amazonaws.com/prod`
- **All priorities complete.** Project is interview-ready with real deployed AWS infrastructure.

## Key Decisions Made
- **Circuit breaker config:** Count-based sliding window (size=10, threshold=50%, min calls=5) — request volume is low so time-based would need higher traffic. 10s wait in OPEN, 3 probes in HALF_OPEN.
- **Fallback strategy:** Returns null, same as the existing catch block in `enrichWithForecast`. Orders are served without ETA when the AI service is down.
- **Timeout adjustment:** RestTemplate 500ms → 1s connect / 2s read. The circuit breaker handles sustained failures, so individual calls can be more generous.
- **ML model:** Used NYC Taxi Trip Duration (Kaggle) rather than synthetic data. Priority is a synthetic column (20% Express with 15-20% speed boost).
- **Model choice:** RandomForest over Ridge — better at non-linear hour/distance interactions. R² 0.45, MAE 4.24 km/h.
- **Speed not duration:** Model predicts speed (km/h), not trip duration. ETA = distance / predicted_speed.
- **Time features from server:** hour_of_day, day_of_week, month from `datetime.now()`, not from request.
- **Map telemetry source:** Option B (dashboard fetches from Python service directly) — avoids Java DTO changes.

## Files Recently Modified (JSON Logging)
- `services/ai-forecasting-python/app/utils/logging_config.py` (new — JsonFormatter + configure_logging)
- `services/ai-forecasting-python/app/main.py` (call configure_logging at startup)
- `services/ai-forecasting-python/tests/test_logging_config.py` (new — 2 tests)
- `progress.md`, `SESSION.md`

## Tradeoffs & Deferred Alternatives
| Decision | What We Chose | Alternative | Why Deferred |
|----------|--------------|-------------|--------------|
| Circuit breaker test approach | **Unit test** with manual `CircuitBreakerRegistry` (no Spring context, no DB needed) | `@SpringBootTest` with full context | Full context requires PostgreSQL running; unit approach is faster, isolated, and tests the same CB behaviour. |
| Map telemetry source | **Option B:** Dashboard calls Python `GET /api/test/telemetry/{order_id}` directly | **Option A:** Add `currentLatitude`/`currentLongitude` to Java `OrderResponseDTO` so a single GET returns everything | Option A requires Java DTO changes, DynamoDB read in the GET path, and re-testing the Order Service. Option B is faster (endpoint already exists, CORS configured) and keeps map work scoped to dashboard only. Migrate to Option A later if latency matters. |
| Forecast route body parsing | **Standard FastAPI body injection** (`request: ForecastRequest` param) | Keep manual `request.body()` + `model_validate_json` workaround | The manual parsing was a debug workaround for the RestTemplate body bug (now fixed via `BufferingClientHttpRequestFactory`). Standard injection is cleaner, less code, and all 14 tests pass. |
| ML model dataset | Real Kaggle data (NYC Taxi Trip Duration) | Synthetic generated data | Synthetic is faster but weaker in interviews. Real data gives richer "Dive Deep" story. |

## How to Resume
Tell the AI: "Read `SESSION.md`, `progress.md`, and `spec.md` to get context. Continue from where we left off."
