import os

TG_KEY = os.environ["TELEGRAM_API_KEY"]
IAM_TOKEN = os.environ["SA_STORAGE_IAM_TOKEN"]
FOLDER_ID = os.environ["FOLDER_ID"]
GPT_INSTRUCTION_TEXT = os.environ["GPT_INSTRUCTION_TEXT"]
BUCKET_NAME = os.environ["BUCKET_NAME"]


YANDEXGPT_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
YANDEXOCR_URL = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TG_KEY}"
TELEGRAM_FILE_URL = f"https://api.telegram.org/file/bot{TG_KEY}"