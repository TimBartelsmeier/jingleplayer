import abc
import logging
from datetime import timedelta

import humanize

from jingleplayer import util

logger = logging.getLogger(__name__)


# region Action Classes
class ActionBase(abc.ABC):
    @abc.abstractmethod
    def get_description_str(self) -> str:
        pass


class NothingAction(ActionBase):
    def get_description_str(self):
        return "do nothing"


class DelayAction(ActionBase):
    def __init__(self, duration: timedelta):
        super().__init__()

        if duration < util.ZERO_TD:
            raise ValueError("Delay must be positive (or 0)")

        self.duration = duration

    def get_description_str(self):
        return f"wait {humanize.precisedelta(self.duration)}"


class PausePlaybackAction(ActionBase):
    def get_description_str(self):
        return "pause playback"


class ResumePlaybackAction(ActionBase):
    def get_description_str(self):
        return "resume playback"


class PlayJingleAction(ActionBase):
    def get_description_str(self):
        return "play jingle"


class AnnounceGameAction(ActionBase):
    def get_description_str(self):
        return "announce game"


class SwitchToGamePlaylistAction(ActionBase):
    def get_description_str(self):
        return "switch to game playlist"


class AnnounceGamePlaylistAction(ActionBase):
    def get_description_str(self):
        return "announce game playlist"


type Action = (
    NothingAction
    | DelayAction
    | PausePlaybackAction
    | ResumePlaybackAction
    | PlayJingleAction
    | AnnounceGameAction
    | SwitchToGamePlaylistAction
    | AnnounceGamePlaylistAction
)


class ActionGroup(ActionBase):
    def __init__(self, actions: list[Action]) -> None:
        super().__init__()
        self.actions = actions

    def get_description_str(self):
        return " -> ".join((a.get_description_str() for a in self.actions))

    def includes(self, action_type: type[Action]):
        return any((isinstance(child, action_type) for child in self.actions))


# endregion


# region parsing
def parse_action_str(s: str) -> Action:
    match s.strip():
        case "nothing" | "" | "do nothing":
            return NothingAction()

        case s if s.startswith("delay") or s.startswith("wait"):
            s = s.removeprefix("delay")
            s = s.removeprefix("wait")
            s = s.strip()

            try:
                return DelayAction(util.parse_timedelta_str(s))
            except Exception as e:
                raise ValueError(f'Invalid delay specification "{s}"') from e

        case "pause playback":
            return PausePlaybackAction()

        case "resume playback":
            return ResumePlaybackAction()

        case "play jingle":
            return PlayJingleAction()

        case "announce game":
            return AnnounceGameAction()

        case "switch to game playlist":
            return SwitchToGamePlaylistAction()

        case "announce game playlist":
            return AnnounceGamePlaylistAction()

        case _:
            raise ValueError(f'Unknown action specification: "{s}"')


def parse_action_group_str(s: str) -> ActionGroup:
    sub_strs = s.split(";")

    return ActionGroup([parse_action_str(sub_str) for sub_str in sub_strs])


# endregion
