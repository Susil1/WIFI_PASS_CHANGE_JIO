# router/

Router JSON-RPC client and helpers.

## What this folder does

- Reads router IP from `config.ini` (via `router/file_handler.py`).
- Logs into the router using JSON-RPC over HTTPS (`/WCGI`).
- Maintains auth (cookie `sysauth` + bearer token) and exposes helper methods to call router APIs.
- Supports Wi‑Fi password change and packet capture download.

## Main files

- `connection.py`
  - Class `routerConnection`
  - `initialise_connection()` → calls `login` then `postLogin`
  - `getInfo(method, params)` → generic JSON-RPC call wrapper
  - `changePassword(newpass)` → uses `getWirelessConfiguration` then `setWirelessConfiguration`
  - `capture_packet(interface, size, file_name="capture.pcap")` → start/stop capture + download
  - `logout()`
- `file_handler.py`
  - Reads `config.ini`
  - Reads/writes `credentials.json`
  - Writes the latest Wi‑Fi password to `newpass.txt`
  - Saves downloaded packet capture to disk

## Inputs / outputs

- Inputs:
  - `config.ini` → `[IP] ip = ...`
  - `credentials.json` → `{ "username": "...", "password": "..." }`
- Outputs:
  - `newpass.txt` (written when password is changed)
  - `capture.pcap` (or whatever file name you pass)

## Notes

- The client disables TLS verification because many routers use self-signed certs. Use only on networks you own / are authorised to test.
