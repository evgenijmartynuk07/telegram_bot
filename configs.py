from os import getenv


BOT_TOKEN = getenv(
    'BOT_TOKEN',
    default=''
)
OPENAI_KEY = getenv(
    'OPENAI_KEY',
    default=''
)
