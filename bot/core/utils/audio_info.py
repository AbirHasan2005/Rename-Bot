# (c) @AbirHasan2005

from mutagen import mp3, wave, aac


async def get_audio_info(audio_path: str):
    file_ext = audio_path.rsplit(".", 1)[-1].upper()
    if file_ext not in ["MP3", "WAVE", "AAC"]:
        return 0
    if file_ext == "MP3":
        audio = mp3.MP3(audio_path)
        return audio.info.length
    if file_ext == "WAVE":
        audio = wave.WAVE(audio_path)
        return audio.info.length
    if file_ext == "AAC":
        audio = aac.AAC(audio_path)
        return audio.info.length
