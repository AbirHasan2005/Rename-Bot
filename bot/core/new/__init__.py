# (c) @AbirHasan2005

from .normal_rename import NormalRename
from .custom_uploader import CustomUploader
from .send_flooded_message import SendFloodedMessage


class New(NormalRename, CustomUploader, SendFloodedMessage):
    """ New Methods for Pyrogram """
