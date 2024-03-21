"""Module containing the ConfigAutoQueue class."""
from configparser import ConfigParser

from AutoSummoner.Config.MainFeatures import MainFeatures


class ConfigAutoQueue:
    """Class representing the Auto Queue configuration."""
    __config = None
    __config_parser = None

    SECTION = MainFeatures.AUTO_QUEUE.value

    def __init__(self, config, config_parser: ConfigParser):
        """
        Initializes the auto queue configuration.
        :param config: the Configuration object.
        :param config_parser: the configuration parser.
        """
        self.__config = config
        self.__config_parser = config_parser
        if not self.__config_parser.has_section(self.SECTION):
            self.__config_parser.add_section(self.SECTION)

    def set_enabled(self, enabled: bool) -> None:
        """
        Save whether the auto queue feature is enabled in the config file.
        :param enabled: True to indicate that auto queue is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "enabled", str(enabled))
        self.__config.save_config()

    def is_enabled(self) -> bool:
        """
        :return: True if auto queue is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "enabled", fallback=False)

    def set_auto_start_queue_enabled(self, enabled: bool) -> None:
        """
        Save whether the auto start queue feature is enabled in the config file.
        :param enabled: True to indicate that auto start queue is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "auto_start_queue", str(enabled))
        self.__config.save_config()

    def is_auto_start_queue_enabled(self) -> bool:
        """
        :return: True if auto start queue is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "auto_start_queue", fallback=False)

    def set_auto_accept_match_enabled(self, enabled: bool) -> None:
        """
        Save whether the auto accept match feature is enabled in the config file.
        :param enabled: True to indicate that auto accept match is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "auto_accept_match", str(enabled))
        self.__config.save_config()

    def is_auto_accept_match_enabled(self) -> bool:
        """
        :return: True if auto accept match is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "auto_accept_match", fallback=False)
