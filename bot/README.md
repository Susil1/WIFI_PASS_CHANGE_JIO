# bot/

Telegram bot (aiogram) that controls the router via `router/` with MongoDB-backed authorisation.

## What this folder does

- Starts an aiogram v3 bot with polling.
- Enforces authorisation for router commands using middleware.
- Provides Telegram commands that call the router JSON-RPC client.
- Periodically reconnects to the router session.

## Main files

- `app.py`
  - Bot setup (Dispatcher + routers)
  - `/start`, `/help`
  - `/authorise <CODE>` → redeems a one-time code from MongoDB
  - `/get_user_profile` → shows current user profile
  - `/delete_profile` → deletes user data (with inline confirmation)
  - Creates a background task to periodically reconnect to the router
- `handler/commands.py`
  - Router-related command handlers:
    - `/change_pass <NEW_PASSWORD>`
    - `/get_lan_clients` (supports inline "show more/less" + rescan)
    - `/get_memory_usage`
    - `/get_wireless_config`
    - `/get_system_status`
- `middleware/auth.py`
  - `AuthMiddleware` checks authorisation via `DB.isAuthorised(user_id)`
- `messages.py`
  - Message templates + helper renderers for responses and inline keyboards
- `file_handler.py`
  - Reads bot token from `config.ini` (`[CRED] TOKEN`)
- `utility.py`
  - Global singletons:
    - `CONNECTION` (routerConnection)
    - `DB` (DB_Connection)
    - `BOT_LOGGER`
  - `periodic_task()` + `reconnect()` helper

## Configuration

- `config.ini`
  - `[IP] ip = ...` (router IP)
  - `[CRED] TOKEN = ...` (Telegram bot token)
- `db.ini` must be configured to let `db/` connect to MongoDB.

## Run

From repo root:

```bash
python telegram_bot.py
```
