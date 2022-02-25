# (c) @AbirHasan2005

import os
import time
import json
import shlex
import shutil
from bot.client import (
    Client
)
from configs import Config
from pyrogram import filters
from pyrogram.types import Message
from bot.core.file_info import (
    get_media_file_name
)
from bot.core.db.database import db
from bot.core.utils.rm import rm_dir
from bot.core.utils.executor import execute
from bot.core.db.add import add_user_to_database
from bot.core.display import progress_for_pyrogram
from bot.core.file_info import get_file_attr


def filesystem_free(path='.'):
    _, __, free = shutil.disk_usage(".")
    return free


@Client.on_message(filters.command("video_info") & filters.private & ~filters.edited)
async def video_info_handler(c: Client, m: Message):
    await add_user_to_database(c, m)
    if filesystem_free() < 5000000000:
        return await m.reply_text(
            "Because of less server space I can't do this task right now !!\n\n"
            "Please try again after some time or use @AHToolsBot to do same task.",
            True
        )
    if (not m.reply_to_message) or (len(m.command) == 1):
        await m.reply_text(f"Reply to video with,\n/{m.command[0]} `--change-title` new title `--change-video-title` new video title `--change-audio-title` new audio title `--change-subtitle-title` new subtitle title `--change-file-name` new file name", True)
        return
    title = None
    video_title = None
    audio_title = None
    subtitle_title = None
    default_f_name = get_media_file_name(m.reply_to_message)
    new_file_name = f"{default_f_name.rsplit('.', 1)[0] if default_f_name else 'output'}.mkv"
    if len(m.command) <= 1:
        return

    flags = [i.strip() for i in m.text.split('--')]
    for f in flags:
        if "change-file-name" in f:
            new_file_name = f[len("change-file-name"):].strip().rsplit(".", 1)[0] + ".mkv"
        if "change-title" in f:
            title = f[len("change-title"):].strip()
        if "change-video-title" in f:
            video_title = f[len("change-video-title"):].strip()
        if "change-audio-title" in f:
            audio_title = f[len("change-audio-title"):].strip()
        if "change-subtitle-title" in f:
            subtitle_title = f[len("change-subtitle-title"):].strip()
    file_type = m.reply_to_message.video or m.reply_to_message.document
    if not file_type.mime_type.startswith("video/"):
        await m.reply_text("This is not a Video!", True)
        return
    editable = await m.reply_text("Downloading Video ...", quote=True)
    dl_loc = Config.DOWNLOAD_DIR + "/" + str(m.from_user.id) + "/" + str(m.message_id) + "/"
    root_dl_loc = dl_loc
    if not os.path.isdir(dl_loc):
        os.makedirs(dl_loc)
    c_time = time.time()
    the_media = await c.download_media(
        message=m.reply_to_message,
        file_name=dl_loc,
        progress=progress_for_pyrogram,
        progress_args=(
            "Downloading ...",
            editable,
            c_time
        )
    )
    await editable.edit("Trying to Fetch Media Metadata ...")
    output = await execute(f"ffprobe -hide_banner -show_streams -print_format json {shlex.quote(the_media)}")
    if not output:
        await rm_dir(root_dl_loc)
        return await editable.edit("Can't fetch media info!")

    try:
        details = json.loads(output[0])
        middle_cmd = f"ffmpeg -i {shlex.quote(the_media)} -c copy -map 0"
        if title:
            middle_cmd += f' -metadata title="{title}"'
        for stream in details["streams"]:
            if (stream["codec_type"] == "video") and video_title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{video_title}"'
            elif (stream["codec_type"] == "audio") and audio_title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{audio_title}"'
            elif (stream["codec_type"] == "subtitle") and subtitle_title:
                middle_cmd += f' -metadata:s:{stream["index"]} title="{subtitle_title}"'
        dl_loc = dl_loc + str(time.time()).replace(".", "") + "/"
        if not os.path.isdir(dl_loc):
            os.makedirs(dl_loc)
        middle_cmd += f" {shlex.quote(dl_loc + new_file_name)}"
        await editable.edit("Please Wait ...\n\nProcessing Video ...")
        await execute(middle_cmd)
        await editable.edit("Renamed Successfully!")
    except:
        # Clean Up
        await editable.edit("Failed to process video!")
        await rm_dir(root_dl_loc)
        return
    try: os.remove(the_media)
    except: pass
    upload_as_doc = await db.get_upload_as_doc(m.from_user.id)
    _default_thumb_ = await db.get_thumbnail(m.from_user.id)
    if not _default_thumb_:
        _m_attr = get_file_attr(m.reply_to_message)
        _default_thumb_ = _m_attr.thumbs[0].file_id \
            if (_m_attr and _m_attr.thumbs) \
            else None
    if _default_thumb_:
        _default_thumb_ = await c.download_media(_default_thumb_, root_dl_loc)
    if (not upload_as_doc) and m.reply_to_message.video:
        await c.upload_video(
            chat_id=m.chat.id,
            video=f"{dl_loc}{new_file_name}",
            thumb=_default_thumb_ or None,
            editable_message=editable,
        )
    else:
        await c.upload_document(
            chat_id=m.chat.id,
            document=f"{dl_loc}{new_file_name}",
            editable_message=editable,
            thumb=_default_thumb_ or None
        )
    await rm_dir(root_dl_loc)
