# MIT License
# Edited and Improved by ChatGPT
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
import os

@Client.on_message(filters.command(["cp"]) & ~filters.edited)
async def account_login(bot: Client, m: Message):
    s = requests.Session()
    editable = await m.reply_text("**Send Token from ClassPlus App**")
    input1 = await bot.listen(editable.chat.id)
    raw_token = input1.text.strip()
    await input1.delete()

    headers = {
        'authority': 'api.classplusapp.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en',
        'api-version': '28',
        'cache-control': 'no-cache',
        'device-id': '516',
        'origin': 'https://web.classplusapp.com',
        'pragma': 'no-cache',
        'referer': 'https://web.classplusapp.com/',
        'region': 'IN',
        'user-agent': 'Mozilla/5.0',
        'x-access-token': raw_token
    }

    try:
        resp = s.get('https://api.classplusapp.com/v2/batches/details?limit=20&offset=0&sortBy=createdAt', headers=headers)
        resp.raise_for_status()
    except Exception as e:
        return await editable.edit("Login Failed. Please check the token.")

    batches = resp.json().get("data", {}).get("totalBatches", [])
    if not batches:
        return await editable.edit("No batches found.")

    batch_text = "**You have these batches:**\n\n**BATCH-ID - BATCH NAME**\n\n"
    for b in batches:
        batch_text += f"```{b['batchId']}``` - **{b['batchName']}**\n\n"

    await editable.edit(batch_text[:4096])

    editable2 = await m.reply_text("**Now send the Batch ID to fetch folders**")
    input2 = await bot.listen(editable2.chat.id)
    batch_id = input2.text.strip()
    await input2.delete()
    await editable2.delete()

    resp = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={batch_id}', headers=headers)
    folders = resp.json().get('data', {}).get('courseContent', [])
    if not folders:
        return await m.reply_text("No folders found for this batch.")

    folder_text = "**You have these folders:**\n\n**FOLDER-ID - FOLDER NAME**\n\n"
    for f in folders:
        folder_text += f"```{f['id']}``` - **{f['name']}**\n\n"

    await m.reply_text(folder_text[:4096])

    editable3 = await m.reply_text("**Now send the Folder ID to list contents**")
    input3 = await bot.listen(editable3.chat.id)
    folder_id = input3.text.strip()
    await input3.delete()
    await editable3.delete()

    res = s.get(f'https://api.classplusapp.com/v2/course/content/get?courseId={batch_id}&folderId={folder_id}', headers=headers)
    contents = res.json().get('data', {}).get('courseContent', [])
    if not contents:
        return await m.reply_text("No content found in this folder.")

    filename = f"classplus_{m.from_user.id}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for item in contents:
            name = item.get("name", "No Name")
            desc = item.get("description", "")
            url = item.get("url", "#")
            f.write(f"{name} - {desc}: {url}\n")

    await m.reply_document(filename, caption="Here is your content list.")
    os.remove(filename)
