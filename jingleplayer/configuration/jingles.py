import logging
import pathlib
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum, auto

import humanize

from jingleplayer import util

from .actions import (
    ActionGroup,
    DelayAction,
    PausePlaybackAction,
    PlayJingleAction,
    ResumePlaybackAction,
    parse_action_group_str,
)

logger = logging.getLogger(__name__)


class JingleTrigger(StrEnum):
    GAME_START = auto()
    GAME_END = auto()

    def description_str(self):
        match self:
            case JingleTrigger.GAME_START:
                return "start of each game"
            case JingleTrigger.GAME_END:
                return "end of each game"


@dataclass
class Jingle:
    name: str

    trigger: JingleTrigger
    offset: timedelta

    pre_actions: ActionGroup
    actions: ActionGroup

    audiofile: pathlib.Path | None = None

    def __post_init__(self):
        self.has_playjingle_action = (self.pre_actions.includes(PlayJingleAction)) or (
            self.actions.includes(PlayJingleAction)
        )

        if self.audiofile:
            if not self.audiofile.is_file():
                raise RuntimeError(
                    f'Jingle file "{self.audiofile}" does not exist or is not a file.'
                )

            self.audio_duration = util.get_audiofile_duration(self.audiofile)

        if self.has_playjingle_action and not self.audiofile:
            raise ValueError(
                "If pre_action, action, or post_action is or includes play_jingle, an audio file must be set."
            )

    def get_info_str(self):
        lines = util.get_info_string_header("Jingle", self.name)

        offset_str = util.get_human_timedelta_string(self.offset)
        lines.append(f"- Trigger: {offset_str} the {self.trigger.description_str()}")

        if self.audiofile:
            assert self.audio_duration
            dur = humanize.precisedelta(self.audio_duration)
            lines.append(f'- File to play: "{self.audiofile}" (duration: {dur})')

            if not self.has_playjingle_action:
                lines.append(
                    '- NOTE: audio file is configured, but will never play because no "play jingle" action is configured'
                )
        elif self.has_playjingle_action:
            lines.append(
                '- WARNING: "play jingle" action is configured, but no audio file is configured for this jingle!'
            )

        lines.append(f"- Before trigger: {self.pre_actions.get_description_str()}")
        lines.append(f"- At trigger time: {self.actions.get_description_str()}")

        return util.lines_to_string(lines)

    @classmethod
    def from_json_obj(
        cls, name: str, obj, root_dir: pathlib.Path, default_delay: timedelta
    ):
        # Trigger
        trigger = JingleTrigger[obj["trigger"].upper()]

        # Offset
        if offset_str := obj.get("offset", None):
            offset = util.parse_timedelta_str(offset_str)
        else:
            offset = timedelta(0)

        # Audio file
        if filename := obj.get("audio_file", None):
            audiofile = root_dir / pathlib.Path(filename)
            logger.info(f'Filename "{filename}" resolves to "{audiofile.resolve()}"')
        else:
            audiofile = None

        # Actions
        if pre_action_str := obj.get("pre_actions", None):
            pre_actions = parse_action_group_str(pre_action_str)
        else:
            pre_actions = ActionGroup(
                [PausePlaybackAction(), DelayAction(default_delay)]
            )

        if action_str := obj.get("actions", None):
            actions = parse_action_group_str(action_str)
        else:
            actions = ActionGroup(
                [PlayJingleAction(), DelayAction(default_delay), ResumePlaybackAction()]
            )

        # finalize
        j = cls(
            name=name,
            trigger=trigger,
            offset=offset,
            pre_actions=pre_actions,
            actions=actions,
            audiofile=audiofile,
        )

        return j
