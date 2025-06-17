# Sports Betting Predictions Bot

Telegram bot that provides accurate sports betting predictions based on live odds analysis from multiple bookmakers.

## Features

- Live odds analysis from 20+ bookmakers
- Betting predictions with confidence ratings
- FIFA Club World Cup, MLB, NBA, NFL, NHL coverage
- Simple commands: /predictions, /odds, /today
- Real-time odds comparison and value detection

## Heroku Deployment

### Quick Deploy (One-Click)

Click this button to deploy your bot to Heroku instantly:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/jeat14/sports-betting-bot)

### Manual Deployment

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-bot-name
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=7816965212:AAHFQfvvbjFtmRajS2wFLTiJZeKOfEzo7C0
   heroku config:set ODDS_API_KEY=b042ef3e00a923abda5dade83334ec20
   ```

5. **Deploy from Git**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   heroku git:remote -a your-bot-name
   git push heroku main
   ```

6. **Scale Worker Process**
   ```bash
   heroku ps:scale worker=1
   ```

## Local Development

1. **Install Dependencies**
   ```bash
   pip install -r heroku_requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   export TELEGRAM_BOT_TOKEN=7816965212:AAHFQfvvbjFtmRajS2wFLTiJZeKOfEzo7C0
   export ODDS_API_KEY=b042ef3e00a923abda5dade83334ec20
   ```

3. **Run Bot**
   ```bash
   python main.py
   ```

## Bot Commands

- `/start` - Welcome message with sport buttons
- `/predictions` - FIFA World Cup predictions
- `/odds` - Current FIFA World Cup odds
- `/today` - All games happening today
- `/sports` - List all available sports

## Architecture

- `main.py` - Bot initialization and command routing
- `bot_handlers.py` - Telegram command handlers
- `odds_service.py` - Live odds API integration
- `prediction_engine.py` - Betting analysis algorithms
- `utils.py` - Message formatting utilities
- `config.py` - Configuration and sports definitions

## API Keys

- **Telegram Bot Token**: Get from @BotFather on Telegram
- **Odds API Key**: Register at the-odds-api.com

## Heroku Configuration

- **Worker Process**: Runs continuously (not web server)
- **Eco Dyno**: Sufficient for personal use
- **Python 3.11**: Specified in runtime.txt
- **Auto Dependencies**: Listed in heroku_requirements.txt