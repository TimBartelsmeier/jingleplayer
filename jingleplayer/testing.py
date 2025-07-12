import logging
import math
import pathlib
import shutil
from collections.abc import Iterable

from jingleplayer import util
from jingleplayer.configuration import Config
from jingleplayer.configuration.actions import (
    AnnounceGameAction,
    AnnounceGamePlaylistAction,
    SwitchToGamePlaylistAction,
)
from jingleplayer.playback_control import PlaybackController

logger = logging.getLogger(__name__)


def _playaudio_and_delay(audiofile: pathlib.Path, type: str):
    print(f"Playing {type}...")
    util.play_audiofile(audiofile)
    util.wait_for(1)


def test_config(cfg: Config, play_audio: bool):
    trmwidth, _ = shutil.get_terminal_size()
    linehalf = "-" * math.ceil(trmwidth / 2)

    has_game_announce = cfg.has_action(AnnounceGameAction)
    has_pl_announce = cfg.has_action(AnnounceGamePlaylistAction)
    has_pl_switch = cfg.has_action(SwitchToGamePlaylistAction)

    if play_audio:
        print("Config Info & Audio File Test")
    else:
        print("Config Info")
    print(linehalf)
    print()

    # Games
    print("Games:")
    print(linehalf)

    if len(cfg.games) > 0:
        print()

        for e in cfg.games.values():
            print(
                e.get_info_str(
                    warn_if_no_announcement=has_game_announce,
                    warn_if_no_playlist=has_pl_switch,
                )
            )

            if play_audio and (af := e.announcement_file):
                _playaudio_and_delay(af, "game announcement")

            print()
    else:
        print("<No games configured.>")

    print()

    # Jingles
    print("Jingles:")
    print(linehalf)

    if len(cfg.jingles) > 0:
        print()

        for j in cfg.jingles.values():
            print(j.get_info_str())

            if play_audio and (af := j.audiofile):
                _playaudio_and_delay(af, "jingle")

            print()
    else:
        print("<No jingles configured.>")

    print()

    # Playlists
    print("Playlists:")
    print(linehalf)

    if len(cfg.playlists) > 0:
        print()

        for pl in cfg.playlists.values():
            print(
                pl.get_info_str(
                    warn_if_no_announcement=has_pl_announce,
                )
            )

            if play_audio and (af := pl.announcement_file):
                _playaudio_and_delay(af, "playlist announcement")

            print()
    else:
        print("<No playlist configured.>")


def test_playbackcontrol(playback_controllers: Iterable[PlaybackController]):
    trmwidth, _ = shutil.get_terminal_size()
    linehalf = "-" * math.ceil(trmwidth / 2)

    print("Playback Controller Test")
    print(linehalf)
    print()

    if any(pc.CAN_ONLY_TOGGLE for pc in playback_controllers):
        print(
            "WARNING: At least on of the configured playback controllers can not reliably pause or resume playback, but just toggle between them. For the tesing mode, make sure that music playback is paused before you start the program and you have a suitable media player open that can be resumed/paused to check if control works."
        )
        print()

    first = True
    for pc in playback_controllers:
        if first:
            first = False
        else:
            util.wait_for(2)

        print(pc.name.capitalize())
        print("-" * len(pc.name))

        print("Starting playback ...")
        pc.resume()

        util.wait_for(2)

        print("Pausing playback ...")
        pc.pause()

        print()
