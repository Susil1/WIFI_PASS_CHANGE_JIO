# WiFi Pass Change (Router + Telegram Bot)

This repo contains two main pieces:

- A Python JSON-RPC client to log in to a Jio router and automate router actions (Wi‑Fi password changes, status queries, packet capture).
- A Telegram bot (aiogram) that exposes safe router actions via commands, with MongoDB-backed authorization (expiry / command limits).

## What This Project Does

- Logs into the router over HTTPS JSON-RPC and keeps a session alive.
- Reads router IP + credentials from local config files.
- Changes Wi‑Fi password using the router's wireless configuration API.
- Fetches router information (LAN clients, memory usage, wireless config, system status, etc.).
- Captures packets from the router (start/stop + download `.pcap`).
- Runs a Telegram bot that:
  - Requires users to authorise using a one-time code stored in MongoDB.
  - Enforces access rules (admin vs non-admin, expiry date, remaining command count).
  - Provides commands to change Wi‑Fi password and query router status.
  - Logs bot activity and attempts.

## Entry Points

- Router automation script: [main.py](main.py)
- Telegram bot runner: [telegram_bot.py](telegram_bot.py)

## Requirements

- Python 3.10+ recommended
- A router that supports this JSON-RPC interface (this repo targets Jio router endpoints)
- MongoDB (Atlas works) for bot authorization storage

Install Python deps:

```bash
pip install -r requirements.txt
```

## Configuration

### 1) Router IP and Telegram token

Edit [config.ini](config.ini):

```ini
[IP]
ip = 192.168.31.1

[CRED]
TOKEN = YOUR_TELEGRAM_BOT_TOKEN
```

### 2) Router credentials

Create/update [credentials.json](credentials.json):

```json
{
  "username": "admin",
  "password": "YOUR_ROUTER_PASSWORD"
}
```

### 3) MongoDB connection (Telegram bot)

Edit [db.ini](db.ini):

```ini
[mongo]
user = YOUR_DB_USER
password = YOUR_DB_PASSWORD
appname = YOUR_ATLAS_APPNAME
```

## Running

### Run the router automation script

```bash
python main.py
```

Notes:

- Most calls in [main.py](main.py) are examples (many are commented out).
- The Wi‑Fi password change method writes the new password to [newpass.txt](newpass.txt).

### Run the Telegram bot

```bash
python telegram_bot.py
```

## Telegram Bot Commands

The bot exposes these main commands (see [bot/messages.py](bot/messages.py) and [bot/handler/commands.py](bot/handler/commands.py)):

- `/authorise <CODE>`: redeem a one-time code from MongoDB and become authorised
- `/change_pass <NEW_PASSWORD>`: change router Wi‑Fi password
- `/get_lan_clients`: list connected LAN clients (with inline "show more/less")
- `/get_memory_usage`: memory usage bar
- `/get_wireless_config`: SSID/security/max clients
- `/get_system_status`: firmware/hardware/model/SSIDs/etc.
- `/get_user_profile`: view your authorisation status
- `/delete_profile`: delete your bot profile (with confirmation)

## Logs & Output Files

- Bot logs: [bot.log](bot.log)
- Script logs: [logs.log](logs.log), [mainlogs.log](mainlogs.log)
- Packet capture output: [capture.pcap](capture.pcap) (default name)
- Last changed Wi‑Fi password: [newpass.txt](newpass.txt)

## Project Structure

- [router/README.md](router/README.md): router JSON-RPC client (login, queries, password change, packet capture)
- [bot/README.md](bot/README.md): Telegram bot (commands, middleware, reconnect task)
- [db/README.md](db/README.md): MongoDB storage for users/codes/limits
- [utils/README.md](utils/README.md): shared dataclasses, logging, constants, paths
- [ADMIN/README.md](ADMIN/README.md): placeholder Node/HTML admin folder
- [wifi-pass-change-notifier/README.md](wifi-pass-change-notifier/README.md): git submodule folder

## Security Notes

- Do not commit real secrets: router passwords, Telegram bot token, MongoDB password.
- This project disables HTTPS certificate verification for the router (self-signed) and should only be used on networks you own or are authorised to test.

## License

See [LICENSE](LICENSE).
