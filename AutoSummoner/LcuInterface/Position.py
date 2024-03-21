"""Module containing the Position class."""
from enum import Enum


class Position(str, Enum):
    """Class representing a League of Legends Position."""
    TOP = "Top"
    MIDDLE = "Middle"
    JUNGLE = "Jungle"
    BOTTOM = "Bottom"
    SUPPORT = "Support"

    @staticmethod
    def get_all_positions() -> list:
        """
        :return: the list of all positions.
        """
        return list(Position)

    @staticmethod
    def from_index(index: int):
        """
        :param index: index of the position .
        :return: Position instance for the given index.
        """
        return Position.get_all_positions()[index]

    def get_index(self):
        """
        :return: the index of the position in the Enum.
        """
        positions = Position.get_all_positions()
        return positions.index(self)

    def get_league_position_str(self) -> str:
        """
        :return: the position as a LCU string.
        """
        league_position_dict = {
            Position.TOP: "TOP",
            Position.MIDDLE: "MIDDLE",
            Position.JUNGLE: "JUNGLE",
            Position.BOTTOM: "BOTTOM",
            Position.SUPPORT: "UTILITY"
        }
        return league_position_dict[self]
