import logging
import pathlib
import time
import typing
from datetime import datetime, timedelta

import humanize
import pause
import playsound3
import pytimeparse2
import tinytag

logger = logging.getLogger(__name__)

RELATIVE_TO_NOW_BASE = datetime.now()

# region parsing/formatting
DT_FORMAT = "%Y-%m-%d %H:%M"
DT_FORMAT_WITH_SECONDS = "%Y-%m-%d %H:%M:%S"

ZERO_TD = timedelta(0)


def parse_timedelta_str(s: str):
    td = typing.cast(  # with raise_exception and as_timedelta, return type is narrowed to timedelta
        timedelta,  # cast() call is required for static type checkers
        pytimeparse2.parse(s, raise_exception=True, as_timedelta=True),
    )

    logger.debug(f'Timedelta string "{s}" parsed to timedelta "{td}"')
    return td


def get_human_timedelta_string(td: timedelta, for_zero: str = "at"):
    if td == ZERO_TD:
        return for_zero
    elif td < ZERO_TD:
        return f"{humanize.precisedelta(td)} before"
    elif td > ZERO_TD:
        return f"{humanize.precisedelta(td)} after"
    raise RuntimeError()


def parse_datetime_str(s: str):
    try:
        val = datetime.strptime(s, DT_FORMAT)
    except ValueError as e:
        try:
            val = datetime.strptime(s, DT_FORMAT_WITH_SECONDS)
        except ValueError:
            raise ValueError(
                f'datetime "{s}" is not given in a supported format.'
            ) from e

    logger.debug(f'Datetime string "{s}" parsed to datetime "{val}"')
    return val


def format_datetime(dt: datetime) -> str:
    return dt.strftime(DT_FORMAT_WITH_SECONDS)


# endregion


# region audio
def play_audiofile(file: pathlib.Path):
    logger.debug(f'Playing sound file "{file}"')
    playsound3.playsound(file, block=True)


def get_audiofile_duration(file: pathlib.Path):
    tag = tinytag.TinyTag.get(file, tags=False, duration=True)
    if tag.duration:
        audio_duration = timedelta(seconds=tag.duration)
        logger.info(f'Audio duration for "{file}" determined to be {audio_duration}')
        return audio_duration
    else:
        raise RuntimeError(f'Audio duration of "{file}" could not be determined.')


# endregion


# region waiting
def wait_until(dt: datetime):
    logger.debug(f"Waiting until {dt}. Now: {datetime.now()}")
    pause.until(dt)
    logger.debug(f"Waiting exited at {datetime.now()}")


def wait_for(seconds: float):
    logger.debug(f"Waiting for {seconds} s. Now: {time.time()}")
    pause.seconds(seconds)
    logger.debug(f"Waiting exited at {time.time()}")


# endregion


# region info strings
def get_info_string_header(type: str, name: str):
    lines: list[str] = []

    s = f'{type} "{name}":'
    lines.append(s)
    lines.append("-" * len(s))

    return lines


def lines_to_string(lines: list[str]):
    return "\n".join(lines)


# endregion
