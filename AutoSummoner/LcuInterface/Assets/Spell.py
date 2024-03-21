"""Module containing the Spell class."""


class Spell:
    """
    Class representing a League of Legends summoner spell.
    """
    def __init__(self, spell_id: int, name: str | None, gamemodes: list | None):
        """
        Initialise the spell.
        :param spell_id: id of the spell.
        :param name: name of the spell.
        :param gamemodes: list of gamemodes this spell is available in.
        """
        self.__id = spell_id
        self.__name = name
        self.__gamemodes = gamemodes

    def id(self) -> int:
        """
        :return: the id of the spell.
        """
        return self.__id

    def name(self) -> str:
        """
        :return: the name of the spell.
        """
        return self.__name if self.__name is not None else "Unknown"

    def gamemodes(self) -> list[str]:
        """
        :return: the list of gamemodes this spell is available in.
        """
        return self.__gamemodes if self.__gamemodes is not None else []

    def __repr__(self):
        return f"Spell(id={self.id()}, name={self.name()}, gamemodes={self.gamemodes()})"
