import datetime
import logging
from collections.abc import Iterable

import humanize

from jingleplayer import util
from jingleplayer.configuration import Config
from jingleplayer.playback_control import PlaybackController

from .actions import execute_actiongroup
from .tasks import GameJingleTask, get_tasks

logger = logging.getLogger(__name__)


def _run_task(task: GameJingleTask, pcs: Iterable[PlaybackController]):
    j = task.jingle
    e = task.game

    logger.info("Waiting for jingle pre_action trigger time")
    util.wait_until(task.start)
    execute_actiongroup(j.pre_actions, j, e, pcs)

    logger.info("Waiting for jingle trigger time")
    util.wait_until(task.action_start)
    execute_actiongroup(j.actions, j, e, pcs)


def schedule_and_run_jingles(
    cfg: Config, playback_controllers: Iterable[PlaybackController]
):
    if any(pc.CAN_ONLY_TOGGLE for pc in playback_controllers):
        print(
            "WARNING: At least one of the configured playback controllers can not reliably pause or resume playback, but just toggle between them. Make sure that music playback is running before you start the program for playback control to work properly."
        )
        print()

    logger.debug("Generating tasks")
    tasks = get_tasks(cfg)
    logger.info(f"Generated {len(tasks)} tasks")

    logger.debug("Starting scheduling loop")
    print(f"Loaded config. Scheduling {len(tasks)} jingles in total).")
    print()

    for t in tasks:
        now = datetime.datetime.now()

        if t.start < now:
            logger.info(
                f'Skipping jingle "{t.jingle.name}" for game "{t.game.name}": start time {t.start} has already passed (now: {now})'
            )
            print(
                f'Skipping jingle "{t.jingle.name}" for game "{t.game.name}": start time has already passed {humanize.naturaltime(now - t.start)}'
            )
            print()
            continue

        logger.info(f'Next: jingle "{t.jingle.name}" for game "{t.game.name}"')
        print(
            f'Next: jingle "{t.jingle.name}" for game "{t.game.name}" (trigger is in {humanize.naturaldelta(t.action_start - now)})'
        )

        _run_task(t, playback_controllers)

        print()

    logger.info("All jingles played, schedule loop exiting")
