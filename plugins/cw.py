import os
import time
import json
import requests
import cloudscraper
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen

@Client.on_message(filters.command(["cw"]))
async def cw_handler(bot: Client, m: Message):
    try:
        editable = await m.reply_text("Send the batch ID:")
        input1 = await bot.listen(editable.chat.id)
        batch_id = input1.text

        editable = await m.reply_text("Send the topic ID:")
        input2 = await bot.listen(editable.chat.id)
        topic_id = input2.text

        editable = await m.reply_text("Send the token:")
        input3 = await bot.listen(editable.chat.id)
        token = input3.text

        editable = await m.reply_text("Send a title for the .txt file:")
        input4 = await bot.listen(editable.chat.id)
        t_name = input4.text

        mm = "./downloads/"
        os.makedirs(mm, exist_ok=True)

        url = f"https://elearn.crwilladmin.com/api/v1/comp/topic-list/{batch_id}?topicid={topic_id}&token={token}"
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        data = json.loads(response.content)

        lessons = data["data"]["lessonDetails"]

        for lesson in lessons:
            try:
                lesson_name = lesson["lessonTitle"]
                bcvid = lesson["brightcoveVideoId"]
                vidid = lesson["videoId"]
                bc_url = "https://edge.api.brightcove.com/playback/v1/accounts/6242462559001/videos"
                bc_hdr = {
                    "Accept": "application/json;pk=BCpkADawqM2ooWpqYO0fKbmuhSqdyeRwYXUMTrItBoKVRlZBcrmx8Bt5vHyzj4x9JH_9NwNKnRNTn-6wJ7zQoj09A7VHzHsH5R9cOKgJmJHh0N5KnLjYWrhCyfMQMtkfyP-2aBqW2Ah-DuZw"
                }

                if bcvid.startswith("63"):
                    try:
                        s = requests.Session()
                        html7 = s.get(f"{bc_url}/{bcvid}", headers=bc_hdr).content
                        video1 = json.loads(html7)
                        video_source1 = video1["sources"][5]
                        video_url1 = video_source1["src"]

                        html8 = s.get(f"https://elearn.crwilladmin.com/api/v1/livestreamToken?type=brightcove&vid={vidid}&token={token}").content
                        surl1 = json.loads(html8)
                        stoken1 = surl1["data"]["token"]

                        link = f"{video_url1}&bcov_auth={stoken1}"
                    except Exception as e:
                        print(str(e))
                        link = "Error retrieving Brightcove link."
                else:
                    link = f"https://www.youtube.com/embed/{bcvid}"

                cc = f"{lesson_name}::{link}"
                with open(f"{mm}{t_name}.txt", 'a') as f:
                    f.write(f"{lesson_name}:{link}\n")

            except Exception as e:
                await m.reply_text(f"Error processing lesson: {str(e)}")

        await m.reply_document(f"{mm}{t_name}.txt")

    except Exception as e:
        await m.reply_text(str(e))

    # Notes download
    try:
        notex = await m.reply_text("Do you want to download notes?\n\nSend **y** or **n**")
        input5 = await bot.listen(m.chat.id)
        raw_text5 = input5.text.lower()

        if raw_text5 == 'y':
            scraper = cloudscraper.create_scraper()
            html_notes = scraper.get(f"https://elearn.crwilladmin.com/api/v1/comp/batch-notes/{topic_id}?topicid={topic_id}&token={token}").content
            notes_data = json.loads(html_notes)
            notes = notes_data["data"]["notesDetails"]
            total_notes = len(notes)

            await m.reply_text(f"Total PDFs Found in Batch ID **{topic_id}** is - **{total_notes}**")
            notes.reverse()

            for note in notes:
                try:
                    name = note["docTitle"]
                    url = note["docUrl"]
                    with open(f"{mm}{t_name}.txt", 'a') as f:
                        f.write(f"{name}:{url}\n")
                except Exception as e:
                    await m.reply_text(f"Error processing note: {str(e)}")

            await m.reply_document(f"{mm}{t_name}.txt")

    except Exception as e:
        print(str(e))

    await m.reply_text("Done")
