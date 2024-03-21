"""Module containing the Configuration class."""
import configparser

from AutoSummoner.Config.Features.ConfigAutoChampionSelect import ConfigAutoChampionSelect
from AutoSummoner.Config.Features.ConfigAutoLobby import ConfigAutoLobby
from AutoSummoner.Config.Features.ConfigAutoQueue import ConfigAutoQueue
from AutoSummoner.Config.MainFeatures import MainFeatures


class Configuration:
    """Class representing the AutoSummoner Configuration."""
    __config_parser = configparser.ConfigParser()
    __feature_configurations = {}

    def __init__(self):
        """
        Initializes the Configuration
        """
        self.load_config()
        self.__feature_configurations = {
            MainFeatures.AUTO_LOBBY: ConfigAutoLobby(self, self.__config_parser),
            MainFeatures.AUTO_QUEUE: ConfigAutoQueue(self, self.__config_parser),
            MainFeatures.AUTO_CHAMPION_SELECT: ConfigAutoChampionSelect(self, self.__config_parser)
        }

    def load_config(self) -> None:
        """
        Load configuration from the config.ini file
        :return:
        """
        self.__config_parser.read("config.ini")

    def save_config(self) -> None:
        """
        Save the configuration to the config.ini file
        """
        with open('config.ini', 'w', encoding="utf-8") as configfile:
            self.__config_parser.write(configfile)
            configfile.flush()

    def get_feature_configuration(self, feature: MainFeatures) -> ConfigAutoLobby | ConfigAutoQueue | ConfigAutoChampionSelect:
        """
        :param feature: requested main feature
        :return: the feature configuration
        """
        return self.__feature_configurations[feature]
