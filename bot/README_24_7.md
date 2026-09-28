# Telegram Bot — 24/7 deployment

## 1. Token
Create a NEW token with @BotFather. The old token that was previously in `bot.py` should be revoked.

Set this environment variable on the hosting service:

BOT_TOKEN=YOUR_NEW_TOKEN

Do not commit the real token to GitHub.

## 2. Local test
Windows:
    set BOT_TOKEN=YOUR_NEW_TOKEN
    pip install -r requirements.txt
    python bot.py

Or create a local `.env` file from `.env.example`:
    BOT_TOKEN=YOUR_NEW_TOKEN

Then:
    pip install -r requirements.txt
    python bot.py

## 3. Railway
- Create a new project and deploy this folder/repository.
- Build command: `pip install -r requirements.txt`
- Start command: `python bot.py`
- Add `BOT_TOKEN` under Variables.
- Use a Worker/service process, not a static web service.

## 4. Render
- Create a Background Worker.
- Build command: `pip install -r requirements.txt`
- Start command: `python bot.py`
- Add `BOT_TOKEN` as an environment variable.
- `render.yaml` is included as a reference configuration.

## Important
The bot uses Telegram long polling, so it must run as a persistent worker process.
