import base64
import requests
import json
from constants import TG_KEY, IAM_TOKEN, TELEGRAM_API_URL, TELEGRAM_FILE_URL
from gpt import gpt, get_text_from_image

def send_message(chat_id, text):
    """Sends a message to a given Telegram chat."""
    print(f"Sending message to chat {chat_id}: {text}")
    url = f"{TELEGRAM_API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    return requests.post(url, data=data)

def process_image_message(message, chat_id):
    try:
        photo = message.get("photo")
        file_id = photo[-1]["file_id"]
    
        # Загружаю фотографию.
        url = f"{TELEGRAM_API_URL}/getFile"
        response = requests.get(url, params={"file_id": file_id})
        response.raise_for_status()
        file_url = response.json().get("result", {}).get("file_path")
    except Exception as e:
        print(f"Failed to get file path: {e}", {"file_id": file_id})
        raise e

    url = f"{TELEGRAM_FILE_URL}/{file_url}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        image = response.content
    except Exception as e:
        print(f"Failed to download image: {e}", {"file_path": file_url})
        raise e

    text, error = get_text_from_image(image)
    if error:
        raise Exception(str(error))
    elif not text:
        raise Exception("На изображении не удалось распознать текст.")
    return text

def get_message_type(message, chat_id):
    """Определяет тип сообщения"""
    if message.get("photo"):  
        return "photo"
    elif text := message.get("text"):  
        entities = message.get("entities", [])
        for entity in entities:
            print(entity)
            if entity.get("type") == "bot_command":
                command = text[entity["offset"]:entity["offset"] + entity["length"]]
                print(entity)
                return command
        return "text"

    else:
        return "error"


def handle_message(message, chat_id) -> None:
    """Отвечает за ответ сообщению"""
    try:
        type = get_message_type(message, chat_id)

        if type == "error":  
            send_message(chat_id, "Я могу обработать только текстовое сообщение или фотографию.")
            return

        elif type == "text":  
            result = gpt(message["text"])
            send_message(chat_id, result)
            return

        elif type == "photo":
            try:
                image_text = process_image_message(message, chat_id)
                print("after")
                result = gpt(image_text)
                send_message(chat_id, result)
                return
            except Exception as e:
                send_message(chat_id, str(e))
                raise e
        else:
            if type in ["/start", "/help"]:
                send_message(chat_id, 'Я помогу подготовить ответ на экзаменационный вопрос по дисциплине "Операционные системы".\nПришлите мне фотографию с вопросом или наберите его текстом.')
            return
        
    except Exception as e:
        print(f"Processing error: {e}")
        send_message(chat_id, str(e))


def handler(event, context):
    try:
        body = json.loads(event['body'])
        message = body.get("message")
        print(body)

        if not message:
            send_message(chat_id, "Я могу обработать только текстовое сообщение или фотографию.")
        
        if "media_group_id" in message:
            send_message(chat_id, "Я могу обработать только одну фотографию.")

        chat_id = message["chat"]["id"]
        
        handle_message(message, chat_id)

        return {"statusCode": 200, "body": "Message processed."}

    except Exception as e:
        print(e)
        send_message(chat_id, str(e))
        raise e
    finally:
        return {"statusCode": 200, "body": "Message processed."}