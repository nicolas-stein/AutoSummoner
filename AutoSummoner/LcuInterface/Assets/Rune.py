"""Module containing the Rune class."""


class Rune:
    """Class representing a League of Legends Rune page."""
    def __init__(self, lcu_rune: dict):
        """
        Initialize the Rune.
        :param lcu_rune: LCU dictionary containing information about the rune.
        """
        self.__id = lcu_rune["id"]
        self.__name = lcu_rune["name"]
        self.__is_valid = lcu_rune["isValid"]

    def id(self) -> int:
        """
        :return: the id of the rune.
        """
        return self.__id

    def name(self) -> str:
        """
        :return: the name of the rune.
        """
        return self.__name

    def is_valid(self) -> bool:
        """
        :return: True if the rune is valid, False otherwise.
        """
        return self.__is_valid
