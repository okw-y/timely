import asyncio
import winsdk.windows.media.control as wmc


async def getMediaSession() -> wmc.GlobalSystemMediaTransportControlsSession:
    sessions = await wmc.GlobalSystemMediaTransportControlsSessionManager.request_async()

    return sessions.get_current_session()


def mediaIsPlaying() -> bool:
    session = asyncio.run(getMediaSession())
    if session is None:
        return False

    return session.get_playback_info().playback_status == 4
