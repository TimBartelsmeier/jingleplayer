import argparse
import logging
import pathlib
import sys

from jingleplayer import execution, playback_control, testing
from jingleplayer.configuration import Config
from jingleplayer.playback_control.controllers import SpotifyDbusPlaybackController


# region parse args, set up logging
def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "configfile",
        type=str,
        help="Path to the config file that should be loaded.",
    )

    parser.add_argument(
        "--playback_controller",
        "-p",
        type=str,
        choices=["dummy", "key", "spotify_dbus"],
        nargs="*",
        help="Which control mechanism(s) to use to pause/resume music playback. To specify multiple, separate them with spaces.",
    )

    parser.add_argument(
        "--info",
        "-i",
        action="store_true",
        help="Show information about the provided configuration; i.e. list all games, jingles, and playlists in the specified configuration and how they are set up.",
    )

    parser.add_argument(
        "--testaudio",
        "-ta",
        action="store_true",
        help='Shows the same information as --info and, in addition, plays all configured audio files (jingles, game/playlist announcements). You can use this to test whether they are set up correctly (correct files, matching volume, ...). After each audio file, there will be a short delay to ensure the files don\'t "blend into each other".',
    )

    parser.add_argument(
        "--testplaybackcontrol",
        "-tpc",
        action="store_true",
        help="Starts and pauses music playback using the playback controllers configured with --playback_controllers (or -p). You can use this to test whether playback control works as expected. The playback controllers are used in succession and there is a short delay between starting and pausing playback and before testing the next controller.",
    )

    parser.add_argument(
        "--test",
        "-t",
        action="store_true",
        help="Has the same effect as passing --testaudio and --testplaybackcontrol.",
    )

    parser.add_argument(
        "--logfile",
        type=str,
        help="File to log to. If it already exists, it is overwritten. If not set, no log will be created.",
    )
    parser.add_argument(
        "--loglevel",
        type=str,
        choices=["debug", "info", "warn", "error"],
        default="warn",
        help="Minimum log level of messages that are output to LOGFILE. If LOGFILE is not set, does nothing. Default is warn.",
    )

    return parser.parse_args()


def _setup_logging(args: argparse.Namespace):
    if args.logfile:
        file = pathlib.Path(args.logfile)
        if file.is_dir():
            raise RuntimeError(
                f'Specified path for logfile ("{args.logfile}") is an existing directory.'
            )
        file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=args.loglevel.upper(),
            format="%(asctime)s %(levelname)s: %(message)s",
            filename=str(file.resolve()),
            filemode="w",
        )
    else:
        logging.basicConfig(handlers=[logging.NullHandler()])


args = _parse_args()

_setup_logging(args)
logger = logging.getLogger(__name__)
logger.debug("Logging set up")

# endregion


# Load config
try:
    cfg = Config.load(args.configfile)
except Exception as exc:
    logger.exception("Exception occured while loading/parsing config:")

    print(
        "There was an unexpected problem while loading the config file, which is most likely caused by an invalid format or invalid values. See the following message for more information."
    )
    print(str(exc))

    sys.exit(1)


# Set up playback controllers
try:
    playback_controllers = playback_control.setup_from_cli(args.playback_controller)

    if cfg.needs_playback_control and len(playback_controllers) == 0:
        s = 'The loaded configuration has playback control actions configured (e.g. "resume playback" or "pause playback"), but no playback controllers are set and playback will not be controlled. See --help for how to configure playback controllers.'

        logger.warning(s)
        print("WARNING: " + s)
        print()

    if cfg.needs_spotify_dbus and not any(
        isinstance(pc, SpotifyDbusPlaybackController) for pc in playback_controllers
    ):
        s = 'The loaded configuration has a switch playlist action configured. This only works with "-p spotify_dbus", which is not passed. Playlist control will not be available. Note that this is only available on linux systems and requires the sdbus package to be installed.'

        logger.warning(s)
        print("WARNING: " + s)
        print()

except Exception as exc:
    logger.exception("Exception occured while parsing --playback_controller option:")

    print(
        "There was an unexpected problem while parsing the --playback_controller option. The following message might be helpful. You can also enable logging using --logfile and --loglevel (see --help)."
    )
    print(str(exc))

    sys.exit(1)


# Main
try:
    do_info = args.info
    do_ta = args.test or args.testaudio
    do_tpc = args.test or args.testplaybackcontrol
    do_any_test = do_info or do_ta or do_tpc

    if do_ta:
        testing.test_config(cfg, True)
        print()
        print()
    elif do_info:
        testing.test_config(cfg, False)
        print()
        print()

    if do_tpc:
        testing.test_playbackcontrol(playback_controllers)

    if not do_any_test:
        execution.schedule_and_run_jingles(cfg, playback_controllers)
        print("No jingles left to play. Exiting program.")

except Exception as exc:
    logger.exception("Exception occured:")

    print(
        "There was an unexpected problem. The following message might be helpful. You can also enable logging using --logfile and --loglevel (see --help)."
    )
    print(str(exc))

    sys.exit(1)
