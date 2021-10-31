# (c) @AbirHasan2005

import shutil
import aiofiles.os
from configs import Config


async def rm_dir(root: str = f"{Config.DOWNLOAD_DIR}"):
    """
    Delete a Folder.

    :param root: Pass DIR Path
    """

    try:
        shutil.rmtree(root)
    except Exception as e:
        Config.LOGGER.getLogger(__name__).error(e)


async def rm_file(file_path: str):
    """
    Delete a File.

    :param file_path: Pass File Path
    """
    try:
        await aiofiles.os.remove(file_path)
    except:
        pass
