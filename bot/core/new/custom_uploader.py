# (c) @AbirHasan2005 & @subinps
# Bruh!
# Took a huge time to make this script.
# So Plis,
# !! Don't Copy without credits !!

# Some Parts Copied from:
# https://github.com/pyrogram/pyrogram/blob/master/pyrogram/methods/advanced/save_file.py
# https://github.com/pyrogram/pyrogram/blob/master/pyrogram/methods/messages/send_video.py
# https://github.com/pyrogram/pyrogram/blob/master/pyrogram/methods/messages/send_audio.py
# https://github.com/pyrogram/pyrogram/blob/master/pyrogram/methods/messages/send_document.py

import os
import io
import math
import inspect
import asyncio
import functools
from configs import Config
from hashlib import sha256, md5
from pyrogram.crypto import aes
from pyrogram import raw
from pyrogram import utils
from pyrogram import StopTransmission
from pyrogram.errors import (
    AuthBytesInvalid,
    VolumeLocNotFound
)
from pyrogram.file_id import (
    FileId,
    FileType,
    ThumbnailSource
)
from pyrogram.session import (
    Auth,
    Session
)
from pyrogram.scaffold import Scaffold

LOGGER = Config.LOGGER
log = LOGGER.getLogger(__name__)


class CustomUploader(Scaffold):
    async def custom_upload(
        self,
        file_id: FileId,
        file_size: int,
        file_name: str,
        progress: callable,
        progress_args: tuple = ()
    ):
        dc_id = file_id.dc_id

        async with self.media_sessions_lock:
            session = self.media_sessions.get(dc_id, None)

            if session is None:
                if dc_id != await self.storage.dc_id():
                    session = Session(
                        self, dc_id, await Auth(self, dc_id, await self.storage.test_mode()).create(),
                        await self.storage.test_mode(), is_media=True
                    )
                    await session.start()

                    for _ in range(3):
                        exported_auth = await self.send(
                            raw.functions.auth.ExportAuthorization(
                                dc_id=dc_id
                            )
                        )

                        try:
                            await session.send(
                                raw.functions.auth.ImportAuthorization(
                                    id=exported_auth.id,
                                    bytes=exported_auth.bytes
                                )
                            )
                        except AuthBytesInvalid:
                            continue
                        else:
                            break
                    else:
                        await session.stop()
                        raise AuthBytesInvalid
                else:
                    session = Session(
                        self, dc_id, await self.storage.auth_key(),
                        await self.storage.test_mode(), is_media=True
                    )
                    await session.start()

                self.media_sessions[dc_id] = session

        async def worker(session):
            while True:
                data = await queue.get()

                if data is None:
                    return

                try:
                    await self.loop.create_task(session.send(data))
                except Exception as e:
                    log.error(e)

        file_type = file_id.file_type

        if file_type == FileType.CHAT_PHOTO:
            if file_id.chat_id > 0:
                peer = raw.types.InputPeerUser(
                    user_id=file_id.chat_id,
                    access_hash=file_id.chat_access_hash
                )
            else:
                if file_id.chat_access_hash == 0:
                    peer = raw.types.InputPeerChat(
                        chat_id=-file_id.chat_id
                    )
                else:
                    peer = raw.types.InputPeerChannel(
                        channel_id=utils.get_channel_id(file_id.chat_id),
                        access_hash=file_id.chat_access_hash
                    )

            location = raw.types.InputPeerPhotoFileLocation(
                peer=peer,
                volume_id=file_id.volume_id,
                local_id=file_id.local_id,
                big=file_id.thumbnail_source == ThumbnailSource.CHAT_PHOTO_BIG
            )
        elif file_type == FileType.PHOTO:
            location = raw.types.InputPhotoFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size
            )
        else:
            location = raw.types.InputDocumentFileLocation(
                id=file_id.media_id,
                access_hash=file_id.access_hash,
                file_reference=file_id.file_reference,
                thumb_size=file_id.thumbnail_size
            )
        part_size = 512 * 1024

        limit = 1024 * 1024
        _n_file_id = None
        file_id_ = None
        file_part = 0
        offset = 0
        file_total_parts = int(math.ceil(file_size / part_size))
        is_big = file_size > 10 * 1024 * 1024
        pool_size = 3 if is_big else 1
        workers_count = 4 if is_big else 1

        pool = [
            Session(
                self, await self.storage.dc_id(), await self.storage.auth_key(),
                await self.storage.test_mode(), is_media=True
            ) for _ in range(pool_size)
        ]
        workers = [self.loop.create_task(worker(session_)) for session_ in pool for _ in range(workers_count)]
        queue = asyncio.Queue(16)

        try:
            for session_ in pool:
                await session_.start()

            try:
                r = await session.send(
                    raw.functions.upload.GetFile(
                        location=location,
                        offset=offset,
                        limit=limit
                    ),
                    sleep_threshold=30
                )

                if isinstance(r, raw.types.upload.File):
                    while True:
                        chunk = r.bytes
                        fp_ = chunk
                        fp = io.BytesIO(fp_)
                        fp.seek(0, os.SEEK_END)
                        file_size_ = fp.tell()
                        fp.seek(0)

                        if not chunk:
                            break

                        if file_size_ == 0:
                            raise ValueError("File size equals to 0 B")

                        if file_size_ > 2000 * 1024 * 1024:
                            raise ValueError("Telegram doesn't support uploading files bigger than 2000 MiB")

                        is_missing_part = _n_file_id is not None
                        file_id_ = file_id_ or self.rnd_id()
                        md5_sum = md5() if not is_big and not is_missing_part else None

                        with fp:
                            file_part_ = 0
                            fp.seek(part_size * file_part_)

                            while True:
                                chunk_ = fp.read(part_size)

                                if not chunk_:
                                    if not is_big and not is_missing_part:
                                        md5_sum = "".join([hex(i)[2:].zfill(2) for i in md5_sum.digest()])
                                    break

                                if is_big:
                                    rpc = raw.functions.upload.SaveBigFilePart(
                                        file_id=file_id_,
                                        file_part=file_part,
                                        file_total_parts=file_total_parts,
                                        bytes=chunk_
                                    )
                                else:
                                    rpc = raw.functions.upload.SaveFilePart(
                                        file_id=file_id_,
                                        file_part=file_part,
                                        bytes=chunk_
                                    )
                                # await session.send(rpc)

                                await queue.put(rpc)

                                if is_missing_part:
                                    return

                                if not is_big and not is_missing_part:
                                    md5_sum.update(chunk_)

                                file_part_ += 1
                                file_part += 1

                        offset += limit

                        if progress:
                            func = functools.partial(
                                progress,
                                min(offset, file_size)
                                if file_size != 0
                                else offset,
                                file_size,
                                *progress_args
                            )

                            if inspect.iscoroutinefunction(progress):
                                await func()
                            else:
                                await self.loop.run_in_executor(self.executor, func)
                        r = await session.send(
                            raw.functions.upload.GetFile(
                                location=location,
                                offset=offset,
                                limit=limit
                            ),
                            sleep_threshold=30
                        )

                elif isinstance(r, raw.types.upload.FileCdnRedirect):
                    async with self.media_sessions_lock:
                        cdn_session = self.media_sessions.get(r.dc_id, None)

                        if cdn_session is None:
                            cdn_session = Session(
                                self, r.dc_id, await Auth(self, r.dc_id, await self.storage.test_mode()).create(),
                                await self.storage.test_mode(), is_media=True, is_cdn=True
                            )

                            await cdn_session.start()

                            self.media_sessions[r.dc_id] = cdn_session

                    try:
                        while True:
                            r2 = await cdn_session.send(
                                raw.functions.upload.GetCdnFile(
                                    file_token=r.file_token,
                                    offset=offset,
                                    limit=limit
                                )
                            )

                            if isinstance(r2, raw.types.upload.CdnFileReuploadNeeded):
                                try:
                                    await session.send(
                                        raw.functions.upload.ReuploadCdnFile(
                                            file_token=r.file_token,
                                            request_token=r2.request_token
                                        )
                                    )
                                except VolumeLocNotFound:
                                    break
                                else:
                                    continue

                            chunk = r2.bytes

                            # https://core.telegram.org/cdn#decrypting-files
                            decrypted_chunk = aes.ctr256_decrypt(
                                chunk,
                                r.encryption_key,
                                bytearray(
                                    r.encryption_iv[:-4]
                                    + (offset // 16).to_bytes(4, "big")
                                )
                            )

                            hashes = await session.send(
                                raw.functions.upload.GetCdnFileHashes(
                                    file_token=r.file_token,
                                    offset=offset
                                )
                            )

                            # https://core.telegram.org/cdn#verifying-files
                            for i, h in enumerate(hashes):
                                cdn_chunk = decrypted_chunk[h.limit * i: h.limit * (i + 1)]
                                assert h.hash == sha256(cdn_chunk).digest(), f"Invalid CDN hash part {i}"

                            fp_ = decrypted_chunk
                            fp = io.BytesIO(fp_)
                            fp.seek(0, os.SEEK_END)
                            file_size_ = fp.tell()
                            fp.seek(0)

                            if not chunk:
                                break

                            if file_size_ == 0:
                                raise ValueError("File size equals to 0 B")

                            if file_size_ > 2000 * 1024 * 1024:
                                raise ValueError("Telegram doesn't support uploading files bigger than 2000 MiB")

                            is_missing_part = _n_file_id is not None
                            file_id_ = file_id_ or self.rnd_id()
                            md5_sum = md5() if not is_big and not is_missing_part else None

                            with fp:
                                file_part_ = 0
                                fp.seek(part_size * file_part_)

                                while True:
                                    chunk_ = fp.read(part_size)

                                    if not chunk_:
                                        if not is_big and not is_missing_part:
                                            md5_sum = "".join([hex(i)[2:].zfill(2) for i in md5_sum.digest()])
                                        break

                                    if is_big:
                                        rpc = raw.functions.upload.SaveBigFilePart(
                                            file_id=file_id_,
                                            file_part=file_part,
                                            file_total_parts=file_total_parts,
                                            bytes=chunk_
                                        )
                                    else:
                                        rpc = raw.functions.upload.SaveFilePart(
                                            file_id=file_id_,
                                            file_part=file_part,
                                            bytes=chunk_
                                        )
                                    # await session.send(rpc)

                                    await queue.put(rpc)

                                    if is_missing_part:
                                        return

                                    if not is_big and not is_missing_part:
                                        md5_sum.update(chunk_)

                                    file_part_ += 1
                                    file_part += 1

                            # f.write(decrypted_chunk)

                            offset += limit

                            if progress:
                                func = functools.partial(
                                    progress,
                                    min(offset, file_size)
                                    if file_size != 0
                                    else offset,
                                    file_size,
                                    *progress_args
                                )

                                if inspect.iscoroutinefunction(progress):
                                    await func()
                                else:
                                    await self.loop.run_in_executor(self.executor, func)

                            if len(chunk) < limit:
                                break
                    except Exception as e:
                        log.error(e, exc_info=True)
                        raise e
            except Exception as e:
                if not isinstance(e, StopTransmission):
                    log.error(str(e), exc_info=True)
                try:
                    os.remove(file_name)
                except OSError:
                    pass
                log.error("Error")
                return None

        except StopTransmission:
            raise
        except Exception as e:
            log.error(e, exc_info=True)
        else:
            if is_big:
                return raw.types.InputFileBig(
                    id=file_id_,
                    parts=file_total_parts,
                    name=file_name
                )
            else:
                return raw.types.InputFile(
                    id=file_id_,
                    parts=file_total_parts,
                    name=file_name,
                    md5_checksum=md5_sum
                )
        finally:
            for _ in workers:
                await queue.put(None)

            await asyncio.gather(*workers)

            for session_ in pool:
                await session_.stop()
