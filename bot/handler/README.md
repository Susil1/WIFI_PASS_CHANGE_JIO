# bot/handler/

Command handlers (aiogram routers) for router-related Telegram commands.

## What’s inside

- `commands.py`
  - Defines `command_route` router.
  - Registers handlers for:
    - `/change_pass <NEW_PASSWORD>`
    - `/get_lan_clients` (+ inline callbacks: `more`, `less`, `rescan`)
    - `/get_memory_usage`
    - `/get_wireless_config`
    - `/get_system_status`
  - Uses `asyncio.to_thread(...)` to run blocking router calls without freezing the event loop.

## How it’s protected

This router is wrapped with `AuthMiddleware` (see `bot/middleware/auth.py`) so only authorised users can execute these commands.
