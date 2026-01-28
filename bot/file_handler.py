from configparser import ConfigParser

from utils.paths import CONFIG_FILE

def getToken()->str:
    config = ConfigParser()
    config.read(CONFIG_FILE)
    TOKEN = config["CRED"]["TOKEN"]
    return TOKEN