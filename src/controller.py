from __future__ import annotations

import logging
import os
import sys
import traceback
import pathlib
from pathlib import Path
from importlib import util
from types import ModuleType
from typing import Type, Dict

from PyQt6.QtWidgets import QWidget

from src.vrc_osc.avatar import Avatar

log = logging.getLogger(__name__)

class Controller(QWidget):
    """
    A controller controls a specific avatar through OSC and an Overlay.
    """
    def __init__(self, avatar: Avatar, parent=None):
        super(QWidget, self).__init__(parent)
        self.avatar = avatar

    @staticmethod
    def get_avatar_id() -> str:
        """
        Return the avatar ID that this controller works on.
        :return:
        """
        return "your avatar id here"



class ControllerRegistry:
    """
    Manages the registration and dynamic loading of controller plugin modules.

    The ControllerRegistry class maintains a registry of controllers, dynamically imports controller plugin
    modules from a specified directory, and registers these plugins using their avatar IDs. It can identify valid
    controller subclasses, ensure each controller adheres to the expected structure, and handle dynamic loading
    to enable extendable functionality.

    :ivar controllers: A dictionary mapping avatar IDs to their respective controller classes.
    :type controllers: Dict[str, Type[Controller]]
    """
    def __init__(self):
        self.controllers: Dict[str, Type[Controller]] = {}


    @staticmethod
    def get_standard_plugins_location() -> str:
        bundle_dir: Path
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            # noinspection PyUnresolvedReferences,PyProtectedMember
            bundle_dir = Path(sys._MEIPASS) / '../../plugins'
        else:
            # we are running in a normal Python environment
            bundle_dir = Path(os.path.dirname(os.path.abspath(__file__))) / '../plugins'
        return os.fspath(bundle_dir.resolve())



    def load_all_plugins(self, plugin_folder: str):
        """
        Loads all plugins from the specified folder and dynamically imports plugin modules. It looks for `.py` files in the
        specified directory while skipping hidden files and `__init__.py`. It dynamically loads any valid plugin modules
        that define a subclass of `Controller` and registers these controllers using their avatar ID.

        :param plugin_folder: The directory containing the plugin modules to load.
        :type plugin_folder: str
        :return: None
        """
        log.info(f"Loading plugins from {plugin_folder}")

        if not os.path.exists(plugin_folder):
            log.error("Plugin folder not found.")
            return

        for fname in os.listdir(plugin_folder):
            # skip __init__.py, "." and ".."
            if not fname.startswith('.') and \
                    not fname.startswith('__') and fname.endswith('.py'):
                # noinspection PyBroadException
                log.info(f"Loading plugin: {fname}")
                module_path = os.path.join(plugin_folder, fname)
                try:
                    spec = util.spec_from_file_location(fname, module_path)
                    module = util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name, attr in vars(module).items():
                        if isinstance(attr, type) and issubclass(attr, Controller) and attr != Controller:
                            self.controllers[attr.get_avatar_id()] = attr
                            log.info(
                                f"Loaded controller {attr.__name__} for avatar {attr.get_avatar_id()}"
                            )
                except Exception as e:
                    log.error("Couldn't load module ", module_path, " because: ", e)
                    traceback.print_exc(file=sys.stdout)
                    log.warning(
                        "Make sure that the module has a class that inherits from Controller and overrides get_avatar_id()"
                    )
        log.info("All plugins loaded.")
