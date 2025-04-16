from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random

@Client.on_message(filters.command("start"))
async def start(bot, message: Message):
    # List of random image URLs
    random_image_urls = [
        "https://graph.org/file/8a7073f6ce349890d306b.jpg",
        "https://graph.org/file/24e49350cbdf44e1b0f1c.jpg",
        "https://graph.org/file/093c58c44f6dc5c6f6e8c.jpg"
    ]

    # Choose a random image URL
    random_image_url = random.choice(random_image_urls)

    # Inline keyboard markup
    reply_markup = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("CLASSPLUS CONTENT", url="https://t.me/Classplus_Content_Center_Bot?start"),
        ]]
    )

    # Send a photo with caption and inline keyboard
    await message.reply_photo(
        photo=random_image_url,
        caption="PLEASE👇PRESS👇HERE",
        quote=True,
        reply_markup=reply_markup
    )
