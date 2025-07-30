from __future__ import annotations

import itertools
import logging
import operator
from collections.abc import Sequence
from dataclasses import dataclass

import humanize

from jingleplayer.configuration import Config, Event, Jingle, JingleTrigger
from jingleplayer.util import ZERO_TD

from .actions import get_actiongroup_duration

logger = logging.getLogger(__name__)


# region base class
def _get_jingle_trigger_time(j: Jingle, e: Event):
    match j.trigger:
        case JingleTrigger.EVENT_START:
            dt = e.start
        case JingleTrigger.EVENT_END:
            dt = e.end

    return dt + j.offset


@dataclass
class EventJingleTask:
    jingle: Jingle
    event: Event

    def __post_init__(self):
        j = self.jingle
        e = self.event

        self.pre_action_duration = get_actiongroup_duration(j.pre_actions, j, e)
        self.action_duration = get_actiongroup_duration(j.actions, j, e)

        self.action_start = _get_jingle_trigger_time(j, e)
        self.start = self.action_start - self.pre_action_duration
        self.end = self.action_start + self.action_duration

        logger.info(
            f'Created EventJingleTask for event "{self.event.name}" and jingle "{self.jingle.name}". Pre_actions starts at {self.start} and takes {humanize.precisedelta(self.pre_action_duration)}. Action starts at {self.action_start} and takes {humanize.precisedelta(self.action_duration)} (until {self.end}).'
        )


# endregion


# region get tasks
class JingleOverlapError(Exception):
    def __init__(self, earlier: EventJingleTask, later: EventJingleTask):
        super().__init__(
            f'Jingle "{later.jingle.name}" for event "{later.event.name}", supposed to start at {later.start}, overlaps with jingle "{earlier.jingle.name}" for event "{earlier.event.name}", ending at {earlier.end}'
        )


def _check_for_overlaps(tasks: Sequence[EventJingleTask]):
    prev = tasks[0]
    for i in range(1, len(tasks)):
        curr = tasks[i]

        delta = curr.start - prev.end
        if delta < ZERO_TD:
            raise JingleOverlapError(prev, curr)

        prev = curr


def get_tasks(cfg: Config):
    combinations = itertools.product(cfg.events.values(), cfg.jingles.values())
    tasks = [EventJingleTask(j, e) for e, j in combinations]
    tasks.sort(key=operator.attrgetter("start", "end"))

    _check_for_overlaps(tasks)

    return tasks


# endregion
