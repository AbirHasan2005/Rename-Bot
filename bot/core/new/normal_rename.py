# (c) @AbirHasan2005

import os
import time
from typing import (
    Union,
    Optional,
    List,
    BinaryIO
)
from pyrogram import (
    types,
    raw,
    utils,
    StopTransmission
)
from pyrogram.scaffold import Scaffold
from pyrogram.errors import (
    FilePartMissing,
    MessageNotModified
)
from configs import Config
from bot.core.utils.rm import rm_file
from bot.core.fixes import fix_thumbnail
from bot.core.db.database import db
from bot.core.display import progress_for_pyrogram
from bot.core.utils.audio_info import get_audio_info
from bot.core.utils.video_info import get_video_info
from bot.core.utils.thumbnail_info import get_thumbnail_info


class NormalRename(Scaffold):
    async def normal_rename(
        self,
        file_id: str,
        file_name: str,
        editable: "types.Message",
        chat_id: Union[int, str],
        upload_mode: str = "document",
        thumb: Union[str, BinaryIO] = None,
        caption: str = "",
        parse_mode: Optional[str] = object,
        caption_entities: List["types.MessageEntity"] = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ] = None,
        **kwargs
    ):
        try:
            c_time = time.time()
            dl_file_path = await self.download_media(
                file_id,
                f"{Config.DOWNLOAD_DIR}/{chat_id}/{time.time()}/",
                progress=progress_for_pyrogram,
                progress_args=(
                    "Downloading ...",
                    editable,
                    c_time
                )
            )
            if not os.path.exists(dl_file_path):
                return None, "File not found!"
            try:
                await editable.edit("Please Wait ...")
            except MessageNotModified: pass

            try:
                c_time = time.time()
                file = await self.save_file(dl_file_path, progress=progress_for_pyrogram, progress_args=(
                    "Uploading ...",
                    editable,
                    c_time
                ))

                await editable.edit("Processing Thumbnail ...")
                upload_as_doc = await db.get_upload_as_doc(chat_id)
                has_db_thumb = await db.get_thumbnail(chat_id)
                width = kwargs.get("width", 0)
                height = kwargs.get("height", 0)
                if has_db_thumb or (not upload_as_doc):
                    if (not width) or (not height):
                        height, width = await get_thumbnail_info(thumb)
                    resize_thumb = kwargs.get("resize_thumb", False)
                    if resize_thumb:
                        thumb = await fix_thumbnail(thumb, height)
                    _thumb = await self.save_file(thumb)
                    await rm_file(thumb)
                else:
                    _thumb = None

                if (upload_as_doc is True) or (upload_mode == "document"):
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(dl_file_path) or "application/zip",
                        file=file,
                        thumb=_thumb,
                        attributes=[
                            raw.types.DocumentAttributeFilename(file_name=file_name or os.path.basename(dl_file_path))
                        ]
                    )
                elif (upload_as_doc is False) and (upload_mode == "video"):
                    duration = kwargs.get("duration", 0)
                    if not duration:
                        await editable.edit("Fetching Video Duration ...")
                        duration, _, __ = await get_video_info(dl_file_path)
                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(dl_file_path) or "video/mp4",
                        file=file,
                        thumb=_thumb,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                supports_streaming=True,
                                duration=duration,
                                w=width,
                                h=height
                            ),
                            raw.types.DocumentAttributeFilename(file_name=file_name or os.path.basename(dl_file_path))
                        ]
                    )
                elif (upload_as_doc is False) and (upload_mode == "audio"):

                    duration = kwargs.get("duration", 0)
                    if not duration:
                        duration = await get_audio_info(dl_file_path)
                    performer = kwargs.get("performer", None)
                    title = kwargs.get("title", None)

                    media = raw.types.InputMediaUploadedDocument(
                        mime_type=self.guess_mime_type(dl_file_path) or "audio/mpeg",
                        file=file,
                        thumb=_thumb,
                        attributes=[
                            raw.types.DocumentAttributeAudio(
                                duration=duration,
                                performer=performer,
                                title=title
                            ),
                            raw.types.DocumentAttributeFilename(file_name=file_name or os.path.basename(dl_file_path))
                        ]
                    )

                else:
                    await editable.edit("I can't rename this type of media!")
                    await rm_file(dl_file_path)
                    return None, "InvalidMedia"

                while True:
                    try:
                        r = await self.send(
                            raw.functions.messages.SendMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=media,
                                silent=disable_notification or None,
                                reply_to_msg_id=reply_to_message_id,
                                random_id=self.rnd_id(),
                                schedule_date=schedule_date,
                                reply_markup=await reply_markup.write(self) if reply_markup else None,
                                **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
                            )
                        )
                    except FilePartMissing as e:
                        await self.save_file(dl_file_path, file_id=file.id, file_part=e.x)
                    else:
                        await editable.edit("Uploaded Successfully!")
                        await rm_file(dl_file_path)
                        return True, False
            except StopTransmission:
                await rm_file(dl_file_path)
                return None, "StopTransmission"
        except Exception as err:
            Config.LOGGER.getLogger(__name__).error(err)
            return None, f"{err}"
