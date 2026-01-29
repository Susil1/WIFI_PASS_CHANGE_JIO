# bot/middleware/

Middlewares for the Telegram bot.

## AuthMiddleware

- File: `auth.py`
- Purpose: blocks unauthorised users from executing protected commands and callbacks.
- Source of truth: `DB.isAuthorised(user_id)` from the MongoDB layer.

## Behaviour

- If user is authorised → proceeds to handler.
- If not authorised → sends an access denied message showing how to use `/authorise <CODE>`.
