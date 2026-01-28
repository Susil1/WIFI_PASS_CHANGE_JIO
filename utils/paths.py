from pathlib import Path
# PATHS
BASE_PATH = Path(__file__).parent.parent
CREDENTIAL_PATH = BASE_PATH/"credentials.json"
CONFIG_FILE = BASE_PATH/"config.ini"
DB_CONFIG_FILE = BASE_PATH/"db.ini"
LOGGER_PATH = BASE_PATH/"logs.log"
BOT_LOGGER_PATH = BASE_PATH/"bot.log"
MAIN_LOGGER_PATH = BASE_PATH/"mainlogs.log"