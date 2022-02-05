# (c) @AbirHasan2005

from .normal_rename import NormalRename
from .custom_uploader import CustomUploader
from .upload_video import UploadVideo
from .upload_document import UploadDocument
from .send_flooded_message import SendFloodedMessage


class New(
    NormalRename,
    CustomUploader,
    SendFloodedMessage,
    UploadVideo,
    UploadDocument
):
    """ New Methods for Pyrogram """
