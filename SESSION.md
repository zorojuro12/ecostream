# EcoStream Session State

## Last Updated
2025-03-25 — ML model implementation + rules/docs cleanup

## Current Priority List (Interview Readiness)
1. ~~Clean up debug.log instrumentation~~ — **PENDING** (identified but not yet done)
2. ~~Train real ML model on public data~~ — **DONE** (NYC Taxi, RandomForest, committed)
3. Live delivery map (Leaflet.js) — **PENDING**
4. Spring Boot Actuator + Resilience4j circuit breaker — **PENDING**
5. Wire S3 logger into forecast flow — **PENDING**
6. Deploy AI service to real Lambda (minimal SAM) — **PENDING**
7. Add dashboard to CI + component tests — **PENDING**
8. Structured JSON logging (Python) — **PENDING**

## Active Context
- **Branch:** `feat/cloud-readiness` (2 commits ahead of origin)
- **Just completed:** Trained a real ML model on NYC Taxi Trip Duration dataset (Kaggle, 1.46M trips). RandomForest pipeline with 5 features (distance_km, hour_of_day, day_of_week, month, priority). MAE 4.24 km/h, R² 0.45. Model artifact and processed training data committed. All 14 Python tests pass.
- **Also completed this session:** Fixed stale cursor rules (ports, packages, model ID), corrected false checkmarks in progress.md, deleted duplicate READMEs and stale debug docs.
- **Next up:** Priority #1 (debug.log cleanup) was identified but deferred — hardcoded `FileWriter`/`open()` calls to `.cursor/debug.log` exist in both Java (`OrderServiceImpl`, `TelemetryRepository`) and Python (`main.py` middleware, `forecasting_routes.py`). These will crash on non-Windows machines and in Lambda. ~15 min fix.
- **After that:** Priority #3 — Live delivery map with Leaflet.js in the dashboard.

## Key Decisions Made
- **ML model:** Used NYC Taxi Trip Duration (Kaggle) rather than synthetic data. Priority is a synthetic column (20% Express with 15-20% speed boost). This is defensible in interviews.
- **Model choice:** RandomForest over Ridge — better at capturing non-linear hour/distance interactions. R² of 0.45 is honest for urban speed prediction with limited features.
- **Speed not duration:** Model predicts speed (km/h), not trip duration. ETA = distance / predicted_speed. This decouples the ML from the Haversine calculation cleanly.
- **Time features from server:** hour_of_day, day_of_week, month come from `datetime.now()` at prediction time, not from the request. Java service doesn't need to send these.
- **Kaggle raw data gitignored:** `data/raw/` is in .gitignore (190MB). Processed `data/training_data.csv` (20k rows, ~600KB) and `models/speed_model.joblib` (~7MB) are committed so the model works on fresh checkout.

## Files Recently Modified (This Session)
- `.cursor/rules/000-global.mdc` — fixed port, added SESSION.md rule, function docs rule, cleanup rule
- `.cursor/rules/100-java-spring.mdc` — fixed package names (entity not model), added missing packages
- `.cursor/rules/200-python-fastapi.mdc` — fixed port 5000→5050
- `.cursor/rules/300-aws-infrastructure.mdc` — fixed Bedrock model ID, now tracked in git
- `.gitignore` — added `**/data/raw/`
- `progress.md` — corrected false checkmarks, updated ML status
- `services/ai-forecasting-python/scripts/prepare_training_data.py` — NEW: data pipeline
- `services/ai-forecasting-python/scripts/train_model.py` — NEW: training script (replaced train_mock_model.py)
- `services/ai-forecasting-python/data/training_data.csv` — NEW: 20k processed rows
- `services/ai-forecasting-python/models/speed_model.joblib` — UPDATED: real trained model
- `services/ai-forecasting-python/app/engine/model_loader.py` — REWRITTEN: 5-feature predict_speed
- `services/ai-forecasting-python/app/services/forecasting_service.py` — UPDATED: passes time features
- `services/ai-forecasting-python/tests/unit/test_ml_engine.py` — REWRITTEN: 7 multi-feature tests
- `services/ai-forecasting-python/README.md` — updated ML section, fixed port references
- DELETED: 3 duplicate READMEs, 2 stale debug docs, train_mock_model.py

## How to Resume
Tell the AI: "Read `SESSION.md`, `progress.md`, and `spec.md` to get context. Continue from where we left off."
