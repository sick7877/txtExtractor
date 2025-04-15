# MIT License
# Copyright (c) 2019-present Dan https://github.com/delivrance
# Code edited by Cryptostark

# Required Libraries
import os
import json
import requests
import cloudscraper
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen  # Enables interactive conversation with users

# Command handler for '/e1'
@Client.on_message(filters.command(["e1"])
async def account_login(bot: Client, m: Message):
    # Step 1: Ask for ID and Password
    editable = await m.reply_text("Send ID & Password like this: ID*Password")

    # Login API endpoint
    login_url = "https://e1coachingcenterapi.classx.co.in/post/userLogin"
    headers = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1"
    }

    # Step 2: Get credentials from user
    creds_msg = await bot.listen(editable.chat.id)
    creds = creds_msg.text.strip().split("*")
    email, password = creds[0], creds[1]

    # Step 3: Login request
    scraper = cloudscraper.create_scraper()
    login_data = {"email": email, "password": password}
    res = scraper.post(login_url, data=login_data, headers=headers).json()

    user_id = res["data"]["userid"]
    token = res["data"]["token"]

    # Authorized headers
    auth_headers = {
        "Host": "e1coachingcenterapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": user_id,
        "Authorization": token
    }

    # Step 4: Fetch courses
    await editable.edit("**Login successful! Fetching batches...**")
    course_url = f"https://e1coachingcenterapi.classx.co.in/get/mycourse?userid={user_id}"
    courses = requests.get(course_url, headers=auth_headers).json()["data"]

    batch_info = "**BATCH-ID - BATCH NAME**\n"
    for course in courses:
        batch_info += f"```{course['id']}``` - **{course['course_name']}**\n"

    await m.reply_text(batch_info)

    # Step 5: Ask for batch ID
    editable2 = await m.reply_text("Send the Batch ID to continue")
    batch_id_msg = await bot.listen(editable2.chat.id)
    batch_id = batch_id_msg.text

    # Step 6: Fetch subjects
    subj_url = f"https://e1coachingcenterapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}"
    subjects = scraper.get(subj_url, headers=auth_headers).json()["data"]
    await m.reply_text(str(subjects))

    # Step 7: Ask for subject ID
    editable3 = await m.reply_text("Enter the Subject ID from the above response")
    subject_id_msg = await bot.listen(editable3.chat.id)
    subject_id = subject_id_msg.text

    # Step 8: Get topics
    topic_url = f"https://e1coachingcenterapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}"
    topics = requests.get(topic_url, headers=auth_headers).json()["data"]

    topic_ids = "&".join([topic["topicid"] for topic in topics])
    topic_list = "\n".join([f"```{t['topicid']}``` - **{t['topic_name']}**" for t in topics])

    await m.reply_text(f"**TOPICS:**\n{topic_list}")
    
    # Step 9: Ask user for topic IDs to download
    editable4 = await m.reply_text(f"Send Topic IDs to download (e.g. `1&2&3`) or this to download all:\n```{topic_ids}```")
    selected_ids_msg = await bot.listen(editable4.chat.id)
    selected_ids = selected_ids_msg.text.split('&')

    # Step 10: Ask for resolution (currently not used but received)
    editable5 = await m.reply_text("Now send the resolution")
    res_msg = await bot.listen(editable5.chat.id)

    # Step 11: Create download directory
    mm = "E1-Coaching-Center"
    os.makedirs("./downloads", exist_ok=True)

    # Step 12: Loop through each topic and decrypt video links
    for topic_id in selected_ids:
        content_url = (
            f"https://e1coachingcenterapi.classx.co.in/get/"
            f"livecourseclassbycoursesubtopconceptapiv3?topicid={topic_id}&start=-1&conceptid=1"
            f"&courseid={batch_id}&subjectid={subject_id}"
        )
        content = requests.get(content_url, headers=auth_headers).json()["data"]

        for item in content:
            title = item["Title"]
            embed = item.get("embed_url") or item.get("pdf_link")
            if embed:
                try:
                    # Decrypt using AES-CBC
                    key = b"638udh3829162018"
                    iv = b"fedcba9876543210"
                    ciphertext = bytearray.fromhex(b64decode(embed.encode()).hex())
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
                    link = decrypted.decode("utf-8")

                    # Save link to file
                    with open(f"./downloads/{mm}.txt", "a") as f:
                        f.write(f"{title}:{link}\n")

                except Exception as e:
                    await m.reply_text(f"Error decrypting: {str(e)}")

    # Step 13: Send file to user
    await m.reply_document(f"./downloads/{mm}.txt")
    await m.reply_text("Done!")
