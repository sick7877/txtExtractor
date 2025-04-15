# MIT License
# Copyright (c) 2019-present Dan
# Edited by Cryptostark

import os
import sys
import json
import time
import re
import logging
import requests
import urllib
import subprocess
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from subprocess import getstatusoutput
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, User
from pyromod import listen
import tgcrypto
from p_bar import progress_bar
import helper
import cloudscraper

# Instantiate the bot properly
bot = Client("my_bot")

@bot.on_edited_message(filters.command(["start"]))
async def account_login(client: Client, m: Message):
    global cancel
    cancel = False

    await m.reply_text("Copy & Paste any one of the Institute Codes:\n"
                       "**Ankit With Rojgar** :- **rozgarapinew.teachx.in**\n"
                       "**The Last Exam** :- **lastexamapi.teachx.in**\n"
                       "**The Mission Institute** :- **missionapi.appx.co.in**")

    input01: Message = await bot.listen(m.chat.id)
    Ins = input01.text.strip()

    await m.reply_text("Send **ID & Password** in format: `ID*Password`")
    input1: Message = await bot.listen(m.chat.id)
    raw_text = input1.text
    email, password = raw_text.split("*")

    # Login API
    login_url = f"https://{Ins}/post/login"
    headers = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-ID": "-2",
        "Authorization": "",
        "Content-Type": "application/x-www-form-urlencoded",
        "Language": "en",
        "User-Agent": "okhttp/4.9.1"
    }
    data = {"email": email, "password": password}
    res = requests.post(login_url, data=data, headers=headers).content
    output = json.loads(res)

    try:
        userid = output["data"]["userid"]
        token = output["data"]["token"]
    except:
        await m.reply_text("Login failed or invalid credentials.")
        return

    host_header = Ins
    hdr1 = {
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-ID": userid,
        "Authorization": token,
        "Language": "en",
        "Host": host_header,
        "User-Agent": "okhttp/4.9.1"
    }

    await m.reply_text("**Login Successful**")

    # Fetch batch
    batch_url = f"https://{Ins}/get/mycourse?userid={userid}"
    res1 = requests.get(batch_url, headers=hdr1)
    b_data = res1.json()['data']
    course_list = "**BATCH-ID - BATCH NAME - INSTRUCTOR**\n\n"

    for data in b_data:
        course_list += f"```{data['id']}``` - **{data['course_name']}**\n"

    await m.reply_text(course_list)
    await m.reply_text("**Now send the Batch ID to Download**")
    input2 = await bot.listen(m.chat.id)
    course_id = input2.text.strip()

    subject_url = f"https://{Ins}/get/allsubjectfrmlivecourseclass?courseid={course_id}"
    res2 = requests.get(subject_url, headers=hdr1).json()
    await m.reply_text(res2["data"])

    await m.reply_text("**Enter the Subject ID shown above**")
    input3 = await bot.listen(m.chat.id)
    subject_id = input3.text.strip()

    topic_url = f"https://{Ins}/get/alltopicfrmlivecourseclass?courseid={course_id}&subjectid={subject_id}"
    res3 = requests.get(topic_url, headers=hdr1)
    b_data2 = res3.json()['data']

    topic_list = "**TOPIC-ID - TOPIC - VIDEOS**\n\n"
    vj = ""
    for data in b_data2:
        topic_list += f"```{data['topicid']}``` - **{data['topic_name']}**\n"
        vj += f"{data['topicid']}&"

    await m.reply_text(topic_list)
    await m.reply_text(f"Now send the **Topic IDs** to Download\n"
                       f"Send like this **1&2&3** or use this:\n```{vj.strip('&')}```")

    input4 = await bot.listen(m.chat.id)
    topic_ids = input4.text.strip().split("&")

    await m.reply_text("**Now send the Resolution**")
    input5 = await bot.listen(m.chat.id)
    resolution = input5.text.strip()

    try:
        mm = "Ankit-With-Rojgar"
        t_name = b_data2[0]["topic_name"]
        file_path = f"{mm}{t_name}.txt"

        for tid in topic_ids:
            if "lastexamapi" in Ins:
                url = f"https://{Ins}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={tid}&start=-1&courseid={course_id}&subjectid={subject_id}"
            elif "missionapi" in Ins:
                url = f"https://{Ins}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={tid}&start=-1&conceptid=4&courseid={course_id}&subjectid={subject_id}"
            else:
                url = f"https://{Ins}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={tid}&start=-1&conceptid=1&courseid={course_id}&subjectid={subject_id}"

            res4 = requests.get(url, headers=hdr1).json()
            topicid = res4["data"]

            for data in topicid:
                b64 = data.get("download_link") or data.get("pdf_link")
                tid_title = re.sub(r"[^\w\s]", "", data["Title"])
                key = "638udh3829162018".encode("utf8")
                iv = "fedcba9876543210".encode("utf8")
                ciphertext = bytearray.fromhex(b64decode(b64.encode()).hex())
                cipher = AES.new(key, AES.MODE_CBC, iv)
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                url = plaintext.decode('utf-8')

                with open(file_path, 'a') as f:
                    f.write(f"{tid_title}:{url}\n")

        await m.reply_document(file_path)
    except Exception as e:
        await m.reply_text(f"Error: {e}")

    await m.reply_text("Done")
