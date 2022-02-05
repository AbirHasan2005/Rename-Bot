# (c) @AbirHasan2005

import asyncio
from typing import (
    List,
    Union,
    Optional
)
from pyrogram.types import (
    Message,
    MessageEntity,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
    ForceReply
)
from pyrogram.errors import (
    FloodWait
)


class SendFloodedMessage:
    async def send_flooded_message(
            self,
            chat_id: Union[int, str],
            text: str,
            parse_mode: Optional[str] = object,
            entities: Optional[List[MessageEntity]] = None,
            disable_web_page_preview: Optional[bool] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            schedule_date: Optional[int] = None,
            reply_markup: Union[
                InlineKeyboardMarkup,
                ReplyKeyboardMarkup,
                ReplyKeyboardRemove,
                ForceReply, None] = None
    ) -> Optional[Message]:
        """
        Try sending Text Message. But if FloodWait raises, than sleep x time and continue.

        :param chat_id: Unique identifier (int) or username (str) of the target chat. For your personal cloud (Saved Messages) you can simply use "me" or "self". For a contact that exists in your Telegram address book you can use his phone number (str).
        :param text: Text of the message to be sent.
        :param parse_mode: By default, texts are parsed using both Markdown and HTML styles. You can combine both syntax together. Pass "markdown" or "md" to enable Markdown-style parsing only. Pass "html" to enable HTML-style parsing only. Pass None to completely disable style parsing.
        :param entities: List of special entities that appear in message text, which can be specified instead of *parse_mode*.
        :param disable_web_page_preview: Disables link previews for links in this message.
        :param disable_notification: Sends the message silently. Users will receive a notification with no sound.
        :param reply_to_message_id: If the message is a reply, ID of the original message.
        :param schedule_date: Date when the message will be automatically sent. Unix time.
        :param reply_markup: Additional interface options. An object for an inline keyboard, custom reply keyboard, instructions to remove reply keyboard or to force a reply from the user.

        :return: On success, the sent text message is returned.
        """

        try:
            __SEND = await self.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                entities=entities,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                schedule_date=schedule_date,
                reply_markup=reply_markup
            )
            return __SEND
        except FloodWait as e:
            if e.x > 120:
                return None
            print(f"Sleeping for {e.x}s")
            await asyncio.sleep(e.x)
            return await self.send_flooded_message(
                chat_id,
                text,
                parse_mode,
                entities,
                disable_web_page_preview,
                disable_notification,
                reply_to_message_id,
                schedule_date,
                reply_markup
            )
