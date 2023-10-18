from functools import partial
from threading import Thread

import pyglet  # type: ignore
import pyglet.app  # type: ignore

from mechvibes.impl import constants
from mechvibes.impl.audio_handler import AudioHandler
from mechvibes.impl.listeners import LinuxListener
from mechvibes.impl.parser import ConfigParser

pyglet.options["headless"] = True


class App:
    def __init__(self):
        ...

    def instigate_listener(
        self, platform: constants.Platform, *, run_in_thread: bool = False
    ) -> bool:
        if not self.platform_is_supported(platform):
            raise NotImplementedError("Operating system unsupported.")

        parser = ConfigParser(
            constants.THEME_SETS_DIR_PATH,
            constants.ACTIVE_THEME_ID,
            constants.CONFIG_FILE_NAME,
        )
        audio_handler = AudioHandler(parser)

        match platform:
            case constants.Platform.DARWIN:
                ...
            case constants.Platform.LINUX:
                listener = LinuxListener(
                    constants.EVENT_PATH, constants.INPUT_EVENT_CODE, audio_handler
                )
                if run_in_thread:
                    listener_thread = Thread(target=listener.listen, daemon=True)
                    listener_thread.start()
                else:
                    listener.listen()
            case constants.Platform.WIN32:
                ...

        return True

    def on_pyglet_event_loop_start(self, platform: constants.Platform):
        Thread(
            target=self.instigate_listener,
            args=(platform,),
            kwargs=dict(run_in_thread=False),
            daemon=True,
        ).start()

    def run(self, platform: constants.Platform):
        event_loop = pyglet.app.EventLoop()
        event_loop.on_enter = partial(self.on_pyglet_event_loop_start, platform)
        event_loop.run()

    def platform_is_supported(self, platform: constants.Platform) -> bool:
        return platform in constants.SUPPORTED_PLATFORMS
