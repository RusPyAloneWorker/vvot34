from constants import IAM_TOKEN, FOLDER_ID, GPT_INSTRUCTION_TEXT, YANDEXGPT_URL, BUCKET_NAME, YANDEXOCR_URL
import requests
import base64

def get_instruction(instruction_key):
    with open(f"/function/storage/{BUCKET_NAME}/{instruction_key}", "r") as file:
        file_content = file.read()
    return file_content

def gpt(text):
        headers = {
            "Content-Type": "application/json",
            "x-folder-id": FOLDER_ID,
            "Authorization": f"Api-Key {IAM_TOKEN}",
        }
        data = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
            "messages": [
                {
                    "role": "system",
                    "text": get_instruction(GPT_INSTRUCTION_TEXT)
                },
                {
                    "role": "user",
                    "text": text
                },
            ],
        }
        try:
            response = requests.post(YANDEXGPT_URL, headers=headers, json=data)
            response.raise_for_status()  
            alternatives = response.json().get("result", {}).get("alternatives", [])

            result = "Я не смог подготовить ответ на экзаменационный вопрос."
            for alt in alternatives:
                if alt.get("status") == "ALTERNATIVE_STATUS_FINAL":
                    result = alt["message"].get("text")
                    break
            return result
        
        except Exception as e:
            print(f"Yandex GPT API errir: {e}")
            return "Я не смог подготовить ответ на экзаменационный вопрос."
        

def get_text_from_image(image):
        try:
            print("in gpt.get_text_from_image")
            base64_image = base64.b64encode(image).decode("utf-8")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Api-Key {IAM_TOKEN}",
            }
            body = {
                "content": base64_image,
                "mimeType": "image/jpeg",
                "languageCodes": ["ru", "en"],
            }

            response = requests.post(YANDEXOCR_URL, headers=headers, json=body)
            return (response.json().get("result", {}).get("textAnnotation", {}).get("fullText"), None)
        except Exception as e:
            print(f"OCR recognition failed: {e}")
            return (None, "Я не могу обработать эту фотографию.")