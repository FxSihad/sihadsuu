import configparser
import logging
from pyrogram import Client
import asyncio


# SETUP LOGGING
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler("Multi.log"), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s",
)
LOGGER = logging.getLogger(__name__)

# LOAD CONFIG
config = configparser.ConfigParser()
config.read("config.ini")


# BOT CLIENT
bot = Client(
    "BotClient",
    api_id=config["pyrogram"]["api_id"],
    api_hash=config["pyrogram"]["api_hash"],
    bot_token=config["pyrogram"]["bot_token"],
    plugins=dict(root="src"),
    max_concurrent_transmissions=10,
    workers=100,
    sleep_threshold=60,
)


bot.run()
