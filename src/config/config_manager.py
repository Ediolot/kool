from pathlib import Path
from typing import Union, Tuple

from PIL import ImageColor
from configobj import ConfigObj

from src.config.default_config import kDefaultConfig


class ConfigOptionError(Exception):
    pass


class ConfigManager:

    def __init__(self, config_path: Union[str, Path]):
        self.config = ConfigObj(str(config_path))
        self._check_and_repair_config()

    def _check_and_repair_config(self):
        # Fill missing values
        for section, options in kDefaultConfig.items():
            if section not in self.config.sections:
                self.config[section] = {}
            for option, value in options.items():
                if option not in self.config[section]:
                    self.config[section][option] = value
        self.config.write()

        # Assert io ordering
        ordering = set()
        for option, value in self.config['io_order'].items():
            if value in ordering:
                raise ConfigOptionError('"io_order" contains duplicated values')
            else:
                ordering.add(value)

    def get_bool(self, path) -> bool:
        section, option = path.split('/')
        return self.config[section][option].lower() == 'true'

    def get_int(self, path) -> int:
        section, option = path.split('/')
        return int(self.config[section][option])

    def get(self, path) -> str:
        section, option = path.split('/')
        return self.config[section][option]

    def get_color(self, path) -> Tuple[int, int, int, int]:
        hex_str = self.get(path)
        hex_str = '#' + hex_str if not hex_str.startswith('#') else hex_str
        return ImageColor.getcolor(hex_str, 'RGBA')

    def get_color_pair(self, option) -> Tuple[Tuple[int, int, int, int], Tuple[int, int, int, int]]:
        """ Return a tuple containing the color and the background color for a given option """
        return self.get_color('colors/' + option), self.get_color('background_colors/' + option)

