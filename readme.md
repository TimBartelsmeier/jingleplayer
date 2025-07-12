# Jingleplayer
## General information
At sports tournaments, short audio files ("jingles") are often played as time signals at the start and/or end of games. This program can be used to play jingles for predefined time slots (e.g. all games played during a tournament). After setting up the configuration for a tournament (see [below](#usage)), you just need to start this program and (if you want) music playback at the beginning of the tournament. The program will then run unattended and no one needs to be time keeper and give signals manually.

The program can automatically pause or resume music playback (e.g. using Spotify) before or after a jingle is played to ensure the jingle can be heard. It can also do some more "advanced" stuff, like announcing games or switching to a different Spotify playlist (or album, ...) for each game.

As of right now, there is no "proper" documentation. There is some basic information to get you started in the next sections; and I’ve tried to keep the instructions as understandable as possible, even for those who aren’t very tech-savvy. If you struggle to get this running or need assistance setting up your tournament, feel free to reach out, I'd be glad to help! The same is true for feature requests, remarks, or ideas for improvement (see also the current [list of feature ideas and todos](#feature-ideas-and-todo)).

## Installation
1. [Install `pixi`](https://pixi.sh/latest/installation/) on your device. You might need to reboot (or re-log) after this.
2. `clone` this repository. Alternatively, you can download the `.zip` archive ("Code" button in the top right -> "Download ZIP") and extract it into a new folder somewhere on your device.
3. Open a terminal session and navigate to the folder into which you cloned/unzipped this project. On Windows, you can do this from the explorer by pressing `SHIFT`, right-clicking into the empty space below all files and selecting "Open PowerShell window here".
4. Run `pixi install` and wait for it to finish.

### Limitations on Windows
This program works best on Linux. On Windows, it can only control music playback by emulating a key press of the play/pause button some keyboards have. On Linux, it can use a more sophisticated method for controlling music playback by "talking" to Spotify directly, which is more reliable and allows to switch playlists for individual games (see [below](#playback-control) for more details on the limitations). If these limitations don’t bother you, you can use the program just fine on Windows.

To get the more advanced options/features possible on Linux on Windows, you can try running the program through [`WSL` (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/setup/environment). I haven’t tested this extensively, but based on my initial tests (Ubuntu, [Spotify installed via `snap`](https://www.spotify.com/de/download/linux/)), it should work as long as you run both the program and Spotify through WSL.

## Usage
Open a shell in the installation folder (like you did [during the installation](#installation)) and run:
`pixi run python -m jingleplayer "{configfile}" {options}`
where you replace `{configfile}` with the path (absolute or relative to the installation folder) to your configuration file.

`{options}` are additional options you can provide. Typically, you probably want to use at least one option for playback control (explained in the [next section](#playback-control)) and, before you actually use the program, test whether everything is set up correctly and works as expected (explained in the [section after the next](#test-modes)). There are also some additional advanced options available, such as setting up a log file. To see the full list, run `pixi run python -m jingleplayer --help`.

### Playback control
Music playback control is configured with the `-p` command-line option. There are three possible values, which will be explained below. If you don't need playback control (i.e. no automatic pausing/resuming music for jingles), you can omit this option altogether.

- `-p spotify_dbus`: This mechanism "talks" to the Spotify client directly using the `dbus` interface. This allows for reliable pausing/resuming (if the program tries to pause music and it is already paused, it stays paused and vice versa) and to switch to specific playlists using the jingleplayer. However, it only works on Linux (as mentioned aboved, it might work on Windows devices if you use `WSL` to run this program and Spotify).

- `-p key`: This mechanism controls music playback by emulating a key press of the play/pause key (which some keyboards have) and to which most media programs should respond. However, there are some limitations with this:
  - The program can only toggle between playing/paused and doesn't know if music is currently running or not. If the program tries to pause music which is already paused, it will start playing instead of staying paused (which is probably what you'd want in this scenario) and vice versa.
  - Typically, they key only controls _one_ media player. If you have multiple active at the same time (e.g. Spotify and a YouTube video), the key press might not control the one you want.
  - It is not possible to switch Spotify playlists with this controller.
  
  Essentially, you need to use this controller if:
  - If you use something other than Spotify for music
  - If you are on Windows and `WSL` is not an option or you don't require the "advanced" features.

It might be possible to create an "advanced" control mechanism similar to `spotify_dbus` for other media sources (YouTube Music, Deezer, ...) as well - I just didn't have a need for it so far. If you do, feel free to reach out and I can look into implementing something similar for your media source of choice.

Two more points for the sake of completeness (you probably won’t need these): 1) There is also `-p dummy`, which I use for testing. It doesn't actually do any control and just prints to the console instead. 2) You can specify multiple controller by separating them with spaces, e.g. `-p dummy key`.

### Test modes
To check whether everything works before using the program, e.g. ...
- ... whether all games & jingles are set up properly;
- ... whether all audio files (jingles, announcements, ...) play properly, have an appropriate volume, ...;
- ... whether playback control works;

you can use the built-in test mode(s). To test everything, simple call the program as you would do for your actual usage and add `--test`. See `--help` for more details.

## Basic configuration
Each tournament (i.e. a group of games for which you want to play the same jingles) is configured with a `.json` file. The [basic configuration file example](<tournaments/example/config - basic example.json>) is a good starting point, together with the notes/examples below.

I recommend storing all files related to a tournament (the config file and all audio files) in a subdirectory in the `tournaments` subdirectory to keep everything "in one place", but you don't have to do this.

### Audio files
You can specify audio files using relative or absolute paths. Relative paths are relative to the config file.

To play audio, this program uses the [`playsound3`](https://github.com/sjmikler/playsound3) library. Supported audio formats vary depending on which backend `playsound3` can use on your device. `mp3` is probably the safest option and should work on all systems and configurations. To test if your audio files work properly, run with the [--testaudio (or `--test`) option](#test-modes).

### `timedelta`s
Multiple properties in the configuration file are `timedelta`s, for example the `duration` of a game or how far it is `offset` from another game. Here are some examples of valid inputs:
- `2s` = 2 seconds long (for `duration`s) or 2 seconds later (for `offset`s)
- `-30min` = 30 minutes earlier
- `5h 3m` = 5 hours and 3 minutes long/later
Negative values are only valid for `offset`s, not for `duration`s.

For more valid formats check the documentation of the [pytimeparse2](https://github.com/onegreyonewhite/pytimeparse2) library that is used for parsing.

### Games
Games have a `start` and an `end`, both of which are `datetime` objects, meaning they refer to a specific time on a specific day. (Repeating games aren’t supported at the moment - you’ll need to create a separate game for each occurrence.) However, you don’t have to define both start and end explicitly: you can specify `start` or `end` relative to the start/end of another game and you can specify `start` and a `duration` instead of the `end`. See the following examples:

- explicit `start` and `end`:
  
  ```json
  "Example Game": {
      "start": "2025-01-01 12:00",
      "end": "2025-01-01 13:00"
  }
  ```

  The format is `%Y-%m-%d %H:%M` (with [these](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) format codes). If you need second-level specification, `%Y-%m-%d %H:%M:%S` is also accepted.

- relative `start` and `duration` instead of `end`:

  ```json
  "games": {
    "Game 1": {
      "start": "2025-01-01 12:00",
      "duration": "1h"
    },
    "Game 2": {
      "start": {
          "relative_to": "END OF GAME: Game 1",
          "offset": "30min"
      },
      "duration": "1h"
    },
    "Game 3": {
      "start": {
        "relative_to": "END OF GAME: Game 2",
        "offset": "30min"
      },
      "duration": "1h"
    }
  }
  ```

  `duration` and `offset` are `timedelta` strings as [explained above](#timedeltas).

If there are a lot of games in close succession, I recommend specify the first game's `start` explicitely and all other games relative to the previous one (like in the example above). The benefit is that you can easily re-schedule without having to edit all games by hand. For example, assume that after the first game, there is some unforeseen delay and the second game can not start at 13:30 as originally planned and needs to be shifted half an hour. Now, you can just close the program, change the configuration file to

```jsonc
// ...
  "Game 2": {
    "start": "2025-01-01 14.00",
// ...
```

and restart the program. Game 3 will automatically be adjusted as well.

Further notes:
- When defining a game’s `start` or `end` relative to another game, the referenced game must appear earlier in the list.
- Instead of `END OF GAME: <name of game>`, you can also use `START OF GAME: <name of game>`.
- You can also use `"relative_to": "NOW"` to make a game start or end relative to the current time (= when the program is started). This is mostly useful for debugging, I can't think of any real-world use case.

### Jingles
A jingle is a set of actions that is executed at a certain trigger time for each game. In the default configuration:
- music playback is paused one second before the trigger,
- at the trigger time the specified audio file is played,
- after the jingle finishes playing, one second is waited before resuming music playback.

Which actions are done [can be customized](#advanced-configuration). If you don't want music playback control, you also simply omit the `-p {...}` option when calling the program.

The one second delay before and after the audio file can be customized by setting the top-level `default_delay` key to a [valid `timedelta` string](#timedeltas), for example

```jsonc
{
    "config_version": "1.0",
    "default_delay": "3s",
    // ...
}
```

`0s` is also a valid value if you don't want any delay. More fine-grained control (e.g. asymmetric delays for before/after the jingle) [is also possible](#advanced-configuration).

You can select when a jingle should be played using a `trigger` and an `offset` from this trigger. For example, with the following configuration

```jsonc
"jingles": {
    "Start": {
        "audio_file": "jingle start.mp3",
        "trigger": "game_start"
    },
    "5min left": {
        "audio_file": "jingle 5min left.mp3",
        "trigger": "game_end",
        "offset": "-5m"
    },
    "Stop": {
        "audio_file": "jingle stop.mp3",
        "trigger": "game_end"
    }
}
```

"Start" is played at the start of each game, "5min left" when there are 5 minutes left on the clock, and "End" at the end of each game.

If the trigger time for a jingle/game combination has already passed when the program starts, it will simply be ignored. This lets you (re)start the program anytime during the tournament (even on the next day for multi-day tournaments) and the next jingle(s) will play at the correct time(s).

## Advanced configuration
You can customize which actions to do for each jingle. This also allows you to do things like, for example,
- fine-grained control over music playback, e.g. let one specific jingle play without pausing the music or only pause  playback beforehand and do not resume afterwards,
- announce each game (play a game-specific audio file),
- switch to a specific Spotify playlist (only possible with [`-p spotify_dbus`](#playback-control)).

To get started, have a look at [this example configuration](<tournaments/example/config - advanced example.json>).

### Actions
Valid actions are:
- `do nothing`: Self-explanatory. You can use this if you want to disable [the default behavior](#jingles) of jingles, e.g. specify `"pre_actions": "do nothing"` to not pause music playback before the jingle.
- `wait <timedelta>`: blocks the program for a certain time (i.e. delays execution of all following actions). For example, (short) delays are useful as "buffers" to ensure that jingles are clearly separated from the music playing before or after, or to separate different announcements. The delay must be positive.
- `pause playback` and `resume playback`: pauses or resumes music playback using the playback controller(s) [configured with `-p`](#playback-control). If none are configured, does nothing.
- `play jingle`: plays the jingle's `audio_file`. If none is set for this jingle, does nothing.
- `announce game`: plays the current game's `announcement_file`. If none is set for this game, does nothing.
- `switch to game playlist`: switches Spotify playback to the current game's playlist. If none is set, does nothing. Note that switching to the playlist automatically starts playback if it was paused before, so there is no need to have a `resume playback` after this. See below for information on how to configure a playlist.
- `announce game playlist`: plays `announcement_file` of the current game's playlist. If the current game has no playlist set or the playlist has no announcement file set, does nothing.

Actions can be chained by separating them with semicolons, e.g. `play jingle; wait 10s; resume playback`. The duration of audio files is taken into account when scheduling `pre_actions`. For example, take the following configuration:

```jsonc
"Start": {
    "audio_file": "jingle start.mp3",
    "trigger": "game_start",
    "pre_actions": "announce game; wait 2s",
    "actions": "play jingle"
},
```

If the game's announcement file is 5 seconds long, it will be played 7 seconds before the start of the game to ensure that the 2 second delay is kept and the jingle is played at the correct time.

Technical note: In reality, the scheduling might be off by a little bit due to two reasons:
- It is assumed that there is no overhead to execution, i.e. that `wait` takes exactly the specified time; `play jingle`, `announce game` and `announce game playlist` take exactly as long as the played audio file; and all other actions are instantenous.
- The determined duration of audio files might be rounded and differ slightly from the actual time required to play the file.
  
The difference will probably be _very_ small (I assume ms-scale - if you do something that requires that much precision, you should probably use a different program anyway). Nevertheless, the program includes a small workaround to compensate for this: trailing `wait` actions are used to calculate when to start with the `pre_actions`, but are not actually executed. (`wait`s that are not at the end of `pre_actions` or `actions` are executed as expected.) In the example above, the announcement file is played exactly 7 seconds before the jingle should be played. If, due to the inaccuracies listed above, it takes 5 seconds and 100 ms to play it(instead of the expected 5 seconds), the jingle will still play at the expected time and the planned 2 second delay becomes a 1.9 second delay.

### Spotify URIs
To determine the URI for a Spotify playlist, do the following:
1. In the desktop client or the web client on a desktop device, right click on the playlist's title and select "Share" -> "Copy link to playlist". In the mobile apps, select "Copy link" from the share menu (accessible from the the three-dots menu under the playlist's title). This will give you the URL (notice the L instead of an I at the end), e.g. <https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF?si=49f49b8a79fa41eb> for the "Global Top 50" playlist.
2. From this URL, select the identifier part, which is the combination and letters between `playlist/` and `?si=`. For the example playlist from the previous step, this is `37i9dQZEVXbMDoHDwVN2tF`.
3. The playlist's URI is `spotify:playlist:{identifier}`, e.g. `spotify:playlist:37i9dQZEVXbMDoHDwVN2tF`.

The URI obtained in step 3 is what you need to set as a playlist's `uri` property to have the playlist start playing on a `switch to game playlist` action. If you specify the URL obtained in step 1 instead, the Spotify client will only display the playlist's page and stop playing music instead. You can also have a look at [Spotify's web API documentation](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids) for more information on the different parameter types.

Note: I named this feature for playlists because I found this to be the most useful, but the specified `uri` can point to any type of Spotify resource, e.g. an album, a song (`track`), a podcast (`show`), an episode of a podcast (`episode`). Determining the URIs of these resources works the same way as described above for playlists.

## Feature ideas and todo
This is a list of potential improvements and features. If any of these would be useful for you - or if you have a new idea - let me know, and I’ll look into implementing it.

- Improvements:
  - Better logging (check what might be superflous and what is missing)
  - More information / "nicer" text UI for the scheduling mode

- QoL features:
  - Load games from iCal-files
  - Additional jingle trigger: half-time
  - Option(s) to skip warning/info messages (e.g. when no playback controller is passed)
  - Improve key-based playback controller
    - Option to invert the assumed playback state at program start to paused instead of playing
    - Add internal status tracking, so pause() is not called twice in succession

- Larger features
  - Ability to set tags for games and jingle to only play (or to not play) for a specific tag. Use case examples:
    - Special jingles that should only play for the finale
    - Organizational announcements (lunch break, ...). Rename games to events for this?
  - Query Spotify resource details using Spotify's web API to show "proper" playlist name, determine whether the playlist is long enough until the next one is started, ...
  - Playback controllers like `spotify_dbus` for other media sources