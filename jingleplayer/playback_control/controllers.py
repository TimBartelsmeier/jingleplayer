import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PlaybackController(ABC):
    CAN_ONLY_TOGGLE: bool = True

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def resume(self):
        pass


class DummyPlaybackController(PlaybackController):
    CAN_ONLY_TOGGLE = False

    @property
    def name(self) -> str:
        return "dummy playback controller"

    def pause(self):
        s = f"{self.name}: pause() called"
        logger.debug(s)
        print(s)

    def resume(self):
        s = f"{self.name}: resume() called"
        logger.debug(s)
        print(s)


class PlayPauseKeyPlaybackController(PlaybackController):
    CAN_ONLY_TOGGLE = True

    @property
    def name(self) -> str:
        return "key-based playback controller"

    def __init__(self):
        super().__init__()

        try:
            import pynput.keyboard

            self._controller = pynput.keyboard.Controller()
            self._key = pynput.keyboard.Key.media_play_pause

            logger.debug("pynput set up")
        except ImportError as e:
            raise RuntimeError(
                f"{self.name} requires the package pynput. Make sure it and all its dependencies are installed and accessible"
            ) from e

    def toggle(self):
        self._controller.tap(self._key)

    def pause(self):
        self.toggle()

    def resume(self):
        self.toggle()


class SpotifyDbusPlaybackController(PlaybackController):
    CAN_ONLY_TOGGLE: bool = False

    @property
    def name(self) -> str:
        return "dbus-based playback controller for Spotify"

    def __init__(self):
        super().__init__()

        from .dbus_interface import Player_Interface

        self._dbus_proxy = Player_Interface(
            service_name="org.mpris.MediaPlayer2.spotify",
            object_path="/org/mpris/MediaPlayer2",
        )

    def pause(self):
        self._dbus_proxy.Pause()

    def resume(self):
        self._dbus_proxy.Play()

    def open_uri(self, uri: str):
        self._dbus_proxy.OpenUri(uri)
