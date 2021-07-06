# (c) @AbirHasan2005

import os
import shutil


async def delete_all(root: str):
    """
    Delete a Folder.

    :param root: Pass Folder Path as String.
    """

    try:
        shutil.rmtree(root)
    except Exception as e:
        print(e)


async def delete_one(file: str):
    """
    Try to Delete a Specific File.

    :param file: Pass File Path.
    """

    try:
        os.remove(file)
    except:
        pass
