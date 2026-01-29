# db/

MongoDB storage layer for the Telegram bot (users, command limits, auth codes, anti-spam).

## What this folder does

- Connects to MongoDB (Atlas-style connection string built from `db.ini`).
- Stores bot users and their roles.
- Stores per-user command usage limits (expiry date and/or remaining commands).
- Stores one-time authorisation codes (redeemed via `/authorise`).
- Tracks failed authorisation attempts to slow brute-force guessing.

## Collections

Created in database `telegram_bot`:

- `users`
  - `user_id` (unique)
  - `username`, `first_name`, `role`, `joined_date`
- `commands`
  - `user_id` (unique)
  - `expiry_date`, `commands_remaining`, `used_commands`, `last_used`
- `codes`
  - `code` (unique)
  - `role`, and optional `expiry_date`, `days`, `time`, `num_of_commands`
- `spams`
  - `user_id` (unique)
  - `failed_attempts`, `last_failed_attempts`

## Main files

- `connection.py`
  - `DB_Connection` wrapper around collections and common queries
  - `isAuthorised(user_id)` enforces:
    - admins always allowed
    - else: allow by expiry date, or decrement `commands_remaining`
- `utility.py`
  - `authorise(key, message, DB)`
    - fetches a code from `codes` and deletes it (one-time use)
    - creates/updates `users` + `commands` for the Telegram user
    - computes expiry based on `days`/`time` when needed
- `file_handler.py`
  - Builds Mongo connection string using `db.ini`

## Configuration

Edit `db.ini` at repo root:

```ini
[mongo]
user = YOUR_DB_USER
password = YOUR_DB_PASSWORD
appname = YOUR_ATLAS_APPNAME
```
