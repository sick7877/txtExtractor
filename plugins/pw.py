import urllib.parse
import requests
import json
import subprocess
import os
import sys
import re
import time
import logging

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, User
from pyrogram.errors import FloodWait
from pyromod import listen
import helper
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from p_bar import progress_bar
from subprocess import getstatusoutput

@Client.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text(
        "Send Auth code in this manner otherwise bot will not respond.\n\nSend like this:-  AUTH CODE"
    )
    input1: Message = await bot.listen(editable.chat.id)
    raw_text1 = input1.text.strip()

    headers = {
        'Host': 'api.penpencil.xyz',
        'authorization': f"Bearer {raw_text1}",
        'client-id': '5eb393ee95fab7468a79d189',
        'client-version': '12.84',
        'user-agent': 'Android',
        'randomid': 'e4307177362e86f1',
        'client-type': 'MOBILE',
        'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}',
        'content-type': 'application/json; charset=UTF-8',
    }

    params = {
        'mode': '1',
        'filter': 'false',
        'exam': '',
        'amount': '',
        'organisationId': '5eb393ee95fab7468a79d189',
        'classes': '',
        'limit': '20',
        'page': '1',
        'programId': '',
        'ut': '1652675230446',
    }

    await editable.edit("**You have these Batches :-\n\nBatch ID : Batch Name**")
    try:
        response = requests.get(
            'https://api.penpencil.xyz/v3/batches/my-batches', params=params, headers=headers
        ).json()["data"]
        for data in response:
            batch_name = data["name"]
            batch_id = data["_id"]
            msg = f"`{batch_name}` : `{batch_id}`"
            await m.reply_text(msg)
    except Exception as e:
        await m.reply_text(f"Failed to fetch batches: {e}")
        return

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input3 = await bot.listen(editable.chat.id)
    raw_text3 = input3.text.strip()

    try:
        subjects = requests.get(
            f'https://api.penpencil.xyz/v3/batches/{raw_text3}/details', headers=headers
        ).json()["data"]["subjects"]
    except Exception as e:
        await m.reply_text(f"Failed to fetch batch details: {e}")
        return

    await editable1.edit("Subject IDs:")
    subject_ids = ""
    for subject in subjects:
        sid = subject['_id']
        await m.reply_text(sid)
        subject_ids += sid + "&"

    editable2 = await m.reply_text(f"**Enter this to download full batch :-**\n```{subject_ids}```")
    input4 = await bot.listen(editable.chat.id)
    raw_text4 = input4.text.strip()

    await m.reply_text("**Enter resolution**")
    input5: Message = await bot.listen(editable.chat.id)
    resolution = input5.text.strip()

    editable4 = await m.reply_text(
        "Now send the **Thumb url** Eg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**"
    )
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text.strip()

    if raw_text6.startswith("http://") or raw_text6.startswith("https://"):
        getstatusoutput(f"wget '{raw_text6}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = None

    try:
        subject_id_list = raw_text4.strip("&").split("&")
        file_name = f"{raw_text3}_batch_links.txt"
        for sid in subject_id_list:
            if not sid:
                continue
            all_data = []
            for page in range(1, 5):
                content_params = {
                    'page': str(page),
                    'tag': '',
                    'contentType': 'exercises-notes-videos',
                    'ut': ''
                }
                content_url = f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{sid}/contents'
                response = requests.get(content_url, params=content_params, headers=headers)
                try:
                    content_data = response.json().get("data", [])
                    all_data.extend(content_data)
                except Exception as e:
                    await m.reply_text(
                        f"Error fetching subject `{sid}` page {page}: {str(e)}\nRaw response: {response.text}"
                    )
                    continue

            for content in all_data:
                title = content.get("topic")
                url = (
                    content.get("url", "")
                    .replace("d1d34p8vz63oiq", "d3nzo6itypaz07")
                    .replace("mpd", "m3u8")
                    .strip()
                )
                if title and url:
                    with open(file_name, "a", encoding="utf-8") as f:
                        f.write(f"{title}:{url}\n")

        await m.reply_document(file_name)
    except Exception as e:
        await m.reply_text(f"Unexpected error: {e}")
