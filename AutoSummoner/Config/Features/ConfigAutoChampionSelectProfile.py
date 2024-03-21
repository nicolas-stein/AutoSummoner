"""Module containing the Auto Champion Select profile class."""
from configparser import ConfigParser

from AutoSummoner.Config.MainFeatures import MainFeatures
from AutoSummoner.LcuInterface.Position import Position


class ConfigAutoChampionSelectProfile:
    """Class representing an Auto Champion Select profile."""
    __config = None
    __config_parser = None
    __positions = None

    SECTION_PREFIX = MainFeatures.AUTO_CHAMPION_SELECT.value

    def __init__(self, profile_id: int, config, config_parser: ConfigParser):
        """
        Initializes the auto champion select profile configuration
        :param profile_id: id of the auto champion select profile
        :param config: the Configuration object
        :param config_parser: the configuration parser
        """
        self.__config = config
        self.__config_parser = config_parser
        self.__profile_id = profile_id
        self.section = self.SECTION_PREFIX + "." + str(profile_id)
        if not self.__config_parser.has_section(self.section):
            self.__config_parser.add_section(self.section)

    def get_id(self) -> int:
        """
        :return: the id of this profile
        """
        return self.__profile_id

    def set_name(self, name: str) -> None:
        """
        Save the name of this profile in the config file.
        :param name:
        :return:
        """
        self.__config_parser.set(self.section, "name", name)
        self.__config.save_config()

    def get_name(self) -> str:
        """
        :return: name of the profile
        """
        return self.__config_parser.get(self.section, "name", fallback="Undefined")

    def set_queues_id(self, queues: list[int]) -> None:
        """
        Save the list of queues id this profile can be applied to in the config file.
        :param queues: list of queues id this profile can be applied to.
        """
        self.__config_parser.set(self.section, "queues", ','.join([str(queue) for queue in queues]))
        self.__config.save_config()

    def get_queues_id(self) -> list[int]:
        """
        :return: list of queues id that this profile is applied to.
        """
        queues_str = self.__config_parser.get(self.section, "queues", fallback="")
        if len(queues_str) > 0:
            return [int(queue_id) for queue_id in queues_str.split(",")]

        return []

    def set_positions(self, positions: list[Position]) -> None:
        """
        Save the list of positions this profile can be applied to in the config file.
        :param positions: list of positions this profile can be applied to.
        """
        self.__config_parser.set(self.section, "positions", ','.join([str(position.get_index()) for position in positions]))
        self.__config.save_config()

    def get_positions(self) -> list[Position]:
        """
        :return: list of positions that this profile is applied to.
        """
        positions_str = self.__config_parser.get(self.section, "positions", fallback="")
        if len(positions_str) > 0:
            return [Position.from_index(int(position_index)) for position_index in positions_str.split(",")]

        return []

    def set_champions_ban_id(self, champions_ban_id: list[int]) -> None:
        """
        Save the id of the champions that should be banned in the config file.
        :param champions_ban_id: list of id of the champions to ban (ordered by priority).
        """
        self.__config_parser.set(self.section, "champions_ban", ','.join([str(champion_id) for champion_id in champions_ban_id]))
        self.__config.save_config()

    def get_champions_ban_id(self) -> list[int]:
        """
        :return: list of id of the champions that should be bans (ordered by priority).
        """
        champions_ban_str = self.__config_parser.get(self.section, "champions_ban", fallback="")
        if len(champions_ban_str) > 0:
            return [int(champion_id) for champion_id in champions_ban_str.split(",")]

        return []

    def set_champions_pick_id(self, champions_pick_id: list[int]) -> None:
        """
        Save the id of the champions that should be picked in the config file.
        :param champions_pick_id: list of id of the champions to pick (ordered by priority).
        """
        self.__config_parser.set(self.section, "champions_pick", ','.join([str(champion_id) for champion_id in champions_pick_id]))
        self.__config.save_config()

    def get_champions_pick_id(self) -> list[int]:
        """
        :return: list of id of the champions that should be picked (ordered by priority).
        """
        champions_pick_str = self.__config_parser.get(self.section, "champions_pick", fallback="")
        if len(champions_pick_str) > 0:
            return [int(champion_id) for champion_id in champions_pick_str.split(",")]

        return []

    def set_summoner_spells_id_global(self, summoner_spell_1_id: int, summoner_spell_2_id: int) -> None:
        """
        Save the id of the summoner spells that should be used for all champions in the config file.
        :param summoner_spell_1_id: id of the first summoner spell that should be used for all champions.
        :param summoner_spell_2_id: id of the first summoner spell that should be used for all champions.
        """
        self.__config_parser.set(self.section, "summoner_spell_1_global", str(summoner_spell_1_id))
        self.__config_parser.set(self.section, "summoner_spell_2_global", str(summoner_spell_2_id))
        self.__config.save_config()

    def get_summoner_spells_id_global(self) -> tuple[int, int] | None:
        """
        :return: id of the summoner spells that should be used for all champions.
        """
        summoner_spell_1_str = self.__config_parser.get(self.section, "summoner_spell_1_global", fallback="")
        summoner_spell_2_str = self.__config_parser.get(self.section, "summoner_spell_2_global", fallback="")

        if len(summoner_spell_1_str) == 0 or len(summoner_spell_2_str) == 0:
            return None

        return (int(summoner_spell_1_str),
                    int(summoner_spell_2_str))

    def set_summoner_spells_id_per_champion_id(self, champion_id: int,
                                         summoner_spell_1_id: int, summoner_spell_2_id: int) -> None:
        """
        Save the summoner spells which should be selected for the given champion in the config file.
        :param champion_id: id of the champion.
        :param summoner_spell_1_id: id of the first summoner spell.
        :param summoner_spell_2_id: id of the first summoner spell.
        """
        self.__config_parser.set(self.section, f"summoner_spell_1_{champion_id}", str(summoner_spell_1_id))
        self.__config_parser.set(self.section, f"summoner_spell_2_{champion_id}", str(summoner_spell_2_id))
        self.__config.save_config()

    def get_summoner_spells_id_per_champion_id(self, champion_id: int) -> tuple[int, int] | None:
        """
        :param champion_id: champion id.
        :return: id of the summoner spells that should be used for the given champion id.
        """
        summoner_spell_1_str = self.__config_parser.get(self.section, f"summoner_spell_1_{champion_id}", fallback="")
        summoner_spell_2_str = self.__config_parser.get(self.section, f"summoner_spell_2_{champion_id}", fallback="")

        if len(summoner_spell_1_str) == 0 or len(summoner_spell_2_str) == 0:
            return None

        return (int(summoner_spell_1_str),
                    int(summoner_spell_2_str))

    def set_using_individual_summoner_spell(self, enabled: bool) -> None:
        """
        Save whether this profile roles should use individual summoner spells per champion to pick.
        :param enabled: True if this profile should use individual summoner spells per champion to pick, false otherwise
        """
        self.__config_parser.set(self.section, "summoner_spells_unique_per_champion", str(enabled))
        self.__config.save_config()

    def is_using_individual_summoner_spell(self) -> bool:
        """
        :return: True if this profile should use individual summoner spells per champion to pick, false otherwise
        """
        return self.__config_parser.getboolean(self.section, "summoner_spells_unique_per_champion", fallback=False)

    def set_rune_id_global(self, rune_id: int) -> None:
        """
        Save the id of the rune that should be used for all champions.
        :param rune_id: id of the rune that should be used for all champions.
        """
        self.__config_parser.set(self.section, "rune_global", str(rune_id))
        self.__config.save_config()

    def get_rune_id_global(self) -> int:
        """
        :return: id of the rune that should be used for all champions.
        """
        return self.__config_parser.getint(self.section, "rune_global", fallback=0)

    def set_using_individual_rune(self, enabled: bool) -> None:
        """
        Save whether this profile roles should use individual rune per champion to pick.
        :param enabled: True if this profile should use individual rune per champion to pick, false otherwise
        """
        self.__config_parser.set(self.section, "runes_unique_per_champion", str(enabled))
        self.__config.save_config()

    def is_using_individual_rune(self) -> bool:
        """
        :return: True if this profile should use individual rune per champion to pick, false otherwise
        """
        return self.__config_parser.getboolean(self.section, "runes_unique_per_champion", fallback=False)

    def set_rune_id_per_champion(self, champion_id: int, rune_id: int) -> None:
        """
        Save the rune which should be selected for the given champion in the config file.
        :param champion_id: id of the champion.
        :param rune_id: id of the rune.
        """
        self.__config_parser.set(self.section, f"rune_{champion_id}", str(rune_id))
        self.__config.save_config()

    def get_rune_id_per_champion(self, champion_id: int) -> int:
        """
        :param champion_id: champion id.
        :return: id of the rune that should be used for the given champion id.
        """
        return self.__config_parser.getint(self.section, f"rune_{champion_id}", fallback=0)
