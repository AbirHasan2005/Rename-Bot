import time
from configs import Config

GAP = {}


async def CheckTimeGap(user_id: int, rm_gap: bool = None):
    """A Function for checking user time gap!

    :parameter user_id: Telegram User ID.
    :parameter rm_gap: Force Remove User from Time Gap.
    :return: This will return True with Left Time if User in Time Gap and will return False if User not in Time Gap.
    """

    if Config.ONE_PROCESS_ONLY is False:
        if str(user_id) in GAP:
            current_time = time.time()
            previous_time = GAP[str(user_id)]
            if round(current_time - previous_time) < Config.SLEEP_TIME:
                return True, round(previous_time - current_time + Config.SLEEP_TIME)
            elif round(current_time - previous_time) >= Config.SLEEP_TIME:
                del GAP[str(user_id)]
                return False, None
        elif str(user_id) not in GAP:
            GAP[str(user_id)] = time.time()
            return False, None
    else:
        if rm_gap is not None:
            del GAP[str(user_id)]
            return True, None
        if str(user_id) not in GAP:
            GAP[str(user_id)] = True
        else:
            return True, "Only One Process Please!"
