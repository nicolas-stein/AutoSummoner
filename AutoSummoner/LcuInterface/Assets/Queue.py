"""Module containing the Queue class."""


class Queue:
    """Class representing a League of Legends Queue."""
    def __init__(self, lcu_queue: dict):
        """
        Initialize the Queue.
        :param lcu_queue: LCU dictionary containing information about the queue.
        """
        self.__id = lcu_queue["id"]
        self.__name = lcu_queue["name"]
        self.__gamemode = lcu_queue["gameMode"]

    def id(self) -> int:
        """
        :return: the id of the queue.
        """
        return self.__id

    def name(self) -> str:
        """
        :return: the name of the queue.
        """
        return self.__name if self.__name is not None else "Unknown"

    def gamemode(self) -> str:
        """
        :return: the gamemode of the queue.
        """
        return self.__gamemode

    def __eq__(self, __value):
        return self.__id == __value.id() if isinstance(__value, Queue) else super().__eq__(__value)

    def __repr__(self):
        return f"Queue(id={self.id()}, name={self.name()}, gamemode={self.gamemode()})"
