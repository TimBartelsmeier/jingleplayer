import json
import logging
import pathlib
from dataclasses import dataclass

import jsonschema
import jsonschema.exceptions

from jingleplayer import util

from .actions import (
    Action,
    PausePlaybackAction,
    ResumePlaybackAction,
    SwitchToGamePlaylistAction,
)
from .games import Game
from .jingles import Jingle
from .playlists import SpotifyPlaylist

logger = logging.getLogger(__name__)

schema_file = pathlib.Path(__file__).with_name("schema.json")


def _load_json(cfg_file: pathlib.Path):
    logger.info(f'Loading config file from "{cfg_file.resolve()}")')

    if not cfg_file.is_file():
        raise RuntimeError(
            f'Specified config file "{cfg_file}" does not exist or is a directory.'
        )

    with cfg_file.open() as cfg_fs:
        return json.load(cfg_fs)


def _validate_against_schema(cfg_json):
    with schema_file.open() as cfg_fs:
        schema = json.load(cfg_fs)

    try:
        jsonschema.validate(cfg_json, schema)
    except jsonschema.exceptions.SchemaError as exc:
        raise RuntimeError("Config schema is not a valid schema") from exc
    except jsonschema.exceptions.ValidationError as exc:
        path_in_config = "config"
        for rp in exc.relative_path:
            path_in_config += f"[{str(rp)}]"

        raise RuntimeError(
            "Config is invalid: " + str(exc.message) + "; occured on " + path_in_config
        ) from exc

    logger.debug("Config json validated against schema")


@dataclass
class Config:
    jingles: dict[str, Jingle]
    games: dict[str, Game]
    playlists: dict[str, SpotifyPlaylist]

    def has_action(self, *actionTypes: type[Action]):
        for actionType in actionTypes:
            if any(
                j.pre_actions.includes(actionType) or j.actions.includes(actionType)
                for j in self.jingles.values()
            ):
                return True

        return False

    @property
    def needs_playback_control(self):
        return self.has_action(PausePlaybackAction, ResumePlaybackAction)

    @property
    def needs_spotify_dbus(self):
        return self.has_action(SwitchToGamePlaylistAction)

    @classmethod
    def load(cls, path: str):
        cfg_file = pathlib.Path(path)
        root_dir = cfg_file.parent

        cfg_json = _load_json(cfg_file)

        _validate_against_schema(cfg_json)

        # Parse default_delay
        default_delay = util.parse_timedelta_str(cfg_json.get("default_delay", "1s"))

        # Parse Playlists
        playlists = {}
        if playlists_obj := cfg_json.get("playlists", None):
            logger.debug("Parsing playlists")
            for name, plobj in playlists_obj.items():
                logger.debug(f'Parsing playlist "{name}"')
                playlists[name] = SpotifyPlaylist.from_json_obj(
                    name,
                    plobj,
                    root_dir=root_dir,
                )
        else:
            logger.debug("No playlists set")

        # Parse Jingles
        logger.debug("Parsing jingles")
        jingles = {}
        for name, jingle_obj in cfg_json["jingles"].items():
            logger.debug(f'Parsing jingle "{name}"')
            jingles[name] = Jingle.from_json_obj(
                name,
                jingle_obj,
                root_dir=root_dir,
                default_delay=default_delay,
            )

        # Parse Games
        logger.debug("Parsing games")
        games = {}
        for name, game_obj in cfg_json["games"].items():
            logger.debug(f'Parsing game "{name}"')
            games[name] = Game.from_json_obj(
                name,
                game_obj,
                known_games=games,
                playlists=playlists,
                root_dir=root_dir,
            )

        logger.debug("Finished parsing config")
        return cls(
            jingles=jingles,
            games=games,
            playlists=playlists,
        )
