# (c) @AbirHasan2005

import os
import sys
import bot
import shutil
from pyrogram import idle
from configs import Config
from sqlite3 import OperationalError

def run_bot():
    bot.bot.start()
    idle()


def rm_st():
    try: shutil.rmtree(Config.DOWNLOAD_DIR)
    except: pass
    try: os.remove("RenameBot.session")
    except: pass
    try: os.remove("RenameBot.session-journal")
    except: pass


if __name__ == "__main__":
    try:
        run_bot()
        bot.bot.stop()
    except OperationalError:
        try: bot.bot.stop()
        except: pass
        rm_st()
        os.execl(sys.executable, sys.executable, *sys.argv)
