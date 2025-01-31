terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
    telegram = {
      source = "yi-jiayu/telegram"
    }
  }
}

provider "telegram" {
  bot_token = var.TELEGRAM_API_KEY
}

provider "yandex" {
  cloud_id                 = var.CLOUD_ID
  folder_id                = var.FOLDER_ID
  service_account_key_file = "../key1.json"
}

resource "archive_file" "zipped_project" {
  type        = "zip"
  output_path = "func.zip"
  source_dir  = "./src"
}

resource "yandex_storage_bucket" "images-bucket-34" {
  bucket = "images-bucket-34"
}

resource "yandex_storage_object" "gpt_instruction" {
  bucket = yandex_storage_bucket.images-bucket-34.id
  key    = "instruction.txt"
  source = "./instruction.txt"
}

resource "yandex_function" "bot_function" {
  name               = "bot-function-34"
  user_hash          = archive_file.zipped_project.output_sha256
  runtime            = "python312"
  entrypoint         = "index.handler"
  service_account_id = var.SERVICE_ACCOUNT_ID_FOR_FUNCTION
  memory             = 128
  execution_timeout  = "50"
  content {
    zip_filename = archive_file.zipped_project.output_path
  }
  environment = {
    "KEYID"                = var.KEYID,
    "SA_STORAGE_IAM_TOKEN" = var.SA_STORAGE_IAM_TOKEN
    "TELEGRAM_API_KEY"     = var.TELEGRAM_API_KEY
    "GPT_INSTRUCTION_TEXT" = yandex_storage_object.gpt_instruction.key
    "FOLDER_ID" = var.FOLDER_ID
    "BUCKET_NAME" = "instructions"
  }
  mounts {
    name = "instructions"
    mode = "ro"
    object_storage {
      bucket = yandex_storage_bucket.images-bucket-34.id
    }
  }
}

resource "yandex_function_iam_binding" "function_iam" {
  function_id = yandex_function.bot_function.id
  role        = "serverless.functions.invoker"
  members     = ["system:allUsers"]
}

resource "telegram_bot_webhook" "set_webhook" {
  url = "https://api.telegram.org/bot${var.TELEGRAM_API_KEY}/setWebhook?url=https://functions.yandexcloud.net/${yandex_function.bot_function.id}"
}

variable "KEYID" {
  type = string
}

variable "FOLDER_ID" {
  type = string
}

variable "SA_STORAGE_IAM_TOKEN" {
  type = string
}

variable "TELEGRAM_API_KEY" {
  type = string
}

variable "CLOUD_ID" {
  type = string
}

variable "SERVICE_ACCOUNT_ID_FOR_FUNCTION" {
  type = string
}

output "function_url" {
  value = "https://functions.yandexcloud.net/${yandex_function.bot_function.id}"
}

output "webhook_url" {
  description = "The Telegram webhook URL configured for the bot."
  value       = telegram_bot_webhook.set_webhook.url
}