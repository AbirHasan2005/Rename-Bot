# (c) @AbirHasan2005

import os
import asyncio
import time
import random
from PIL import Image
from configs import Config
from helpers.clean import delete_one, delete_all
from helpers.display_progress import progress_for_pyrogram, humanbytes
from helpers.database.access_db import db
from helpers.check_gap import CheckTimeGap
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Thumbnail


async def UploadFile(bot: Client, message: Message, file_path: str, file_size):
    try:
        caption_ = await db.get_caption(message.chat.id)
        db_thumbnail = await db.get_thumbnail(message.chat.id)
        file_thumbnail = None
        if db_thumbnail is not None:
            file_thumbnail = await bot.download_media(
                message=db_thumbnail,
                file_name=f"{Config.DOWNLOAD_PATH}/{str(message.chat.id)}/thumbnail/"
            )
            Image.open(file_thumbnail).convert("RGB").save(file_thumbnail)
            img = Image.open(file_thumbnail)
            img.resize((100, 100))
            img.save(file_thumbnail, "JPEG")
        c_time = time.time()
        sent_ = await bot.send_document(
            chat_id=message.chat.id,
            document=file_path,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading File ...",
                message,
                c_time
            ),
            force_document=True,
            thumb=file_thumbnail,
            caption=((Config.CAPTION.format((await bot.get_me()).username) + f"\n\n**File Name:** `{file_path.rsplit('/', 1)[-1]}`\n**File Size:** `{humanbytes(file_size)}`") if (caption_ is None) else caption_),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Developer - @AbirHasan2005", url="https://t.me/AbirHasan2005")],
                    [InlineKeyboardButton("Support Group", url="https://t.me/DevsZone"),
                     InlineKeyboardButton("Bots Channel", url="https://t.me/Discovery_Updates")]
                ]
            )
        )
        await asyncio.sleep(Config.SLEEP_TIME)
        forward_ = await sent_.forward(chat_id=Config.LOG_CHANNEL)
        await forward_.reply_text(
            text=f"**User:** [{message.chat.first_name}](tg://user?id={str(message.chat.id)})\n**Username:** `{message.chat.username}`\n**UserID:** `{message.chat.id}`",
            disable_web_page_preview=True,
            quote=True
        )
    except Exception as err:
        try:
            await message.edit(f"Failed to File!\n**Error:**\n`{err}`")
            await asyncio.sleep(50)
        except:
            print(f"Failed to Upload File!\nError: {err}")
    await delete_one(file_path)
    if Config.ONE_PROCESS_ONLY:
        await CheckTimeGap(message.chat.id, rm_gap=True)
    await message.delete(True)


async def UploadVideo(bot: Client, message: Message, file_path: str, file_size, width: int = 100, height: int = 100, duration: int = 0, default_thumb: Thumbnail = None):
    try:
        metadata = extractMetadata(createParser(file_path))
        if (duration == 0) and metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if ((width == 0) or (width == 100)) and metadata.has("width"):
            width = metadata.get("width")
        if ((height == 0) or (height == 100)) and metadata.has("height"):
            height = metadata.get("height")
        db_thumbnail = await db.get_thumbnail(message.chat.id)
        if db_thumbnail is not None:
            video_thumbnail = await bot.download_media(
                message=db_thumbnail,
                file_name=f"{Config.DOWNLOAD_PATH}/{str(message.chat.id)}/thumbnail/"
            )
            Image.open(video_thumbnail).convert("RGB").save(video_thumbnail)
            img = Image.open(video_thumbnail)
            img.resize((width, height))
            img.save(video_thumbnail, "JPEG")
        elif default_thumb is not None:
            video_thumbnail = await bot.download_media(
                message=default_thumb.file_id,
                file_name=f"{Config.DOWNLOAD_PATH}/{str(message.chat.id)}/thumbnail/"
            )
            Image.open(video_thumbnail).convert("RGB").save(video_thumbnail)
            img = Image.open(video_thumbnail)
            img.resize((width, height))
            img.save(video_thumbnail, "JPEG")
        else:
            video_thumbnail = Config.DOWNLOAD_PATH + "/" + str(message.chat.id) + "/thumbnail/" + str(time.time()) + ".jpg"
            ttl = random.randint(0, int(duration) - 1)
            file_generator_command = [
                "ffmpeg",
                "-ss",
                str(ttl),
                "-i",
                file_path,
                "-vframes",
                "1",
                video_thumbnail
            ]
            process = await asyncio.create_subprocess_exec(
                *file_generator_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            e_response = stderr.decode().strip()
            t_response = stdout.decode().strip()
            print(t_response)
            print(e_response)
            if os.path.lexists(video_thumbnail):
                Image.open(video_thumbnail).convert("RGB").save(video_thumbnail)
                img = Image.open(video_thumbnail)
                img.resize((width, height))
                img.save(video_thumbnail, "JPEG")
            else:
                video_thumbnail = None
        caption_ = await db.get_caption(message.chat.id)
        c_time = time.time()
        sent_ = await bot.send_video(
            chat_id=message.chat.id,
            video=file_path,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading Video ...",
                message,
                c_time
            ),
            duration=duration,
            thumb=video_thumbnail,
            width=width,
            height=height,
            caption=((Config.CAPTION.format((await bot.get_me()).username) + f"\n\n**File Name:** `{file_path.rsplit('/', 1)[-1]}`\n**File Size:** `{humanbytes(file_size)}`") if (caption_ is None) else caption_),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Developer - @AbirHasan2005", url="https://t.me/AbirHasan2005")],
                    [InlineKeyboardButton("Support Group", url="https://t.me/DevsZone"),
                     InlineKeyboardButton("Bots Channel", url="https://t.me/Discovery_Updates")]
                ]
            )
        )
        await asyncio.sleep(Config.SLEEP_TIME)
        forward_ = await sent_.forward(chat_id=Config.LOG_CHANNEL)
        await forward_.reply_text(
            text=f"**User:** [{message.chat.first_name}](tg://user?id={str(message.chat.id)})\n**Username:** `{message.chat.username}`\n**UserID:** `{message.chat.id}`",
            disable_web_page_preview=True,
            quote=True
        )
    except Exception as err:
        try:
            await message.edit(f"Failed to File!\n**Error:**\n`{err}`")
            await asyncio.sleep(50)
        except:
            print(f"Failed to Upload File!\nError: {err}")
    await delete_one(file_path)
    if Config.ONE_PROCESS_ONLY:
        await CheckTimeGap(message.chat.id, rm_gap=True)
    await delete_all(root=Config.DOWNLOAD_PATH + "/" + str(message.chat.id) + "/thumbnail/")
    await message.delete(True)


async def UploadAudio(bot: Client, message: Message, file_path: str, file_size, duration: int, title: str, performer: str):
    try:
        caption_ = await db.get_caption(message.chat.id)
        db_thumbnail = await db.get_thumbnail(message.chat.id)
        file_thumbnail = None
        if db_thumbnail is not None:
            file_thumbnail = await bot.download_media(
                message=db_thumbnail,
                file_name=f"{Config.DOWNLOAD_PATH}/{str(message.chat.id)}/thumbnail/"
            )
            Image.open(file_thumbnail).convert("RGB").save(file_thumbnail)
            img = Image.open(file_thumbnail)
            img.resize((100, 100))
            img.save(file_thumbnail, "JPEG")
        c_time = time.time()
        sent_ = await bot.send_audio(
            chat_id=message.chat.id,
            audio=file_path,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading Audio ...",
                message,
                c_time
            ),
            thumb=file_thumbnail,
            duration=(duration if (duration is not None) else 0),
            performer=(performer if (performer is not None) else "Abir Hasan"),
            title=(title if (title is not None) else file_path.rsplit('/', 1)[-1].rsplit(".", 1)[0]),
            caption=((Config.CAPTION.format((await bot.get_me()).username) + f"\n\n**File Name:** `{file_path.rsplit('/', 1)[-1]}`\n**File Size:** `{humanbytes(file_size)}`") if (caption_ is None) else caption_),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Developer - @AbirHasan2005", url="https://t.me/AbirHasan2005")],
                    [InlineKeyboardButton("Support Group", url="https://t.me/DevsZone"),
                     InlineKeyboardButton("Bots Channel", url="https://t.me/Discovery_Updates")]
                ]
            )
        )
        await asyncio.sleep(Config.SLEEP_TIME)
        forward_ = await sent_.forward(chat_id=Config.LOG_CHANNEL)
        await forward_.reply_text(
            text=f"**User:** [{message.chat.first_name}](tg://user?id={str(message.chat.id)})\n**Username:** `{message.chat.username}`\n**UserID:** `{message.chat.id}`",
            disable_web_page_preview=True,
            quote=True
        )
    except Exception as err:
        try:
            await message.edit(f"Failed to File!\n**Error:**\n`{err}`")
            await asyncio.sleep(50)
            raise err
        except:
            print(f"Failed to Upload File!\nError: {err}")
    await delete_one(file_path)
    if Config.ONE_PROCESS_ONLY:
        await CheckTimeGap(message.chat.id, rm_gap=True)
    await message.delete(True)
