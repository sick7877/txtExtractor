# MIT License
# Copyright (c) 2019-present Dan
# Code edited by Cryptostark and fixed by ChatGPT

import requests
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import getstatusoutput

@Client.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("Send **Auth code** like this:  `AUTH CODE`")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text1 = input1.text

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
        'organisationId': '5eb393ee95fab7468a79d189',
        'limit': '20',
        'page': '1',
    }

    await editable.edit("**You have these Batches:**\n\n**Batch Name : Batch ID**")
    response = requests.get('https://api.penpencil.xyz/v3/batches/my-batches', params=params, headers=headers).json()["data"]
    for data in response:
        msg = f"**{data['name']}** : `{data['_id']}`"
        await m.reply_text(msg)

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input3 = await bot.listen(editable.chat.id)
    raw_text3 = input3.text

    response2 = requests.get(f'https://api.penpencil.xyz/v3/batches/{raw_text3}/details', headers=headers).json()["data"]["subjects"]
    await editable1.edit("**Subject ID List:**")
    
    vj = ""
    for data in response2:
        tids = data['_id']
        idid = f"{tids}&"
        if len(vj) + len(idid) > 4000:
            await m.reply_text(vj)
            vj = ""
        vj += idid
    await m.reply_text(f"**Enter this to download full batch:**\n`{vj}`")

    input4 = await bot.listen(editable.chat.id)
    raw_text4 = input4.text

    await m.reply_text("**Enter resolution**")
    input5 = await bot.listen(editable.chat.id)
    raw_text5 = input5.text

    editable4 = await m.reply_text("Now send the **Thumb URL** or send `no`")
    input6 = await bot.listen(editable.chat.id)
    thumb = input6.text
    if thumb.lower().startswith("http"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = None

    try:
        xv = raw_text4.split('&')
        batch_name = ""
        for y in range(len(xv)):
            t = xv[y]
            for page in range(1, 5):
                params = {
                    'page': str(page),
                    'tag': '',
                    'contentType': 'exercises-notes-videos',
                    'ut': ''
                }
                response_data = requests.get(f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents', params=params, headers=headers).json()["data"]
                for data in response_data:
                    title = data["topic"]
                    url = data["url"].replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8").strip()
                    line = f"{title}: {url}"
                    if not batch_name:
                        batch_name = data.get("batch", "batch_data")
                    with open(f"{batch_name}.txt", 'a') as f:
                        f.write(f"{line}\n")
        await m.reply_document(f"{batch_name}.txt")
    except Exception as e:
        await m.reply_text(f"Error: `{str(e)}`")
