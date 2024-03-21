"""Module containing the AssetsWorker class."""
import requests
from PyQt5.QtCore import QObject, pyqtSignal

from AutoSummoner.LcuInterface.Assets.Spell import Spell
from AutoSummoner.LcuInterface.Assets.Champion import Champion


class AssetsWorker(QObject):
    """Asset worker responsible for loading static assets in the background"""

    __champions_dict = {}
    __summoner_spells_dict = {}

    # Signals
    champions_loaded = pyqtSignal(dict)
    summoner_spells_loaded = pyqtSignal(dict)

    def run(self):
        """
        Worker function which runs in another thread.
        Loads all assets
        """
        self.__load_champions()
        self.__load_summoner_spells()

    def __load_champions(self):
        """
        Loads all League of Legends champions data from the community dragon API
        """
        try:
            response = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json', timeout=30)
            champions = response.json()
        except requests.exceptions.RequestException as e:
            print("Failed to get champion list !\n", e)
            return

        self.__champions_dict = {}
        for champion in champions:
            if champion["id"] > 0:
                self.__champions_dict[champion["id"]] = Champion(champion["id"], champion["name"])

        self.__champions_dict = dict(sorted(self.__champions_dict.items(), key=lambda champ: champ[1].name()))
        self.champions_loaded.emit(self.__champions_dict)

    def __load_summoner_spells(self):
        """
        Loads all League of Legends summoners spells data from the community dragon API
        """
        summoners_spells = []
        try:
            response = requests.get('https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-spells.json', timeout=30)
            summoners_spells = response.json()
        except requests.exceptions.RequestException as e:
            print("Failed to get summoner spell list !\n", e)

        self.__summoner_spells_dict = {}
        for spell in summoners_spells:
            if len(spell["name"]) > 0 and len(spell["gameModes"]) > 0:
                self.__summoner_spells_dict[spell["id"]] = Spell(spell["id"], spell["name"], spell["gameModes"])

        self.__summoner_spells_dict = dict(sorted(self.__summoner_spells_dict.items(), key=lambda spell_: spell_[1].name()))
        self.summoner_spells_loaded.emit(self.__summoner_spells_dict)
