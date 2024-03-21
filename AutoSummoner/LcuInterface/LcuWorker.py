"""This module contains the LcuWorker class."""
import asyncio

from PyQt5.QtCore import QObject, pyqtSignal
from aiohttp import ClientResponse
from lcu_driver import Connector
from lcu_driver.connection import Connection
from lcu_driver.events.responses import WebsocketEventResponse

from AutoSummoner.Config.Configuration import Configuration
from AutoSummoner.Config.Features.ConfigAutoChampionSelectProfile import ConfigAutoChampionSelectProfile
from AutoSummoner.Config.MainFeatures import MainFeatures
from AutoSummoner.LcuInterface.Assets.Queue import Queue
from AutoSummoner.LcuInterface.Assets.Rune import Rune


class LcuWorker(QObject):
    """Class of the LCU Worker, responsible for communicating with the League client."""

    connector: Connector = None
    event_loop = None
    config = Configuration()

    # Signals
    update_status = pyqtSignal(str)
    update_queues = pyqtSignal(list)
    update_owned_champions = pyqtSignal(list)
    update_runes = pyqtSignal(list)

    __last_queue_id = None

    def load_config(self) -> None:
        """
        Loads the configuration.
        """
        self.config.load_config()

    def run(self) -> None:
        """
        Main function, runs in a background thread.
        """
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)

        self.connector = Connector(loop=self.event_loop)
        self.connector.ready(self.connect)
        self.connector.ws.register(uri='/lol-gameflow/v1/session', event_types=('UPDATE',))(self.gameflow_changed)
        self.connector.ws.register(uri='/lol-lobby/v2/lobby', event_types=('UPDATE',))(self.lobby_updated)
        self.connector.ws.register(uri='/lol-matchmaking/v1/ready-check', event_types=('UPDATE',))(self.matchmaking_updated)
        self.connector.ws.register(uri='/lol-champ-select/v1/session', event_types=('UPDATE',))(self.champion_select_updated)
        self.connector.start()

    async def connect(self, connection: Connection) -> None:
        """
        Called when the LCU connection is established, updates the UI with the current gameflow.
        :param connection: LCU connection.
        """
        self.update_status.emit("Connected to League Client, loading configuration...")

        # Loading queues
        queues: ClientResponse = await connection.request('get', '/lol-game-queues/v1/queues')
        queues_list = await queues.json()
        queues_list = [item for item in queues_list if item["queueAvailability"] == "Available"]
        queues_list = [Queue(item) for item in queues_list]
        self.update_queues.emit(queues_list)

        # Loading champions
        owned_champions: ClientResponse = await connection.request('get', '/lol-champions/v1/owned-champions-minimal')
        owned_champions_list: list[dict] = await owned_champions.json()
        self.update_owned_champions.emit(owned_champions_list)

        # Loading runes
        runes: ClientResponse = await connection.request('get', '/lol-perks/v1/pages')
        runes_list = await runes.json()
        runes_list = [Rune(item) for item in runes_list]
        self.update_runes.emit(runes_list)

        self.update_status.emit("Connected to League Client, awaiting gameflow...")
        gameflow_json: ClientResponse = await connection.request('get', '/lol-gameflow/v1/session')
        gameflow_json: dict = await gameflow_json.json()
        await self.process_updated_gameflow(connection, gameflow_json)

        if "phase" in gameflow_json:
            if gameflow_json["phase"] == "Lobby":
                lobby_status: ClientResponse = await connection.request('get', '/lol-lobby/v2/lobby')
                lobby_status_json = await lobby_status.json()
                await self.process_updated_lobby(connection, lobby_status_json)
            elif gameflow_json["phase"] == "Matchmaking":
                matchmaking_status: ClientResponse = await connection.request('get', '/lol-matchmaking/v1/ready-check')
                matchmaking_status_json = await matchmaking_status.json()
                await self.process_updated_matchmaking(connection, matchmaking_status_json)
            elif gameflow_json["phase"] == "ChampSelect":
                champion_select_status: ClientResponse = await connection.request('get', '/lol-champ-select/v1/session')
                champion_select_status_json = await champion_select_status.json()
                await self.process_updated_champion_select(connection, champion_select_status_json)

    async def gameflow_changed(self, connection: Connection, event: WebsocketEventResponse) -> None:
        """
        Called when the League gameflow changes.
        :param connection: LCU connection.
        :param event: gameflow changed event.
        """
        await self.process_updated_gameflow(connection, event.data)

    async def process_updated_gameflow(self, connection: Connection, gameflow: dict) -> None:
        """
        Processes the updated gameflow event and act depending on the user configuration.
        :param connection: LCU connection.
        :param gameflow: current League gameflow dictionary.
        """
        config_auto_lobby = self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY)

        if "phase" not in gameflow or gameflow["phase"] == "None":
            self.__last_queue_id = None
            auto_select_queue_id = config_auto_lobby.get_auto_select_queue_id()
            if config_auto_lobby.is_enabled() and config_auto_lobby.is_auto_select_queue_enabled() and auto_select_queue_id > 0:
                self.update_status.emit("Connected to League Client, changing lobby...")
                await connection.request('post', '/lol-lobby/v2/lobby', data={"queueId": auto_select_queue_id})
            else:
                self.update_status.emit("Connected to League Client, waiting for lobby...")
        elif gameflow["phase"] == "Lobby":
            self.__last_queue_id = None
            lobby_status: ClientResponse = await connection.request('get', '/lol-lobby/v2/lobby')
            lobby_status_json = await lobby_status.json()
            await self.process_updated_lobby(connection, lobby_status_json)
        elif gameflow["phase"] == "Matchmaking":
            self.__last_queue_id = None
            self.update_status.emit("Connected to League Client, matchmaking in progress...")
        elif gameflow["phase"] == "ChampSelect":
            self.__last_queue_id = gameflow["gameData"]["queue"]["id"]
            champion_select_status: ClientResponse = await connection.request('get', '/lol-champ-select/v1/session')
            champion_select_status_json = await champion_select_status.json()
            await self.process_updated_champion_select(connection, champion_select_status_json)
        else:
            self.update_status.emit("Connected to League Client, gameflow phase : " + gameflow["phase"])

    async def lobby_updated(self, connection: Connection, event: WebsocketEventResponse) -> None:
        """
        Called when the League lobby changes.
        :param connection: LCU connection.
        :param event: lobby updated event.
        """
        await self.process_updated_lobby(connection, event.data)

    async def process_updated_lobby(self, connection: Connection, lobby_state: dict) -> None:
        """
        Processes the lobby updated event and act depending on the user configuration.
        :param connection: LCU connection.
        :param lobby_state: current lobby state dictionary.
        """
        config_auto_lobby = self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY)
        auto_select_queue_id = config_auto_lobby.get_auto_select_queue_id()
        if config_auto_lobby.is_auto_select_queue_enabled() and 0 < auto_select_queue_id != lobby_state["gameConfig"]["queueId"]:
            self.update_status.emit("Connected to League Client, changing lobby...")
            await connection.request('post', '/lol-lobby/v2/lobby', data={"queueId": auto_select_queue_id})
            return

        if config_auto_lobby.is_auto_select_roles_enabled():
            config_auto_select_roles_positions = config_auto_lobby.get_auto_select_roles()
            if lobby_state["localMember"]["firstPositionPreference"] != "" and lobby_state["localMember"]["secondPositionPreference"] != "" and \
                    (lobby_state["localMember"]["firstPositionPreference"] != config_auto_select_roles_positions[0].get_league_position_str() or
                     lobby_state["localMember"]["secondPositionPreference"] != config_auto_select_roles_positions[1].get_league_position_str()):
                self.update_status.emit("Connected to League Client, changing lobby roles...")
                await connection.request('put',
                                         '/lol-lobby/v2/lobby/members/localMember/position-preferences',
                                         data={"firstPreference": config_auto_select_roles_positions[0].get_league_position_str(),
                                               "secondPreference": config_auto_select_roles_positions[1].get_league_position_str()})
                return

        if lobby_state["canStartActivity"]:
            if self.config.get_feature_configuration(MainFeatures.AUTO_QUEUE).is_auto_start_queue_enabled():
                self.update_status.emit("Connected to League Client, starting matchmaking...")
                await connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
            else:
                self.update_status.emit("Connected to League Client, waiting for matchmaking...")
        else:
            self.update_status.emit("Connected to League Client, waiting for lobby to be ready...")

    async def matchmaking_updated(self, connection: Connection, event: WebsocketEventResponse) -> None:
        """
        Called when the matchmaking state is updated.
        :param connection: LCU connection.
        :param event: matchmaking updated event.
        """
        await self.process_updated_matchmaking(connection, event.data)

    async def process_updated_matchmaking(self, connection: Connection, matchmaking_state: dict) -> None:
        """
        Processes the matchmaking updated event and act depending on the user configuration.
        :param connection: LCU connection.
        :param matchmaking_state: current matchmaking state dictionary.
        """
        if matchmaking_state["state"] == "InProgress" and matchmaking_state["playerResponse"] == "None":
            if self.config.get_feature_configuration(MainFeatures.AUTO_QUEUE).is_auto_accept_match_enabled():
                self.update_status.emit("Connected to League Client, accepting matchmaking...")
                await connection.request('post', "/lol-matchmaking/v1/ready-check/accept")
            else:
                self.update_status.emit("Connected to League Client, waiting for accepting match...")
        elif matchmaking_state["state"] == "InProgress" and matchmaking_state["playerResponse"] == "Accepted":
            self.update_status.emit("Connected to League Client, waiting for other players accepting match...")

    async def champion_select_updated(self, connection: Connection, event: WebsocketEventResponse) -> None:
        """
        Called when the champion select is updated.
        :param connection: LCU connection.
        :param event: champion select updated event.
        """
        await self.process_updated_champion_select(connection, event.data)

    async def process_updated_champion_select(self, connection: Connection, champion_select_state: dict) -> None:
        """
        Processes the champion select updated event and act depending on the user configuration.
        :param connection: LCU connection.
        :param champion_select_state: current champion select state dictionary.
        """
        local_player_cell_id = champion_select_state["localPlayerCellId"]
        profile = self.__get_champion_select_profile(champion_select_state)
        if profile is None:
            self.update_status.emit("Connected to League Client, waiting for champion select (no profile found)...")
            return

        # Finding champion to pick
        banned_champions = self.__get_banned_champions(champion_select_state["actions"])
        picked_champions = self.__get_picked_champions(champion_select_state["actions"], local_player_cell_id)

        champion_to_pick = self.__get_champion_to_pick(profile, banned_champions, picked_champions)
        champion_to_ban = self.__get_champion_to_ban(profile, banned_champions, picked_champions)

        summoners_to_pick_id = self.__get_summoners_to_pick(profile, champion_to_pick)
        rune_to_pick_id = self.__get_rune_to_pick(profile, champion_to_pick)

        for action in champion_select_state["actions"]:
            for subaction in action:
                if subaction["actorCellId"] == local_player_cell_id and not subaction["completed"]:
                    if subaction["type"] == "ban" and subaction["isInProgress"]:
                        if champion_to_ban is not None:
                            self.update_status.emit("Connected to League Client, banning champion...")
                            response = await connection.request('patch', f"/lol-champ-select/v1/session/actions/{subaction['id']}", data={"championId": champion_to_ban})
                            if response.ok:
                                await connection.request('post', f"/lol-champ-select/v1/session/actions/{subaction['id']}/complete")
                                self.update_status.emit("Connected to League Client, waiting for pick...")
                        else:
                            print("champion_to_ban is None !")
                    elif subaction["type"] == "pick":
                        if champion_to_pick is not None:
                            response = None
                            if subaction["championId"] != champion_to_pick:
                                response = await connection.request('patch', f"/lol-champ-select/v1/session/actions/{subaction['id']}", data={"championId": champion_to_pick})
                            if subaction["isInProgress"] and (subaction["championId"] == champion_to_pick or (response is not None and response.ok)):
                                response = await connection.request('post',f"/lol-champ-select/v1/session/actions/{subaction['id']}/complete")
                                if response.ok:
                                    # Picking runes
                                    if rune_to_pick_id is not None:
                                        await connection.request('put', '/lol-perks/v1/currentpage', data=rune_to_pick_id)

                                    if summoners_to_pick_id is not None:
                                        await connection.request('patch', '/lol-champ-select/v1/session/my-selection', data={"spell1Id": summoners_to_pick_id[0], "spell2Id": summoners_to_pick_id[1]})

                                self.update_status.emit("Connected to League Client, waiting for game to start...")
                        else:
                            print("champion_to_pick is None !")

    def __get_champion_select_profile(self, champion_select_state: dict) -> ConfigAutoChampionSelectProfile | None:
        local_player_cell_id = champion_select_state["localPlayerCellId"]
        local_player_position = ""

        for player in champion_select_state["myTeam"]:
            if player["cellId"] == local_player_cell_id:
                local_player_position = player["assignedPosition"]

        return self.config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT).find_profile_config(self.__last_queue_id, local_player_position)

    @staticmethod
    def __get_banned_champions(champion_select_actions: list) -> list[int]:
        banned_champions = []
        for action in champion_select_actions:
            for subaction in action:
                if subaction["completed"] and subaction["type"] == "ban":
                    banned_champions.append(subaction["championId"])
        return banned_champions

    @staticmethod
    def __get_picked_champions(champion_select_actions: list, local_player_cell_id: int) -> list[int]:
        picked_champions = []
        for action in champion_select_actions:
            for subaction in action:
                if subaction["type"] == "pick" and subaction["actorCellId"] != local_player_cell_id:
                    picked_champions.append(subaction["championId"])
        return picked_champions

    @staticmethod
    def __get_champion_to_pick(profile: ConfigAutoChampionSelectProfile, banned_champions: list[int], picked_champions: list[int]) -> int | None:
        champions_to_pick = [champion for champion in profile.get_champions_pick_id() if
                             champion not in banned_champions and champion not in picked_champions]
        return champions_to_pick[0] if len(champions_to_pick) > 0 else None

    @staticmethod
    def __get_champion_to_ban(profile: ConfigAutoChampionSelectProfile, banned_champions: list[int], picked_champions: list[int]) -> int | None:
        champions_to_ban = [champion for champion in profile.get_champions_ban_id()
                            if champion not in picked_champions and champion not in banned_champions]
        return champions_to_ban[0] if len(champions_to_ban) > 0 else None

    @staticmethod
    def __get_summoners_to_pick(profile: ConfigAutoChampionSelectProfile, champion_to_pick: int) -> tuple[int, int] | None:
        if profile.is_using_individual_summoner_spell():
            if champion_to_pick is not None:
                return profile.get_summoner_spells_id_per_champion_id(champion_to_pick)
            return None
        return profile.get_summoner_spells_id_global()

    @staticmethod
    def __get_rune_to_pick(profile: ConfigAutoChampionSelectProfile, champion_to_pick: int) -> int | None:
        if profile.is_using_individual_rune():
            if champion_to_pick is not None:
                return profile.get_rune_id_per_champion(champion_to_pick)
            return None
        return profile.get_rune_id_global()
