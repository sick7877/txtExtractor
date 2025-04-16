import urllib import urllib.parse import requests import json import subprocess from pyrogram.types.messages_and_media import message import helper from pyromod import listen from pyrogram.types import Message import tgcrypto import pyrogram from pyrogram import Client, filters from pyrogram.types.messages_and_media import message from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup from pyrogram.errors import FloodWait import time from pyrogram.types import User, Message from p_bar import progress_bar from subprocess import getstatusoutput import logging import os import sys import re from pyrogram import Client as bot import cloudscraper from Crypto.Cipher import AES from Crypto.Util.Padding import unpad from base64 import b64encode, b64decode

@bot.on_message(filters.command(["pw"])) async def account_login(bot: Client, m: Message): editable = await m.reply_text( "Send Auth code in this manner otherwise bot will not respond.\n\nSend like this:-  AUTH CODE" ) input1: Message = await bot.listen(editable.chat.id) raw_text1 = input1.text headers = { 'Host': 'api.penpencil.xyz', 'authorization': f"Bearer {raw_text1}", 'client-id': '5eb393ee95fab7468a79d189', 'client-version': '12.84', 'user-agent': 'Android', 'randomid': 'e4307177362e86f1', 'client-type': 'MOBILE', 'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}', 'content-type': 'application/json; charset=UTF-8', }

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
    response = requests.get('https://api.penpencil.xyz/v3/batches/my-batches', params=params, headers=headers).json()["data"]
    for data in response:
        batch = data["name"]
        aa = f"```{data['name']}```  :  ```{data['_id']}\n```"
        await m.reply_text(aa)
except Exception as e:
    await m.reply_text(f"Failed to fetch batches: {e}")
    return

editable1 = await m.reply_text("**Now send the Batch ID to Download**")
input3 = await bot.listen(editable.chat.id)
raw_text3 = input3.text

try:
    response2 = requests.get(f'https://api.penpencil.xyz/v3/batches/{raw_text3}/details', headers=headers).json()["data"]["subjects"]
except Exception as e:
    await m.reply_text(f"Failed to fetch batch details: {e}")
    return

await editable1.edit("subject : subjectId")
vj = ""
for data in response2:
    bb = f"{data['_id']}&"
    await m.reply_text(bb)
    vj += bb

editable2 = await m.reply_text(f"**Enter this to download full batch :-**\n```{vj}```")
input4 = await bot.listen(editable.chat.id)
raw_text4 = input4.text

await m.reply_text("**Enter resolution**")
input5: Message = await bot.listen(editable.chat.id)
raw_text5 = input5.text

editable4 = await m.reply_text("Now send the **Thumb url** Eg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**")
input6 = await bot.listen(editable.chat.id)
raw_text6 = input6.text
thumb = raw_text6
if thumb.startswith("http://") or thumb.startswith("https://"):
    getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
    thumb = "thumb.jpg"
else:
    thumb = None

try:
    xv = raw_text4.strip('&').split('&')
    for t in xv:
        if not t:
            continue
        all_data = []
        for i in range(1, 5):
            params_content = {'page': str(i), 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
            url = f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents'
            response = requests.get(url, params=params_content, headers=headers)
            try:
                content_data = response.json()["data"]
                all_data.extend(content_data)
            except Exception as e:
                await m.reply_text(f"Error fetching subject `{t}` page {i}: {str(e)}\nRaw response: {response.text}")
                continue

        for data in all_data:
            class_title = data.get("topic")
            class_url = data.get("url", "").replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8").strip()
            if class_title and class_url:
                with open(f"{batch}.txt", 'a') as f:
                    f.write(f"{class_title}:{class_url}\n")

    await m.reply_document(f"{batch}.txt")
except Exception as e:
    await m.reply_text(f"Unexpected error: {e}")

