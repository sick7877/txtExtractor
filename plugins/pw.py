
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from subprocess import getstatusoutput

@Client.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("Send Auth code like this:\n\n`AUTH CODE`")
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

    await editable.edit("**Fetching batches...**")

    try:
        response = requests.get('https://api.penpencil.xyz/v3/batches/my-batches', headers=headers).json()["data"]
        batch_list_text = "**Your Batches:**\n\n`Batch Name` : `Batch ID`\n\n"
        for data in response:
            batch_list_text += f"`{data['name']}` : `{data['_id']}`\n"
        await m.reply_text(batch_list_text)
    except Exception as e:
        await m.reply_text(f"Error fetching batches: {e}")
        return

    editable2 = await m.reply_text("**Now send the Batch ID to Download:**")
    input2 = await bot.listen(editable2.chat.id)
    batch_id = input2.text.strip()

    try:
        subjects = requests.get(f'https://api.penpencil.xyz/v3/batches/{batch_id}/details', headers=headers).json()["data"]["subjects"]
    except Exception as e:
        await m.reply_text(f"Error fetching subjects: {e}")
        return

    subject_ids = ""
    await m.reply_text("**Subject List:**\n\n")
    for subj in subjects:
        await m.reply_text(f"`{subj['name']}` : `{subj['_id']}`")
        subject_ids += subj['_id'] + "&"

    editable3 = await m.reply_text(f"**Enter this to download full batch:**\n`{subject_ids}`")
    input3 = await bot.listen(editable3.chat.id)
    raw_subject_ids = input3.text.strip()

    await m.reply_text("**Enter resolution (e.g., 360):**")
    resolution = (await bot.listen(editable3.chat.id)).text.strip()

    await m.reply_text("**Send Thumb URL or type `no`:**")
    thumb_input = (await bot.listen(editable3.chat.id)).text.strip()
    thumb = None
    if thumb_input.lower() != "no":
        getstatusoutput(f"wget '{thumb_input}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    try:
        for subj_id in raw_subject_ids.strip('&').split('&'):
            if not subj_id:
                continue
            all_data = []
            for page in range(1, 5):
                url = f"https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{subj_id}/contents"
                params = {
                    'page': str(page),
                    'tag': '',
                    'contentType': 'exercises-notes-videos',
                    'ut': ''
                }
                r = requests.get(url, params=params, headers=headers)
                try:
                    all_data += r.json()["data"]
                except:
                    continue

            file_name = f"{subj_id}_links.txt"
            with open(file_name, 'w') as f:
                for data in all_data:
                    class_title = data.get("topic")
                    class_url = data.get("url", "").replace("d1d34p8vz63oiq", "d3nzo6itypaz07").replace("mpd", "m3u8")
                    if class_title and class_url:
                        f.write(f"{class_title} : {class_url}\n")
            await m.reply_document(file_name)

    except Exception as e:
        await m.reply_text(f"Unexpected error: {str(e)}")
