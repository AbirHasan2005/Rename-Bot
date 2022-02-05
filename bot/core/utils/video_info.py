# (c) @AbirHasan2005

import json
import asyncio
import subprocess


def convert_sexagesimal_to_sec(text):
    if isinstance(text, float):
        num = str(text)
        nums = num.split('.')
    else:
        nums = text.split(':')
    if len(nums) == 2:
        st_sn = int(nums[0]) * 60 + float(nums[1])
        return st_sn
    elif len(nums) == 3:
        st_sn = int(nums[0]) * 3600 + int(nums[1]) * 60 + float(nums[2])
        return st_sn
    else:
        return 0


async def get_video_info(filename):
    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
    fields = json.loads(result)['streams'][0]
    return fields['duration'], fields['height'], fields['width']


async def get_audio_or_video_duration(path: str, provider: str = "ffprobe"):
    duration = 0
    if provider == "ffprobe":
        process = await asyncio.create_subprocess_shell(
            f"ffprobe -v quiet -print_format json -show_format -show_streams '{path}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stdout = stdout.decode('utf-8', 'replace').strip()
        stderr = stderr.decode('utf-8', 'replace').strip()
        if not stdout:
            duration = 0
        else:
            try:
                json_data = json.loads(stdout)
                stream_tags = json_data.get('streams')[0].get('tags')
                duration = int(convert_sexagesimal_to_sec(stream_tags.get('DURATION')))
            except:
                duration = 0
    if (provider == "mediainfo") or (not duration):
        process = await asyncio.create_subprocess_shell(
            f'mediainfo --Inform="General;%Duration%" "{path}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stdout = stdout.decode('utf-8', 'replace').strip()
        stderr = stderr.decode('utf-8', 'replace').strip()
        if not stdout:
            duration = 0
        else:
            try:
                duration = int(int(stdout) / 1000)
            except: pass
    return duration


async def get_video_height(path: str):
    process = await asyncio.create_subprocess_shell(
        f"ffprobe -v quiet -print_format json -show_format -show_streams '{path}'",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode('utf-8', 'replace').strip()
    stderr = stderr.decode('utf-8', 'replace').strip()
    if not stdout:
        return 0
    try:
        json_data = json.loads(stdout)
        height = json_data.get('streams')[0].get('height')
        return height or 0
    except: return 0


async def get_video_width(path: str):
    process = await asyncio.create_subprocess_shell(
        f"ffprobe -v quiet -print_format json -show_format -show_streams '{path}'",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    stdout = stdout.decode('utf-8', 'replace').strip()
    stderr = stderr.decode('utf-8', 'replace').strip()
    if not stdout:
        return 0
    try:
        json_data = json.loads(stdout)
        width = json_data.get('streams')[0].get('width')
        return width or 0
    except: return 0
