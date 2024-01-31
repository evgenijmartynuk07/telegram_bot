import os
from dotenv import load_dotenv

load_dotenv()

telegram_token = os.environ.get("TELEGRAM_TOKEN")
openai_key = os.environ.get("OPENAI_KEY")
