# EcoStream Session State

## Last Updated
2025-03-25 — Implemented live delivery map (Priority #3)

## Priority List (Interview Readiness)

### Active / Remaining
| # | Task | Status | Est. Time |
|---|------|--------|-----------|
| 4 | Spring Boot Actuator + Resilience4j circuit breaker | **NEXT** | 2-3 hrs |
| 5 | Wire S3 logger into forecast flow | PENDING | 15-30 min |
| 6 | Deploy AI service to real Lambda (minimal SAM) | PENDING | 2-3 hrs |
| 7 | Add dashboard to CI + component tests | PENDING | 1-2 hrs |
| 8 | Structured JSON logging (Python) | PENDING | 1 hr |

### Completed
| # | Task | Date |
|---|------|------|
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
- **Just completed:** Live delivery map (Priority #3) — Leaflet.js `DeliveryMap` component with CARTO dark tiles, vehicle/destination markers, route polyline, 5s telemetry polling from Python service.
- **Up next:** Priority #4 — Spring Boot Actuator + Resilience4j circuit breaker for Order Service.

## Key Decisions Made
- **ML model:** Used NYC Taxi Trip Duration (Kaggle) rather than synthetic data. Priority is a synthetic column (20% Express with 15-20% speed boost).
- **Model choice:** RandomForest over Ridge — better at non-linear hour/distance interactions. R² 0.45, MAE 4.24 km/h.
- **Speed not duration:** Model predicts speed (km/h), not trip duration. ETA = distance / predicted_speed.
- **Time features from server:** hour_of_day, day_of_week, month from `datetime.now()`, not from request.
- **Map telemetry source:** Option B (dashboard fetches from Python service directly) — avoids Java DTO changes.

## Files Recently Modified (Map Feature)
- `services/web-dashboard-ts/src/components/DeliveryMap.tsx` (new)
- `services/web-dashboard-ts/src/api/telemetryClient.ts` (new)
- `services/web-dashboard-ts/src/App.tsx` (modified — telemetry state + map integration)
- `services/web-dashboard-ts/src/main.tsx` (modified — Leaflet CSS import)
- `services/web-dashboard-ts/src/index.css` (modified — vehicle marker green tint)
- `services/web-dashboard-ts/package.json` (modified — leaflet + react-leaflet deps)

## Tradeoffs & Deferred Alternatives
| Decision | What We Chose | Alternative | Why Deferred |
|----------|--------------|-------------|--------------|
| Map telemetry source | **Option B:** Dashboard calls Python `GET /api/test/telemetry/{order_id}` directly | **Option A:** Add `currentLatitude`/`currentLongitude` to Java `OrderResponseDTO` so a single GET returns everything | Option A requires Java DTO changes, DynamoDB read in the GET path, and re-testing the Order Service. Option B is faster (endpoint already exists, CORS configured) and keeps map work scoped to dashboard only. Migrate to Option A later if latency matters. |
| Forecast route body parsing | **Standard FastAPI body injection** (`request: ForecastRequest` param) | Keep manual `request.body()` + `model_validate_json` workaround | The manual parsing was a debug workaround for the RestTemplate body bug (now fixed via `BufferingClientHttpRequestFactory`). Standard injection is cleaner, less code, and all 14 tests pass. |
| ML model dataset | Real Kaggle data (NYC Taxi Trip Duration) | Synthetic generated data | Synthetic is faster but weaker in interviews. Real data gives richer "Dive Deep" story. |

## How to Resume
Tell the AI: "Read `SESSION.md`, `progress.md`, and `spec.md` to get context. Continue from where we left off."
