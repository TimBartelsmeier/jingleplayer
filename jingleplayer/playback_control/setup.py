import logging
import platform

from .controllers import (
    DummyPlaybackController,
    PlaybackController,
    PlayPauseKeyPlaybackController,
    SpotifyDbusPlaybackController,
)

logger = logging.getLogger(__name__)

# region check sdbus availability
SDBUS_AVAILABLE = False
if platform.system() == "Linux":
    logger.debug("Platform is Linux, checking if sdbus is available")

    import importlib.util

    if importlib.util.find_spec("sdbus"):
        SDBUS_AVAILABLE = True
        logger.debug("sdbus is available")
# endregion


def _get_playbackcontroller(pc_str: str) -> PlaybackController:
    match pc_str:
        case "dummy":
            return DummyPlaybackController()
        case "key":
            return PlayPauseKeyPlaybackController()
        case "spotify_dbus":
            if not SDBUS_AVAILABLE:
                raise RuntimeError(
                    "SpotifyDbusPlaybackController is only available on linux systems and requires the sdbus library to be installed."
                )
            else:
                return SpotifyDbusPlaybackController()
        case _:
            raise ValueError(f"Unknown playback controller option: {pc_str}")


def setup_from_cli(cli_options: list[str] | None) -> list[PlaybackController]:
    logger.debug("Setting up playback controllers based on CLI options")

    if cli_options is None or len(cli_options) == 0:
        return []

    pcs: list[PlaybackController] = []
    for s in set(cli_options):
        pc = _get_playbackcontroller(s)
        logger.debug(f'CLI option "{s}" parsed to PlaybackController {pc}')
        pcs.append(pc)

    return pcs
