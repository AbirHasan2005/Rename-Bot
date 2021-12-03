# (c) @AbirHasan2005

import traceback
from typing import Union
from bot.client import Client
from pyrogram import (
    raw,
    utils
)
from pyrogram.types import (
    Message
)
from configs import Config
from bot.core.utils.rm import rm_dir
from bot.core.fixes import fix_thumbnail
from bot.core.db.database import db
from bot.core.file_info import (
    get_thumb_file_id,
    get_media_mime_type
)


async def handle_big_rename(
    c: Client,
    m: Message,
    file_id: Union[
        "raw.types.InputFileBig",
        "raw.types.InputFile"
    ],
    file_name: str,
    editable: Message,
    file_type: str
):
    await editable.edit("Sending to you ...")
    upload_as_doc = await db.get_upload_as_doc(m.from_user.id)

    if (upload_as_doc is False) and (file_type == "video"):
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

    elif (upload_as_doc is False) and (file_type == "audio"):
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

    elif (upload_as_doc is True) or (file_type == "document"):
        _f_thumb = get_thumb_file_id(m.reply_to_message)
        _db_thumb = await db.get_thumbnail(m.from_user.id)
        thumbnail_file_id = _db_thumb \
            if _db_thumb \
            else (_f_thumb
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
        mime_type = get_media_mime_type(m.reply_to_message) or "application/zip"

        media = raw.types.InputMediaUploadedDocument(
            mime_type=mime_type,
            file=file_id,
            force_file=True,
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
    _db_caption = await db.get_caption(m.from_user.id)
    apply_caption = await db.get_apply_caption(m.from_user.id)
    if (not _db_caption) and (apply_caption is True):
        caption = m.reply_to_message.caption.markdown \
            if m.reply_to_message.caption \
            else "**Developer: @AbirHasan2005**"
    elif _db_caption and (apply_caption is True):
        caption = _db_caption
    else:
        caption = ""
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
