# (c) @AbirHasan2005

import os
import time
import random
import traceback
from typing import (
    List,
    Union,
    Optional,
    BinaryIO
)
from PIL import Image
from pyrogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
    MessageEntity,
    Message
)
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

from configs import Config
from bot.core.ffmpeg import take_screen_shot
from bot.core.utils.video_info import get_audio_or_video_duration, get_video_height, get_video_width
from bot.core.display import progress_for_pyrogram


class UploadVideo:
    async def upload_video(
        self,
        chat_id: Union[int, str],
        video: str,
        editable_message: Message,
        caption: str = "",
        parse_mode: Optional[str] = object,
        caption_entities: List[MessageEntity] = None,
        ttl_seconds: Optional[int] = None,
        duration: int = 0,
        width: int = 0,
        height: int = 0,
        thumb: Union[str, BinaryIO] = None,
        file_name: str = None,
        supports_streaming: bool = True,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, None] = None,
        status_message: str = "📤 Uploading as Video ..."
    ) -> Optional[Message]:
        """
        Advanced Video Uploader Function.

        :param chat_id: Unique identifier (int) or username (str) of the target chat. For your personal cloud (Saved Messages) you can simply use "me" or "self". For a contact that exists in your Telegram address book you can use his phone number (str).
        :param video: Video to send. Pass a video file path as string to upload a new video that exists on your local machine.
        :param editable_message: Pass editable Message object for updating with progress text.
        :param parse_mode: By default, texts are parsed using both Markdown and HTML styles. You can combine both syntaxes together. Pass "markdown" or "md" to enable Markdown-style parsing only. Pass "html" to enable HTML-style parsing only. Pass None to completely disable style parsing.
        :param caption: Video caption, 0-1024 characters.
        :param caption_entities: List of special entities that appear in the caption, which can be specified instead of *parse_mode*.
        :param ttl_seconds: Self-Destruct Timer. If you set a timer, the video will self-destruct in *ttl_seconds* seconds after it was viewed.
        :param duration: Duration of sent video in seconds. By default function will try to get duration data from video.
        :param width: Video width. By default function will try to get width data from video.
        :param height: Video height. By default function will try to get height data from video.
        :param thumb: Thumbnail of the video sent. The thumbnail should be in JPEG format and less than 200 KB in size. A thumbnail's width and height should not exceed 320 pixels. Thumbnails can't be reused and can be only uploaded as a new file. By default function will take random screenshot from video and use it as thumbnail.
        :param file_name: File name of the video sent. Defaults to file's path basename.
        :param supports_streaming: Pass True, if the uploaded video is suitable for streaming. Defaults to True.
        :param disable_notification: Sends the message silently. Users will receive a notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the original message.
        :param schedule_date: Date when the message will be automatically sent. Unix time.
        :param reply_markup: Additional interface options. An object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        :param status_message: Pass status string. Default: "📤 Uploading as Video ..."
        """

        duration = duration or (await get_audio_or_video_duration(video))
        height = height or (await get_video_height(video))
        width = width or (await get_video_width(video))
        metadata = extractMetadata(createParser(video))
        if metadata.has("duration"):
            duration = metadata.get("duration").seconds
        if thumb is None:
            if not os.path.exists(video):
                return None
            try:
                ss_dir = f"{Config.DOWN_PATH}/Thumbnails/{str(time.time())}/"
                thumbnail = await take_screen_shot(
                    video_file=video,
                    output_directory=ss_dir,
                    ttl=random.randint(0, (duration or 1) - 1)
                )
                if metadata.has("width"):
                    t_width = metadata.get("width")
                else:
                    t_width = width or 90
                if metadata.has("height"):
                    t_height = metadata.get("height")
                else:
                    t_height = height or 90
                if os.path.exists(thumbnail):
                    Image.open(thumbnail).convert("RGB").save(thumbnail)
                    img = Image.open(thumbnail)
                    img.resize((width, height))
                    img.save(thumbnail, "JPEG")
                else:
                    thumbnail = None
            except Exception as error:
                print("Unable to Get Video Data!\n\n"
                      f"Error: {error}")
                traceback.print_exc()
                thumbnail = None
        else:
            thumbnail = thumb
        if not caption:
            caption = f"**File Name:** `{os.path.basename(video)}`" \
                      "\n\n**@AH_RenameBot**"
        c_time = time.time()
        await self.send_video(
            chat_id=chat_id,
            video=video,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            ttl_seconds=ttl_seconds,
            duration=duration,
            width=width or 90,
            height=height or 90,
            thumb=thumbnail,
            file_name=file_name,
            supports_streaming=supports_streaming,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            reply_markup=reply_markup,
            progress=progress_for_pyrogram,
            progress_args=(
                status_message,
                editable_message,
                c_time
            )
        )
        await editable_message.edit("Uploaded Successfully!")
