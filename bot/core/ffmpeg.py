# (c) @AbirHasan2005

import os
import time
import asyncio
from typing import Optional


async def take_screen_shot(video_file, output_directory, ttl) -> Optional[str]:
    """
    Take Screenshot from Video.

    Source: https://stackoverflow.com/a/13891070/4723940

    :param video_file: Pass Video File Path.
    :param output_directory: Pass output folder path for screenshot. If folders not exists, this will create folders.
    :param ttl: Time!

    :return: This will return screenshot image path.
    """

    output_dir = f'{output_directory}/{time.time()}/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filepath = output_dir + "thumbnail.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        output_filepath
    ]
    # width = "90"
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    return output_filepath if os.path.lexists(output_filepath) else None
