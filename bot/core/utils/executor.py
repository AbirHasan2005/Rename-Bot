# (c) @AbirHasan2005

import shlex
import asyncio
from typing import Tuple


async def execute(cmnd: str) -> Tuple[str, str, int, int]:
    """
    Execute a Command as Async.

    :param cmnd: Pass Command as String.
    """

    cmnds = shlex.split(cmnd)
    process = await asyncio.create_subprocess_exec(
        *cmnds,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (stdout.decode('utf-8', 'replace').strip(),
            stderr.decode('utf-8', 'replace').strip(),
            process.returncode,
            process.pid)
