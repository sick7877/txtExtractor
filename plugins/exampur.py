import urllib.parse
import requests
import json
from pyrogram import Client, filters
from pyrogram.types import Message
import cloudscraper
import os

# Main command handler
@Client.on_message(filters.command(["exampur"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text("Send ID & Password in this format: email*password")

    input1: Message = await bot.listen(m.chat.id)
    raw_text = input1.text
    try:
        email, password = raw_text.split("*")
    except ValueError:
        await m.reply_text("Invalid format. Please send as email*password")
        return

    await input1.delete()

    BASE_URL = "https://exampur.videocrypt.in"
    login_url = f"{BASE_URL}/auth/login"
    headers = {
        "appauthtoken": "no_token",
        "User-Agent": "Dart/2.15(dart:io)",
        "content-type": "application/json; charset=UTF-8",
        "Accept-Encoding": "gzip",
        "host": "exampur.videocrypt.in"
    }

    payload = json.dumps({
        "phone_ext": "91",
        "phone": "",
        "email": email,
        "password": password
    })

    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.post(login_url, data=payload, headers=headers).content
        output = json.loads(res)
        token = output["data"]["authToken"]
    except Exception as e:
        await m.reply_text(f"Login failed: {e}")
        return

    auth_headers = headers.copy()
    auth_headers["appauthtoken"] = token

    await m.reply_text("**Login Successful**")

    try:
        res1 = requests.get(f"{BASE_URL}/mycourses", headers=auth_headers)
        b_data = res1.json()['data']
    except:
        await m.reply_text("Failed to retrieve batches.")
        return

    batch_text = "**BATCH-ID - BATCH NAME**\n\n"
    for data in b_data:
        batch_text += f"```{data['_id']}``` - **{data['title']}**\n\n"

    await m.reply_text(batch_text)

    editable = await m.reply_text("**Now send the Batch ID to Download**")
    input2 = await bot.listen(m.chat.id)
    batch_id = input2.text

    try:
        subj_res = scraper.get(
            f"{BASE_URL}/course_subject/{batch_id}",
            headers=auth_headers
        ).content
        subj_data = json.loads(subj_res)["data"]
    except:
        await m.reply_text("Failed to fetch subjects.")
        return

    subj_ids = "".join([f"{s['_id']}&" for s in subj_data]).strip("&")
    await m.reply_text(f"Send the **Subject IDs** to download like `id1&id2`\n\nAll IDs:\n```{subj_ids}```")

    input3 = await bot.listen(m.chat.id)
    subj_input = input3.text.split("&")

    try:
        for subj_id in subj_input:
            chapter_res = requests.get(
                f"{BASE_URL}/course_material/chapter/{subj_id}/{batch_id}",
                headers=auth_headers
            )
            chapters = chapter_res.json()['data']

            for chapter in chapters:
                enc_chap = urllib.parse.quote(chapter, safe="")
                enc_chap = enc_chap.replace("%28", "(").replace("%29", ")").replace("%26", "&")

                material_res = requests.get(
                    f"{BASE_URL}/course_material/material/{subj_id}/{batch_id}/{enc_chap}",
                    headers=auth_headers
                )
                materials = material_res.json()['data']

                for material in materials:
                    title = material["title"].replace("/", "_")
                    video_link = material.get("video_link")
                    pdf_link = material.get("material_url")

                    if video_link:
                        file_path = f"{title}.mp4"
                        with open(file_path, "wb") as f:
                            f.write(requests.get(video_link).content)
                        await bot.send_video(m.chat.id, video=file_path, caption=title)
                        os.remove(file_path)

                    elif pdf_link:
                        file_path = f"{title}.pdf"
                        with open(file_path, "wb") as f:
                            f.write(requests.get(pdf_link).content)
                        await bot.send_document(m.chat.id, document=file_path, caption=title)
                        os.remove(file_path)

        await m.reply_text("**All available materials have been sent.**")

    except Exception as e:
        await m.reply_text(f"**Error:** {str(e)}")
