# (c) @AbirHasan2005

import shutil
from os import (
    PathLike,
    remove
)
from typing import Union
from configs import Config


async def rm_dir(root: Union[PathLike[str], str] = f"{Config.DOWNLOAD_DIR}"):
    """
    Delete a Folder.

    :param root: Pass DIR Path
    """

    try:
        shutil.rmtree(root)
    except Exception as e:
        Config.LOGGER.getLogger(__name__).error(e)


async def rm_file(file_path: PathLike):
    """
    Delete a File.

    :param file_path: Pass File Path
    """
    remove(file_path)
