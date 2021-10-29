# (c) @AbirHasan2005

from typing import Union
from pyromod import listen
from pyrogram import Client as RawClient
from pyrogram.storage import Storage
from configs import Config
from bot.core.new import New

LOGGER = Config.LOGGER
log = LOGGER.getLogger(__name__)


class Client(RawClient, New):
    """ Custom Bot Class """

    def __init__(self, session_name: Union[str, Storage] = "RenameBot"):
        super().__init__(
            session_name,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(
                root="bot/plugins"
            )
        )

    async def start(self):
        await super().start()
        log.info("Bot Started!")

    async def stop(self, *args):
        await super().stop()
        log.info("Bot Stopped!")
