# (c) @AbirHasan2005

from .normal_rename import NormalRename
from .custom_uploader import CustomUploader


class New(NormalRename, CustomUploader):
    """ New Methods for Pyrogram """
