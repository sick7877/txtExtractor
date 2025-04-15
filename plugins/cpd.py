# MIT License
# Copyright (c) 2019-present Dan <https://github.com/delivrance>

import os
import re
import sys
import time
import json
import logging
import requests
import subprocess
from base64 import b64decode
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
from pyromod import listen
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

import helper
from p_bar import progress_bar

@Client.on_message(filters.command(["cpd"]) & ~filters.edited)
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("Send txt file**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read().split("\n")
        links = [i.split(":", 1) for i in content]
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return

    editable = await m.reply_text(f"Total links found: **{len(links)}**\n\nSend start index (default is **0**):")
    input1: Message = await bot.listen(editable.chat.id)
    try:
        start_index = int(input1.text)
    except:
        start_index = 0

    editable = await m.reply_text("**Enter Title**")
    input_title: Message = await bot.listen(editable.chat.id)
    title = input_title.text

    await m.reply_text("**Enter resolution**")
    input_res: Message = await bot.listen(editable.chat.id)
    resolution = input_res.text

    editable = await m.reply_text("Now send the **Thumb URL** or type **no**")
    input_thumb: Message = await bot.listen(editable.chat.id)
    thumb = input_thumb.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    count = start_index + 1

    try:
        for i in range(start_index, len(links)):
            name_part = links[i][0].translate(str.maketrans('', '', '\t:/+|@#*.')).strip()
            url = links[i][1]
            name = f"{str(count).zfill(3)}) {name_part}"

            if "classplus" in url:
                headers = {
                    'Host': 'api.classplusapp.com',
                    'x-access-token': f'{token}',
                    'user-agent': 'Mobile-Android',
                    'app-version': '1.4.37.1',
                    'api-version': '18',
                    'device-id': '5d0d17ac8b3c9f51',
                    'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30',
                    'accept-encoding': 'gzip',
                }
                params = (('url', url),)
                res = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url1 = res.json().get("url", "")
                res1 = requests.get(url1, headers={'User-Agent': 'ExoPlayerDemo/1.4.37.1'})
                url1 = res1.text.split("\n")[2]
            else:
                url1 = url

            prog = await m.reply_text(f"**Downloading:**\n\n**Name:** `{name}`\n**URL:** `{url1}`")
            caption = f'**Title »** {name_part}.mkv\n**Caption »** {title}\n**Index »** {str(count).zfill(3)}'

            if "pdf" in url:
                cmd = f'yt-dlp -o "{name}.pdf" "{url1}"'
            else:
                cmd = f'yt-dlp -o "{name}.mp4" --no-keep-video --no-check-certificate --remux-video mkv "{url1}"'

            try:
                download_cmd = f"{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args 'aria2c: -x 16 -j 32'"
                os.system(download_cmd)

                if os.path.isfile(f"{name}.mkv"):
                    filename = f"{name}.mkv"
                elif os.path.isfile(f"{name}.mp4"):
                    filename = f"{name}.mp4"
                elif os.path.isfile(f"{name}.pdf"):
                    filename = f"{name}.pdf"
                else:
                    raise Exception("Download failed.")

                subprocess.run(f'ffmpeg -i "{filename}" -ss 00:01:00 -vframes 1 "{filename}.jpg"', shell=True)
                await prog.delete(True)
                reply = await m.reply_text(f"Uploading - ```{name}```")

                thumbnail = thumb if thumb != "no" else f"{filename}.jpg"
                duration = int(helper.duration(filename))
                start_time = time.time()

                if "pdf" in url1:
                    await m.reply_document(filename, caption=caption)
                else:
                    await m.reply_video(
                        filename,
                        supports_streaming=True,
                        height=720,
                        width=1280,
                        caption=caption,
                        duration=duration,
                        thumb=thumbnail,
                        progress=progress_bar,
                        progress_args=(reply, start_time),
                    )

                count += 1
                os.remove(filename)
                os.remove(f"{filename}.jpg")
                await reply.delete(True)
                time.sleep(1)

            except Exception as e:
                await m.reply_text(f"**Download failed ❌**\n{str(e)}\n**Name:** {name}\n**Link:** `{url}` & `{url1}`")
                continue

    except Exception as e:
        await m.reply_text(str(e))

    await m.reply_text("Done.")
