import json
import logging
import os
import requests
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from logging.handlers import RotatingFileHandler

# Setup logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5000000, backupCount=10),
        logging.StreamHandler(),
    ],
)

# Create bot client
bot = Client(
    "CW",
    bot_token="8190086252:AAHkseLMEdl_Hxaoz38C9vQaGujXqIpHVoY",
    api_id=28712726,
    api_hash="06acfd441f9c3402ccdb1945e8e2a93b"
)

@bot.on_message(filters.command(["down"]) & ~filters.edited)
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text(
        "Send **ID & Password** like this: **ID*Password**"
    )
    
    input1: Message = await bot.listen(editable.chat.id)
    raw_text = input1.text
    await input1.delete(True)

    try:
        mobile, password = raw_text.split("*")
    except Exception:
        await editable.edit("Invalid format. Use: `ID*Password`")
        return

    info = {
        "api_key": "kdc123",
        "mobilenumber": mobile,
        "password": password
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Host': 'ignitedminds.live',
        'Connection': 'Keep-Alive',
        'User-Agent': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
    }

    try:
        response = requests.post(
            'https://ignitedminds.live/android/User/login_user',
            headers=headers,
            data=json.dumps(info)
        )
        data = response.json()
        userid = data["id"]
        token = data["connection_key"]
        await editable.edit("**Login Successful!**")
    except ValueError:
        await editable.edit("**Login failed: Invalid JSON response.**")
        LOGGER.error("Invalid JSON: " + response.text)
    except KeyError:
        await editable.edit("**Login failed: Missing fields in response.**")
    except Exception as e:
        await editable.edit(f"**Login failed: {e}**")

async def main():
    await bot.start()
    bot_info = await bot.get_me()
    LOGGER.info(f"<--- @{bot_info.username} Started --->")
    await idle()

asyncio.get_event_loop().run_until_complete(main())
LOGGER.info("<--- Bot Stopped --->")
