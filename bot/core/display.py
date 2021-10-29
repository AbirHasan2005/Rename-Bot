# (c) @AbirHasan2005

import math
import time
import asyncio
from bot import bot
from typing import Union
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import FloodWait

PROGRESS = """
⏳ **Percentage:** `{0}%`
✅ **Done:** `{1}`
💠 **Total:** `{2}`
📶 **Speed:** `{3}/s`
🕰 **ETA:** `{4}`
"""


async def progress_for_pyrogram(
    current,
    total,
    ud_type,
    message: Union[Message, CallbackQuery],
    start
):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "[{0}{1}] \n".format(
            ''.join(["●" for _ in range(math.floor(percentage / 5))]),
            ''.join(["○" for _ in range(20 - math.floor(percentage / 5))])
            )

        tmp = progress + PROGRESS.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            try:
                _ = message.message_id
                await message.edit(
                    text="**{}**\n\n {}".format(
                        ud_type,
                        tmp
                    ),
                    parse_mode='markdown'
                )
            except AttributeError:
                await bot.edit_inline_caption(
                    inline_message_id=message.inline_message_id,
                    caption="**{}**\n\n {}".format(
                        ud_type,
                        tmp
                    ),
                    parse_mode='markdown'
                )
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception:
            pass


def humanbytes(size):
    # https://stackoverflow.com/a/49361727/4723940
    # 2**10 = 1024
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " days, ") if days else "") + \
          ((str(hours) + " hours, ") if hours else "") + \
          ((str(minutes) + " min, ") if minutes else "") + \
          ((str(seconds) + " sec, ") if seconds else "") + \
          ((str(milliseconds) + " millisec, ") if milliseconds else "")
    return tmp[:-2]
