# Python AI Service Port Issue – Summary

## What’s happening now

- **Symptom:** Starting the AI service (via `start-ai-service.ps1` or `uvicorn ... --port 5000` / `--port 5001`) fails with:
  ```text
  ERROR: [WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions
  ```
- **Ports tried:** 5000 and 5001 both hit 10013. **Cause:** Windows excluded port range **4936–5035** includes both (see `netsh interface ipv4 show excludedportrange protocol=tcp`). Default is now **5050** (outside that range).
- **Effect:** The AI Forecasting Service does not start, so the Order service cannot get forecasts and the dashboard shows no Distance/ETA.

---

## Why it can seem to start “out of nowhere”

It worked yesterday and fails today even though you didn’t change the app. That’s common on Windows for a few reasons:

1. **Windows reserved / excluded port ranges**
   - Windows (and some features like Hyper-V, WSL, Windows NAT) **reserve ranges of ports** so normal apps can’t bind to them.
   - These ranges are **dynamic**: they can be created or changed when:
     - You reboot.
     - A service (e.g. Docker, WSL, Hyper-V, VPN) starts or updates.
     - Windows Update or a driver change runs.
   - So **5000 or 5001 might have been free yesterday** and **inside a reserved range today** (or the other way around another day).

2. **Another process took the port**
   - Something else (another app, a previous Python process, another tool) may have bound to 5000 or 5001. If that process didn’t release the port cleanly, or a new one started at boot, you can get “address in use” (10048) or sometimes 10013 depending on how the port is held.

3. **Security / firewall / antivirus**
   - Less common, but security software can start blocking or “owning” certain ports after an update or a policy change, which can show up as 10013.

So: **the app didn’t change; the environment (reserved ports or who’s using 5000/5001) did.** That’s why it feels like it broke “out of nowhere.”

---

## What to do

1. **See if Windows reserved 5000/5001**
   ```powershell
   netsh interface ipv4 show excludedportrange protocol=tcp
   ```
   If 5000 or 5001 (or a range that includes them) appears, that’s why you get 10013.

2. **See what is using the port**
   ```powershell
   netstat -ano | findstr ":5000 :5001"
   ```
   If something is LISTENING, you can stop that process or use a different port.

3. **Use a port that’s not reserved and not in use**
   - Ports **5000–5035** are in the Windows excluded range on your machine; use **5050** (now the default) or e.g. **8000**, **8765**.
   - Start the AI service (script now defaults to 5050):
     ```powershell
     .\start-ai-service.ps1
     ```
   - Order service is configured with `ai.forecasting.base-url=http://localhost:5050`. Restart the Order service after any change.

4. **Optional: reduce future surprises**
   - If you use Hyper-V/WSL/Docker, sometimes stopping or disabling them (or rebooting) can free or shift reserved ranges, but that’s not always possible. Using a higher, less common port (e.g. 5050 or 8000) often avoids reserved ranges.

---

## One-line summary

**You’re hitting WinError 10013 because Windows or another process is now blocking or reserving port 5000/5001; the Python app didn’t change. Use `netsh` and `netstat` to confirm, then run the AI service on a different port (e.g. 5050) and set `ai.forecasting.base-url` to match.**
