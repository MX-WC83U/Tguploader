import os
import logging
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# create bot client
bot = Client(
    "my_bot",
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
    bot_token=os.environ.get("BOT_TOKEN")
)

# helper function to send a message
def send_message(chat_id: int, text: str):
    bot.send_message(chat_id=chat_id, text=text)

# helper function to send a file
def send_file(chat_id: int, file_path: str):
    try:
        # use chunked upload for larger files
        if os.path.getsize(file_path) > 1024 * 1024 * 1024:
            with open(file_path, 'rb') as f:
                file_id = ""
                while True:
                    chunk = f.read(1024 * 1024 * 1024)
                    if not chunk:
                        break
                    url = f"https://api.telegram.org/bot{bot.token}/sendDocument"
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    data = {'chat_id': chat_id, 'document': ('file', chunk)}
                    response = requests.post(url, headers=headers, data=data)
                    file_id = response.json()["result"]["document"]["file_id"]
            send_message(chat_id, f"File uploaded: {os.path.basename(file_path)}")
            return file_id
        else:
            # send smaller files using the send_document method
            bot.send_document(chat_id=chat_id, document=file_path)
            send_message(chat_id, f"File uploaded: {os.path.basename(file_path)}")
    except Exception as e:
        send_message(chat_id, f"Error uploading file: {e}")

# /download command handler
@bot.on_message(filters.command("download"))
def download_handler(client: Client, message: Message):
    try:
        # download the file from the URL provided
        url = message.text.split(" ", 1)[1]
        response = requests.get(url)
        file_name = os.path.basename(url)
        with open(file_name, "wb") as f:
            f.write(response.content)
        # send the file to the user
        send_file(message.chat.id, file_name)
        # delete the local file
        os.remove(file_name)
    except Exception as e:
        send_message(message.chat.id, f"Error downloading file: {e}")

# start the bot client
bot.run()
