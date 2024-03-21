"""Module containing the MainFeatures Enum"""
from enum import Enum


class MainFeatures(str, Enum):
    """Enum of the main AutoSummoner features."""
    AUTO_LOBBY = "AutoLobby"
    AUTO_QUEUE = "AutoQueue"
    AUTO_CHAMPION_SELECT = "AutoChampionSelect"
