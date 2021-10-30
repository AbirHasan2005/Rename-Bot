# (c) @AbirHasan2005

import json
import subprocess


async def get_video_info(filename):
    result = subprocess.check_output(
            f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
            shell=True).decode()
    fields = json.loads(result)['streams'][0]
    return fields['duration'], fields['height'], fields['width']
