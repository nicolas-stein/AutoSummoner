"""Module containing the ConfigAutoChampionSelect class."""
from configparser import ConfigParser

from AutoSummoner.Config.MainFeatures import MainFeatures
from AutoSummoner.Config.Features.ConfigAutoChampionSelectProfile import ConfigAutoChampionSelectProfile


class ConfigAutoChampionSelect:
    """Class representing the Auto Champion Select configuration."""
    __config = None
    __config_parser = None
    __config_per_profile = {}

    SECTION = MainFeatures.AUTO_CHAMPION_SELECT.value

    def __init__(self, config, config_parser: ConfigParser):
        """
        Initializes the auto champion select configuration
        :param config: the Configuration object
        :param config_parser: the configuration parser
        """
        self.__config = config
        self.__config_parser = config_parser
        if not self.__config_parser.has_section(self.SECTION):
            self.__config_parser.add_section(self.SECTION)

        auto_champion_select_profiles_ids = []

        for section in self.__config_parser.sections():
            if section.startswith(self.SECTION+".") and section.count(".") == 1:
                try:
                    auto_champion_select_profiles_ids.append(int(section.removeprefix(self.SECTION+".")))
                except ValueError as e:
                    print(e)

        for profile in auto_champion_select_profiles_ids:
            self.__config_per_profile[profile] = ConfigAutoChampionSelectProfile(profile, self.__config, self.__config_parser)

    def set_enabled(self, enabled: bool) -> None:
        """
        Save whether the auto champion select feature is enabled in the config file.
        :param enabled: True to indicate that auto champion select is enabled, False otherwise.
        """
        self.__config_parser.set(self.SECTION, "enabled", str(enabled))
        self.__config.save_config()

    def is_enabled(self) -> bool:
        """
        :return: True if auto champion select is enabled, False otherwise.
        """
        return self.__config_parser.getboolean(self.SECTION, "enabled", fallback=False)

    def get_all_profiles(self) -> list[ConfigAutoChampionSelectProfile]:
        """
        :return: list of all auto champion select profiles
        """
        return list(self.__config_per_profile.values())

    def get_config_for_profile(self, profile_id: int) -> ConfigAutoChampionSelectProfile:
        """
        :param profile_id: requested auto champion select profile id
        :return: the auto champion select profile with the given profile id
        """
        return self.__config_per_profile[profile_id]

    def generate_profile(self) -> ConfigAutoChampionSelectProfile:
        """
        Generates a new auto champion select profile
        :return: the newly created auto champion select profile
        """
        profile_ids = [profile.get_id() for profile in self.get_all_profiles()]
        if len(profile_ids) == 0:
            new_profile_id = 0
        else:
            new_profile_id = max(profile_ids) + 1

        self.__config_per_profile[new_profile_id] = ConfigAutoChampionSelectProfile(new_profile_id, self.__config, self.__config_parser)

        return self.__config_per_profile[new_profile_id]

    def remove_profile(self, profile_id: int) -> None:
        """
        Removes an auto champion select profile from the configuration
        :param profile_id: id of the profile to remove
        """
        self.__config_per_profile.pop(profile_id)
        self.__config_parser.remove_section(self.SECTION+"."+str(profile_id))
        self.__config.save_config()

    def find_profile_config(self, queue_id: int, position: str) -> ConfigAutoChampionSelectProfile | None:
        """
        :param queue_id: requested queue_id
        :param position: requested position
        :return: an auto champion select profile which can be used for the given queue id and position, or None if no profile could be found
        """
        for profile in self.get_all_profiles():
            if queue_id in profile.get_queues_id():
                if (position == "" and len(profile.get_positions()) == 0) or \
                        (position.upper() in [position.get_league_position_str() for position in profile.get_positions()]):
                    return profile
        return None
