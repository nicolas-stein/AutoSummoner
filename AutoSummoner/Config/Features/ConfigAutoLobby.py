"""Module containing the ConfigAutoLobby class."""
from configparser import ConfigParser

from AutoSummoner.Config.MainFeatures import MainFeatures
from AutoSummoner.LcuInterface.Position import Position


class ConfigAutoLobby:
    """Class representing the Auto Lobby configuration."""

    __config = None
    __config_parser = None

    SECTION = str(MainFeatures.AUTO_LOBBY.value)
    SECTION_AUTO_SELECT_QUEUE = SECTION + ".AutoSelectQueue"
    SECTION_AUTO_SELECT_ROLES = SECTION + ".AutoSelectRoles"
    SECTIONS = [SECTION, SECTION_AUTO_SELECT_QUEUE, SECTION_AUTO_SELECT_ROLES]

    def __init__(self, config, config_parser: ConfigParser):
        """
        Initializes the lobby configuration
        :param config: the Configuration object
        :param config_parser: the configuration parser
        """
        self.__config = config
        self.__config_parser = config_parser
        for section in self.SECTIONS:
            if not self.__config_parser.has_section(section):
                self.__config_parser.add_section(section)

    def set_enabled(self, enabled: bool) -> None:
        """
        Save whether the auto lobby feature is enabled in the config file.
        :param enabled: True to indicate that auto lobby is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "enabled", str(enabled))
        self.__config.save_config()

    def is_enabled(self) -> bool:
        """
        :return: True if auto lobby is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "enabled", fallback=False)

    # Auto Select Queue
    def set_auto_select_queue(self, queue_id: int, enabled: bool) -> None:
        """
        Save whether the auto select queue feature is enabled in the config file.
        :param enabled: True to indicate that auto select queue is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "auto_select_queue", str(enabled))
        self.__config_parser.set(self.SECTION_AUTO_SELECT_QUEUE, "queue_id", str(queue_id))
        self.__config.save_config()

    def is_auto_select_queue_enabled(self) -> bool:
        """
        :return: True if auto select queue is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "auto_select_queue", fallback=False)

    def get_auto_select_queue_id(self) -> int:
        """
        :return: the id of the queue which should be selected automatically or 0 it wasn't configured
        """
        return self.__config_parser.getint(self.SECTION_AUTO_SELECT_QUEUE, "queue_id", fallback=0)

    # Auto Select Roles
    def set_auto_select_roles_enabled(self, enabled: bool) -> None:
        """
        Save whether the auto select roles feature is enabled in the config file.
        :param enabled: True to indicate that auto select roles is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "auto_select_roles", str(enabled))
        self.__config.save_config()

    def is_auto_select_roles_enabled(self) -> bool:
        """
        :return: True if auto select roles is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "auto_select_roles", fallback=False)

    def set_auto_select_roles_preferences(self, first_preference: Position, second_preference: Position) -> None:
        """
        Save the roles which should be automatically selected in the config file.
        :param first_preference: first role to be selected
        :param second_preference: second role to be selected
        """
        self.__config_parser.set(self.SECTION_AUTO_SELECT_ROLES, "first_preference", first_preference.value)
        self.__config_parser.set(self.SECTION_AUTO_SELECT_ROLES, "second_preference", second_preference.value)
        self.__config.save_config()

    def get_auto_select_roles(self) -> tuple[Position, Position]:
        """
        :return: the roles which should be automatically selected, defaults to Top then Middle
        """
        first_preference = Position(self.__config_parser.get(self.SECTION_AUTO_SELECT_ROLES, "first_preference",
                                                             fallback=Position.TOP.value))
        fallback_second = Position.MIDDLE if first_preference == Position.TOP else Position.TOP
        second_preference = Position(self.__config_parser.get(self.SECTION_AUTO_SELECT_ROLES, "second_preference",
                                                              fallback=fallback_second.value))
        return first_preference, second_preference
