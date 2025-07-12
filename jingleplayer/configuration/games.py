from __future__ import annotations

import logging
import pathlib
from dataclasses import dataclass
from datetime import datetime

import humanize

import jingleplayer.util as util

from .playlists import SpotifyPlaylist

logger = logging.getLogger(__name__)


def _parse_relative_dt(d: dict, known_games: dict[str, Game]):
    rel_str: str = d["relative_to"]

    if rel_str == "NOW":
        rel_dt = util.RELATIVE_TO_NOW_BASE
    elif rel_str.startswith("END OF GAME: "):
        game_id = rel_str.removeprefix("END OF GAME: ")
        try:
            rel_dt = known_games[game_id].end
        except KeyError as ke:
            raise ValueError(f'Game "{game_id}" does not exist') from ke
    elif rel_str.startswith("START OF GAME: "):
        game_id = rel_str.removeprefix("START OF GAME: ")
        try:
            rel_dt = known_games[game_id].start
        except KeyError as ke:
            raise ValueError(f'Game "{game_id}" does not exist') from ke
    else:
        raise ValueError(f'Value "{rel_str}" is not valid for relative_to')

    if offset_str := d.get("offset", None):
        offset = util.parse_timedelta_str(offset_str)
    else:
        offset = util.ZERO_TD

    dt = rel_dt + offset
    logger.debug(f"Relative start/end specification {d} parsed to datetime {dt}")
    return dt


def _parse_dt(obj: object, games: dict[str, Game]):
    if isinstance(obj, str):
        return util.parse_datetime_str(obj)
    elif isinstance(obj, dict):
        return _parse_relative_dt(obj, games)

    raise ValueError("Unknown datetime specification")


@dataclass
class Game:
    name: str

    start: datetime
    end: datetime

    announcement_file: pathlib.Path | None

    playlist: SpotifyPlaylist | None = None

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError(f"start of game {self.name} is later than the end.")

        if self.announcement_file is not None:
            if not self.announcement_file.is_file():
                raise RuntimeError(
                    f'Announcement file "{self.announcement_file}" does not exist or is not a file.'
                )

            self.announcement_duration = util.get_audiofile_duration(
                self.announcement_file
            )

    def get_info_str(
        self,
        warn_if_no_announcement: bool = False,
        warn_if_no_playlist: bool = False,
    ):
        lines = util.get_info_string_header("Game", self.name)

        lines.append(f"- Start: {util.format_datetime(self.start)}")
        lines.append(f"- End: {util.format_datetime(self.end)}")
        dur = humanize.naturaldelta(self.start - self.end)
        lines.append(f"- Duration: {dur}")

        if self.announcement_file:
            assert self.announcement_duration
            dur = humanize.precisedelta(self.announcement_duration)
            lines.append(
                f'- Announcement file: "{self.announcement_file}" (duration: {dur})'
            )
        elif warn_if_no_announcement:
            lines.append(
                '- WARNING: at least one jingle has the "announce game" action configured, but this game has no announcement file. It will therefore not be announced.'
            )

        if self.playlist:
            lines.append(f"- Game playlist: {self.playlist.name}")
        elif warn_if_no_playlist:
            lines.append(
                '- WARNING: at least one jingle has the "switch to game playlist" action configured, but this game has no playlist. The playlist will be left unchanged.'
            )

        return util.lines_to_string(lines)

    @classmethod
    def from_json_obj(
        cls,
        name: str,
        obj: dict,
        known_games: dict[str, Game],
        playlists: dict[str, SpotifyPlaylist],
        root_dir: pathlib.Path,
    ):
        start = _parse_dt(obj["start"], known_games)

        if (end_str := obj.get("end", None)) is not None:
            end = _parse_dt(end_str, known_games)

            if start >= end:
                raise ValueError("Start of game must be before its end")

        elif (dur_str := obj.get("duration", None)) is not None:
            dur = util.parse_timedelta_str(dur_str)
            end = start + dur
        else:
            raise RuntimeError("Either end or duration must be set on game")

        announcement_file = None
        if ann_file_str := obj.get("announcement_file", None):
            filename = pathlib.Path(ann_file_str)
            announcement_file = root_dir / filename
            logger.info(
                f'Filename "{filename}" resolves to "{announcement_file.resolve()}"'
            )

        if pl_key := obj.get("playlist", None):
            pl = playlists.get(pl_key, None)
        else:
            pl = None

        g = cls(
            name,
            start=start,
            end=end,
            announcement_file=announcement_file,
            playlist=pl,
        )

        plstr = (
            "no playlist set"
            if g.playlist is None
            else f'playlist: "{g.playlist.name}"'
        )
        logger.info(f'Parsed game "{g.name}" (from {g.start} to {g.end}, {plstr})')

        return g
