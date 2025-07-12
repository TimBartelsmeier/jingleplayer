from sdbus import DbusInterfaceCommon, dbus_method


class Player_Interface(  # type: ignore
    DbusInterfaceCommon,
    interface_name="org.mpris.MediaPlayer2.Player",  # type: ignore
):
    @dbus_method()
    def Pause(self):
        raise NotImplementedError()

    @dbus_method()
    def Play(self):
        raise NotImplementedError()

    @dbus_method("s")
    def OpenUri(self, uri: str):
        raise NotImplementedError()
