# Pro Access BD - Lovable Extension License Generator Bot

A 24/7 Telegram License Generator Bot for the Lovable Pro extension.

## Features
- Generates keys in format: `LOVABLE-PRO-DURATION-XXXX-XXXX`
- Supported Types: `LIFETIME`, `1YEAR`, `1MONTH`, custom `7DAYS`
- Telegram Bot (@lovableprolicensekey_bot) integration with interactive buttons
- Zero external dependencies (uses standard library `urllib` + `json`)

## Deployment to Render.com
1. Create a **Background Worker** on Render.com
2. Set Start Command: `python3 telegram_bot.py`
3. Add Environment Variable: `BOT_TOKEN` = ``
