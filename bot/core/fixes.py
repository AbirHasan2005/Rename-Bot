# (c) @AbirHasan2005

from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


async def fix_thumbnail(thumb_path: str, height: int = 0):
    if not height:
        metadata = extractMetadata(createParser(thumb_path))
        if metadata.has("height"):
            height = metadata.get("height")
        else:
            height = 0
    Image.open(thumb_path).convert("RGB").save(thumb_path)
    img = Image.open(thumb_path)
    img.resize((320, height))
    img.save(thumb_path, "JPEG")
    return thumb_path
