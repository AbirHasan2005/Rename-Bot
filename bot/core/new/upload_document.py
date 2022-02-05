# (c) @AbirHasan2005

import os
import time
from typing import (
    List,
    Union,
    Optional,
    BinaryIO
)
from pyrogram.types import (
    Message,
    MessageEntity,
    ForceReply,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup
)
from bot.core.display import progress_for_pyrogram


class UploadDocument:
    async def upload_document(
        self,
        chat_id: Union[int, str],
        document: str,
        editable_message: Message,
        caption: str = "",
        parse_mode: Optional[str] = object,
        caption_entities: List[MessageEntity] = None,
        thumb: Union[str, BinaryIO] = None,
        file_name: str = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: int = None,
        reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, None] = None,
        status_message: str = "📤 Uploading as Document ..."
    ):
        """
        Advanced Document Uploader Function.

        :param chat_id: Unique identifier (int) or username (str) of the target chat. For your personal cloud (Saved Messages) you can simply use "me" or "self". For a contact that exists in your Telegram address book you can use his phone number (str).
        :param document: Document to send. Pass a file path as string to upload a new document that exists on your local machine.
        :param editable_message: Pass editable Message object for updating with progress text.
        :param parse_mode: By default, texts are parsed using both Markdown and HTML styles. You can combine both syntaxes together. Pass "markdown" or "md" to enable Markdown-style parsing only. Pass "html" to enable HTML-style parsing only. Pass None to completely disable style parsing.
        :param caption: Video caption, 0-1024 characters.
        :param caption_entities: List of special entities that appear in the caption, which can be specified instead of *parse_mode*.
        :param thumb: Thumbnail of the video sent. The thumbnail should be in JPEG format and less than 200 KB in size. A thumbnail's width and height should not exceed 320 pixels. Thumbnails can't be reused and can be only uploaded as a new file. By default function will take random screenshot from video and use it as thumbnail.
        :param file_name: File name of the video sent. Defaults to file's path basename.
        :param disable_notification: Sends the message silently. Users will receive a notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the original message.
        :param schedule_date: Date when the message will be automatically sent. Unix time.
        :param reply_markup: Additional interface options. An object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.
        :param status_message: Pass status string. Default: "📤 Uploading as Video ..."
        """

        if not caption:
            caption = f"**File Name:** `{os.path.basename(document)}`" \
                      "\n\n**@AH_RenameBot**"
        c_time = time.time()
        await self.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            thumb=thumb,
            file_name=file_name,
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
