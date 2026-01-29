# utils/

Shared utilities used by both the router automation script and the Telegram bot.

## Main files

- `paths.py`
  - Central paths (repo root, config paths, log paths)
- `constants.py`
  - Builds router URL from `config.ini` (`https://<ip>/WCGI`)
  - Date format and anti-spam constants
- `utility.py`
  - Password generator `getNewPassword()` (uses `secrets`)
  - Dataclasses:
    - `Payload` (JSON-RPC request builder)
    - `Response` (normalized JSON-RPC response)
    - `UserData`, `UserInfo`, `Command`
  - Logging:
    - `LogConsole` writes to file and optionally prints to console
- `colors.py`
  - ANSI color constants for console output

## Notes

- The router IP is read via `router/file_handler.py` → `config.ini`.
- Logging outputs default to `logs.log`, `mainlogs.log`, and `bot.log` at the repo root.
