import os
from dotenv import load_dotenv
load_dotenv()

DOCKERHUB_USERNAME=os.getenv('DOCKERHUB_USERNAME')
DOCKERHUB_PASSWORD=os.getenv('DOCKERHUB_PASSWORD')
DOCKERHUB_BASE_URL="https://hub.docker.com"

DISCORD_WEBHOOKURL = 'https://discordapp.com/api/webhooks/7XXXXXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXX'
SLACK_WEBHOOKURL = 'https://hooks.slack.com/services/TXXXXXXXX/BXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXX'
TELEGRAM_CONFIG = {
    "token": os.getenv('TELEGRAM_CONFIG_TOKEN'),
    "chat_id": os.getenv('TELEGRAM_CONFIG_CHAT_ID')
}
