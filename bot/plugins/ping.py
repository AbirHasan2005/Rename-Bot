# (c) @AbirHasan2005

from bot import Client
from pyrogram import filters
from pyrogram.types import Message
from bot.core.db.add import add_user_to_database


@Client.on_message(filters.command(["start", "ping"]) & ~filters.edited)
async def ping_handler(c: Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await m.reply_text("Hi, I am Rename Bot!\n\n"
                       "I can rename media without downloading it!\n"
                       "Speed depends on your media DC.\n\n"
                       "Just send me media and reply to it with /rename command.")


@Client.on_message(filters.command("help") & ~filters.edited)
async def help_handler(c: Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    await add_user_to_database(c, m)
    await m.reply_text("I can rename media without downloading it!\n"
                       "Speed depends on your media DC.\n\n"
                       "Just send me media and reply to it with /rename command.\n\n"
                       "To set custom thumbnail reply to any image with /set_thumbnail\n\n"
                       "To see custom thumbnail press /show_thumbnail")
