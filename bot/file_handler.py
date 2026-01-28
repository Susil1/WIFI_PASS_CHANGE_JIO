from configparser import ConfigParser
import os

from utils.paths import CONFIG_FILE

def getToken()->str:
    config = ConfigParser()
    config.read(CONFIG_FILE)
    try:
        return config["CRED"]["TOKEN"]
    except Exception as e:
        raise RuntimeError(
            "Telegram bot token not found. Set TELEGRAM_BOT_TOKEN or add [CRED] TOKEN to config.ini"
        ) from e