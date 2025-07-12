from collections.abc import Iterable
from datetime import timedelta
from functools import reduce

from jingleplayer import util
from jingleplayer.configuration import (
    Action,
    ActionGroup,
    Game,
    Jingle,
)
from jingleplayer.configuration.actions import (
    AnnounceGameAction,
    DelayAction,
    NothingAction,
    PausePlaybackAction,
    PlayJingleAction,
    ResumePlaybackAction,
    SwitchToGamePlaylistAction,
)
from jingleplayer.playback_control import (
    PlaybackController,
    SpotifyDbusPlaybackController,
)


def get_action_duration(
    action: Action,
    jingle: Jingle,
    game: Game,
) -> timedelta:
    match action:
        case NothingAction() | PausePlaybackAction() | ResumePlaybackAction():
            return timedelta(0)

        case DelayAction():
            return action.duration

        case PlayJingleAction():
            if dur := jingle.audio_duration:
                return dur

            return timedelta(0)

        case AnnounceGameAction():
            if dur := game.announcement_duration:
                return dur
            else:
                return timedelta(0)

        case SwitchToGamePlaylistAction():
            return timedelta(0)

        case AnnounceGameAction():
            if (pl := game.playlist) and (dur := pl.announcement_duration):
                return dur

            return timedelta(0)

        case _:
            raise TypeError("Unknown action type")


def get_actiongroup_duration(
    actiongroup: ActionGroup,
    jingle: Jingle,
    game: Game,
) -> timedelta:
    return reduce(
        lambda acc, a: acc + get_action_duration(a, jingle, game),
        actiongroup.actions,
        timedelta(0),
    )


def execute_action(
    action: Action,
    jingle: Jingle,
    game: Game,
    playback_controllers: Iterable[PlaybackController],
):
    match action:
        case NothingAction():
            pass

        case DelayAction():
            util.wait_for(action.duration.total_seconds())

        case PausePlaybackAction():
            for pc in playback_controllers:
                pc.pause()

        case ResumePlaybackAction():
            for pc in playback_controllers:
                pc.resume()

        case PlayJingleAction():
            if jingle.audiofile:
                assert jingle.audiofile
                util.play_audiofile(jingle.audiofile)

        case AnnounceGameAction():
            if f := game.announcement_file:
                util.play_audiofile(f)

        case SwitchToGamePlaylistAction():
            for pc in playback_controllers:
                if not isinstance(pc, SpotifyDbusPlaybackController):
                    continue

                if pl := game.playlist:
                    pc.open_uri(pl.uri)

        case AnnounceGameAction():
            if (pl := game.playlist) and (af := pl.announcement_file):
                util.play_audiofile(af)

        case _:
            raise TypeError("Unknown action type")


def execute_actiongroup(
    actiongroup: ActionGroup,
    jingle: Jingle,
    game: Game,
    playback_controllers: Iterable[PlaybackController],
    skip_trailing_delay: bool = True,
):
    trail_idx = len(actiongroup.actions) - 1

    for idx, action in enumerate(actiongroup.actions):
        if skip_trailing_delay and idx == trail_idx and isinstance(action, DelayAction):
            break

        execute_action(action, jingle, game, playback_controllers)
