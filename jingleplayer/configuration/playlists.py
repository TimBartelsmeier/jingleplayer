import logging
import pathlib
from dataclasses import dataclass

import humanize

from jingleplayer import util

logger = logging.getLogger(__name__)


@dataclass
class SpotifyPlaylist:
    name: str
    uri: str

    announcement_file: pathlib.Path | None

    def __post_init__(self):
        if self.announcement_file is not None:
            if not self.announcement_file.is_file():
                raise RuntimeError(
                    f'Announcement file "{self.announcement_file}" does not exist or is not a file.'
                )

            self.announcement_duration = util.get_audiofile_duration(
                self.announcement_file
            )

    def get_info_str(self, warn_if_no_announcement: bool = False):
        lines = util.get_info_string_header("Playlist", self.name)

        lines.append(f"- URI to open: {self.uri}")

        if self.announcement_file:
            assert self.announcement_duration
            dur = humanize.precisedelta(self.announcement_duration)
            lines.append(
                f'- Announcement file: "{self.announcement_file}" (duration: {dur})'
            )
        elif warn_if_no_announcement:
            lines.append(
                '- WARNING: at least one jingle has the "announce playlist" action configured, but this playlist has no announcement file. It will therefore not be announced.'
            )

        return util.lines_to_string(lines)

    @classmethod
    def from_json_obj(
        cls,
        name: str,
        obj,
        root_dir: pathlib.Path,
    ):
        announcement_file = None
        if ann_file_str := obj.get("announcement_file", None):
            filename = pathlib.Path(ann_file_str)
            announcement_file = root_dir / filename
            logger.info(
                f'Filename "{filename}" resolves to "{announcement_file.resolve()}"'
            )

        return cls(
            name,
            uri=obj["uri"],
            announcement_file=announcement_file,
        )
