# (c) @AbirHasan2005

import time
import traceback
from bot import Client
from pyrogram import (
    filters,
    raw,
    utils
)
from pyrogram.file_id import FileId
from pyrogram.types import Message
from bot.core.file_info import (
    get_media_file_id,
    get_media_file_size,
    get_media_file_name,
    get_file_type
)
from configs import Config
from bot.core.fixes import fix_thumbnail
from bot.core.display import progress_for_pyrogram
from bot.core.utils.rm import rm_dir
from bot.core.db.database import db
from bot.core.db.add import add_user_to_database
from bot.core.handlers.time_gap import check_time_gap


@Client.on_message(filters.command(["rename", "r"]) & ~filters.edited)
async def rename_handler(c: Client, m: Message):
    # Checks
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    is_in_gap, sleep_time = await check_time_gap(m.from_user.id)
    if is_in_gap:
        await m.reply_text("Sorry Sir,\n"
                           "No Flooding Allowed!\n\n"
                           f"Send After `{str(sleep_time)}s` !!",
                           quote=True)
        return
    await add_user_to_database(c, m)
    if (not m.reply_to_message) or (not m.reply_to_message.media):
        return await m.reply_text("Reply to any media to rename it!", quote=True)

    # Proceed
    editable = await m.reply_text("Now send me new file name!", quote=True)
    user_input_msg: Message = await c.listen(m.chat.id, timeout=300)
    if user_input_msg.text is None:
        await editable.edit("Process Cancelled!")
        return await user_input_msg.continue_propagation()
    if user_input_msg.text and user_input_msg.text.startswith("/"):
        await editable.edit("Process Cancelled!")
        return await user_input_msg.continue_propagation()
    if user_input_msg.text.rsplit(".", 1)[-1].lower() != get_media_file_name(m.reply_to_message).rsplit(".", 1)[-1].lower():
        file_name = user_input_msg.text.rsplit(".", 1)[0][:255] + "." + get_media_file_name(m.reply_to_message).rsplit(".", 1)[-1].lower()
    else:
        file_name = user_input_msg.text[:255]
    await editable.edit("Please Wait ...")
    file_type = get_file_type(m.reply_to_message)
    _c_file_id = FileId.decode(get_media_file_id(m.reply_to_message))
    try:
        c_time = time.time()
        file_id = await c.custom_upload(
            file_id=_c_file_id,
            file_size=get_media_file_size(m.reply_to_message),
            file_name=file_name,
            progress=progress_for_pyrogram,
            progress_args=(
                "Uploading ...\n"
                f"DC: {_c_file_id.dc_id}",
                editable,
                c_time
            )
        )
        if not file_id:
            return await editable.edit("Failed to Rename!")

        await editable.edit("Sending to you ...")

        if file_type == "video":
            ttl_seconds = None
            supports_streaming = m.reply_to_message.video.supports_streaming \
                if m.reply_to_message.video.supports_streaming \
                else None
            duration = m.reply_to_message.video.duration \
                if m.reply_to_message.video.duration \
                else 0
            width = m.reply_to_message.video.width \
                if m.reply_to_message.video.width \
                else 0
            height = m.reply_to_message.video.height \
                if m.reply_to_message.video.height \
                else 0
            mime_type = m.reply_to_message.video.mime_type \
                if m.reply_to_message.video.mime_type \
                else "video/mp4"
            _f_thumb = m.reply_to_message.video.thumbs[0] \
                if m.reply_to_message.video.thumbs \
                else None
            _db_thumb = await db.get_thumbnail(m.from_user.id)
            thumbnail_file_id = _db_thumb \
                if _db_thumb \
                else (_f_thumb.file_id
                      if _f_thumb
                      else None)
            if thumbnail_file_id:
                await editable.edit("Fetching Thumbnail ...")
                thumb_path = await c.download_media(thumbnail_file_id,
                                                    f"{Config.DOWNLOAD_DIR}/{m.from_user.id}/{m.message_id}/")
                if _db_thumb:
                    thumb_path = await fix_thumbnail(thumb_path)
                thumb = await c.save_file(path=thumb_path)
            else:
                thumb = None

            media = raw.types.InputMediaUploadedDocument(
                mime_type=mime_type,
                file=file_id,
                ttl_seconds=ttl_seconds,
                thumb=thumb,
                attributes=[
                    raw.types.DocumentAttributeVideo(
                        supports_streaming=supports_streaming,
                        duration=duration,
                        w=width,
                        h=height
                    ),
                    raw.types.DocumentAttributeFilename(file_name=file_name)
                ]
            )

        elif file_type == "audio":
            _f_thumb = m.reply_to_message.audio.thumbs[0] \
                if m.reply_to_message.audio.thumbs \
                else None
            _db_thumb = await db.get_thumbnail(m.from_user.id)
            thumbnail_file_id = _db_thumb \
                if _db_thumb \
                else (_f_thumb.file_id
                      if _f_thumb
                      else None)
            if thumbnail_file_id:
                await editable.edit("Fetching Thumbnail ...")
                thumb_path = await c.download_media(thumbnail_file_id,
                                                    f"{Config.DOWNLOAD_DIR}/{m.from_user.id}/{m.message_id}/")
                if _db_thumb:
                    thumb_path = await fix_thumbnail(thumb_path)
                thumb = await c.save_file(path=thumb_path)
            else:
                thumb = None
            mime_type = m.reply_to_message.audio.mime_type \
                if m.reply_to_message.audio.mime_type \
                else "audio/mpeg"
            duration = m.reply_to_message.audio.duration \
                if m.reply_to_message.audio.duration \
                else None
            performer = m.reply_to_message.audio.performer \
                if m.reply_to_message.audio.performer \
                else None
            title = m.reply_to_message.audio.title \
                if m.reply_to_message.audio.title \
                else None

            media = raw.types.InputMediaUploadedDocument(
                mime_type=mime_type,
                file=file_id,
                force_file=None,
                thumb=thumb,
                attributes=[
                    raw.types.DocumentAttributeAudio(
                        duration=duration,
                        performer=performer,
                        title=title
                    ),
                    raw.types.DocumentAttributeFilename(file_name=file_name)
                ]
            )

        elif file_type == "document":
            _f_thumb = m.reply_to_message.document.thumbs[0] \
                if m.reply_to_message.document.thumbs \
                else None
            _db_thumb = await db.get_thumbnail(m.from_user.id)
            thumbnail_file_id = _db_thumb \
                if _db_thumb \
                else (_f_thumb.file_id
                      if _f_thumb
                      else None)
            if thumbnail_file_id:
                await editable.edit("Fetching Thumbnail ...")
                thumb_path = await c.download_media(thumbnail_file_id,
                                                    f"{Config.DOWNLOAD_DIR}/{m.from_user.id}/{m.message_id}/")
                if _db_thumb:
                    thumb_path = await fix_thumbnail(thumb_path)
                thumb = await c.save_file(path=thumb_path)
            else:
                thumb = None
            mime_type = m.reply_to_message.document.mime_type \
                if m.reply_to_message.document.mime_type \
                else "application/zip"

            media = raw.types.InputMediaUploadedDocument(
                mime_type=mime_type,
                file=file_id,
                force_file=None,
                thumb=thumb,
                attributes=[
                    raw.types.DocumentAttributeFilename(file_name=file_name)
                ]
            )
        else:
            return await editable.edit("I can't rename it!")

        reply_markup = m.reply_to_message.reply_markup \
            if m.reply_to_message.reply_markup \
            else None
        caption = m.reply_to_message.caption.markdown \
            if m.reply_to_message.caption \
            else "**Developer: @AbirHasan2005**"
        parse_mode = "Markdown"

        try:
            r = await c.send(
                raw.functions.messages.SendMedia(
                    peer=await c.resolve_peer(m.chat.id),
                    media=media,
                    silent=None,
                    reply_to_msg_id=None,
                    random_id=c.rnd_id(),
                    schedule_date=None,
                    reply_markup=await reply_markup.write(c) if reply_markup else None,
                    **await utils.parse_text_entities(c, caption, parse_mode, None)
                )
            )
            await rm_dir(f"{Config.DOWNLOAD_DIR}/{m.from_user.id}/{m.message_id}/")
        except Exception as _err:
            Config.LOGGER.getLogger(__name__).error(_err)
            Config.LOGGER.getLogger(__name__).info(f"{traceback.format_exc()}")
        else:
            await editable.edit("Uploaded Successfully!")
    except Exception as err:
        await editable.edit("Failed to Rename File!\n\n"
                            f"**Error:** `{err}`\n\n"
                            f"**Traceback:** `{traceback.format_exc()}`")
