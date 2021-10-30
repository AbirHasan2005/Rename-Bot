# (c) @AbirHasan2005

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


async def get_thumbnail_info(thumb_path: str):
    try:
        metadata = extractMetadata(createParser(thumb_path))
    except: return 0, 0
    try:
        if metadata.has("height"):
            height = metadata.get("height")
        else:
            height = 0
    except:
        height = 0
    try:
        if metadata.has("width"):
            width = metadata.get("width")
        else:
            width = 0
    except:
        width = 0

    return height, width
