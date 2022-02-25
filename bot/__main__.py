# (c) @AbirHasan2005

import os
import sys
import bot
import shutil
import asyncio
from pyrogram import idle
from configs import Config
from sqlite3 import OperationalError


def rm_st():
    try: shutil.rmtree(Config.DOWNLOAD_DIR)
    except: pass
    try: os.remove("RenameBot.session")
    except: pass
    try: os.remove("RenameBot.session-journal")
    except: pass


def run_bot():
    async def runner():
        await bot.bot.start()
        await idle()
        await bot.bot.stop()

    rm_st()
    asyncio.get_event_loop().run_until_complete(runner())


if __name__ == "__main__":
    try:
        run_bot()
    except OperationalError:
        rm_st()
        os.execl(sys.executable, sys.executable, *sys.argv)
