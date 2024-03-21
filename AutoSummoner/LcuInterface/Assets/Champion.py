"""Module containing the Champion class."""


class Champion:
    """Class representing a League of Legends Champion."""
    def __init__(self, champ_id: int, name: str | None):
        """
        Initialise the Champion
        :param champ_id: id of the champion
        :param name: name of the champion or None if unknown
        """
        self.__id = champ_id
        self.__name = name

    def id(self) -> int:
        """
        :return: the id of the champion.
        """
        return self.__id

    def name(self) -> str:
        """
        :return: the name of the champion.
        """
        return self.__name if self.__name is not None else "Unknown"

    def __eq__(self, __value):
        return self.__id == __value.id() if isinstance(__value, Champion) else super().__eq__(__value)

    def __repr__(self):
        return f"Champion(id={self.id()}, name={self.name()})"
