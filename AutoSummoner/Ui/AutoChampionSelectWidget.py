"""Module containing the auto champion select configuration widget."""
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QFile
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QInputDialog, QListWidgetItem, QComboBox, QCheckBox, \
    QMessageBox

from AutoSummoner.Config.Configuration import Configuration
from AutoSummoner.Config.MainFeatures import MainFeatures
from AutoSummoner.Config.Features.ConfigAutoChampionSelect import ConfigAutoChampionSelect
from AutoSummoner.Config.Features.ConfigAutoChampionSelectProfile import ConfigAutoChampionSelectProfile
from AutoSummoner.LcuInterface.Assets.Champion import Champion
from AutoSummoner.LcuInterface.Assets.Queue import Queue
from AutoSummoner.LcuInterface.Assets.Rune import Rune
from AutoSummoner.LcuInterface.Assets.Spell import Spell
from AutoSummoner.Ui.EditProfileDialog import EditProfileDialog


class AutoChampionSelectWidget(QWidget):
    """Subwidget of the AutoSummoner main window, showing the auto champion select configuration."""

    # pylint: disable=too-many-instance-attributes
    __config = Configuration()
    configUpdatedSignal = pyqtSignal()

    __champions_dict: dict[int:Champion] = {}
    __summoner_spells_dict: dict[int: Spell] = {}

    __queues_dict: dict[int:Queue] = {}
    __runes_dict: dict[int:Rune] = {}

    __previous_summoner_spell_1: int = None
    __previous_summoner_spell_2: int = None

    def __init__(self, parent=None):
        """
        Initializes the widget UI and links UI elements to variables.
        :param parent: The parent widget
        """
        super().__init__(parent)

        # Loading UI and linking elements
        ui_file = QFile(":/designer/auto_champion_select_widget.ui")
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self.auto_champion_select_champion_profile_combobox: QComboBox = self.findChild(QComboBox,"auto_champion_select_champion_profile_combobox")
        self.auto_champion_select_champion_profile_add_button: QPushButton = self.findChild(QPushButton, "auto_champion_select_champion_profile_add_button")
        self.auto_champion_select_champion_profile_edit_button: QPushButton = self.findChild(QPushButton, "auto_champion_select_champion_profile_edit_button")
        self.auto_champion_select_champion_profile_remove_button: QPushButton = self.findChild(QPushButton, "auto_champion_select_champion_profile_remove_button")

        self.auto_champion_select_champion_ban_list: QListWidget = self.findChild(QListWidget, 'auto_champion_select_champion_ban_list')
        self.auto_champion_select_champion_ban_list.model().rowsMoved.connect(self.__save_champions_ban_config)
        self.auto_champion_select_champion_ban_add_button: QPushButton = self.findChild(QPushButton, 'auto_champion_select_champion_ban_add_button')
        self.auto_champion_select_champion_ban_remove_button: QPushButton = self.findChild(QPushButton, 'auto_champion_select_champion_ban_remove_button')

        self.auto_champion_select_champion_pick_list: QListWidget = self.findChild(QListWidget, 'auto_champion_select_champion_pick_list')
        self.auto_champion_select_champion_pick_list.model().rowsMoved.connect(self.__save_champions_pick_config)
        self.auto_champion_select_champion_pick_add_button: QPushButton = self.findChild(QPushButton, 'auto_champion_select_champion_pick_add_button')
        self.auto_champion_select_champion_pick_remove_button: QPushButton = self.findChild(QPushButton, 'auto_champion_select_champion_pick_remove_button')

        self.auto_champion_select_champion_summoner_spell_combobox_1: QComboBox = self.findChild(QComboBox, 'auto_champion_select_champion_summoner_spell_combobox_1')
        self.auto_champion_select_champion_summoner_spell_combobox_2: QComboBox = self.findChild(QComboBox, 'auto_champion_select_champion_summoner_spell_combobox_2')
        self.auto_champion_select_champion_summoner_spell_unique_checkbox: QCheckBox = self.findChild(QCheckBox, 'auto_champion_select_champion_summoner_spell_unique_checkbox')

        self.auto_champion_select_champion_rune_combobox: QComboBox = self.findChild(QComboBox, 'auto_champion_select_champion_rune_combobox')
        self.auto_champion_select_champion_rune_unique_checkbox: QCheckBox = self.findChild(QCheckBox, 'auto_champion_select_champion_rune_unique_checkbox')

    @pyqtSlot()
    def load_config(self) -> None:
        """
        Loads the user configuration and updates the UI accordingly.
        """
        self.__config.load_config()

        config_auto_champion_select: ConfigAutoChampionSelect = self.__config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT)
        previous_profile = self.__get_current_profile()
        self.auto_champion_select_champion_profile_combobox.clear()
        for index, profile in enumerate(config_auto_champion_select.get_all_profiles()):
            self.auto_champion_select_champion_profile_combobox.addItem(profile.get_name(), profile.get_id())
            if previous_profile is not None and profile == previous_profile:
                self.auto_champion_select_champion_profile_combobox.setCurrentIndex(index)

    @pyqtSlot(list)
    def on_lcuWorker_updateQueues(self, queue_list: list[Queue]) -> None:
        """
        Called by the LCU worker, updates the widget's queue list.
        :param queue_list: list of available queues for the current League account
        """
        # pylint: disable=invalid-name
        self.__queues_dict = {queue.id(): queue for queue in queue_list}

    @pyqtSlot(list)
    def on_lcuWorker_updateRunes(self, rune_list: list[Rune]) -> None:
        """
        Called by the LCU worker, updates the widget's rune list and UI accordingly.
        :param rune_list: list of runes for the current League account.
        """
        # pylint: disable=invalid-name
        self.__runes_dict = {rune.id(): rune for rune in rune_list}
        self.__update_runes_combobox()

    @pyqtSlot()
    def on_auto_champion_select_champion_profile_add_button_clicked(self) -> None:
        """
        Called when clicking the "Add" profile button.
        """
        edit_profile_dialog = EditProfileDialog(self.__queues_dict, parent=self)
        edit_profile_dialog.accepted.connect(self.on_edit_profile_dialog_accepted)
        edit_profile_dialog.show()

    @pyqtSlot()
    def on_auto_champion_select_champion_profile_edit_button_clicked(self) -> None:
        """
        Called when clicking the "Edit" profile button.
        """
        edit_profile_dialog = EditProfileDialog(self.__queues_dict,
                                                existing_profile_config=self.__get_current_profile(), parent=self)
        edit_profile_dialog.accepted.connect(self.on_edit_profile_dialog_accepted)
        edit_profile_dialog.show()

    @pyqtSlot()
    def on_edit_profile_dialog_accepted(self) -> None:
        """
        Called when the edit profile dialog is accepted and saves the new profile configuration.
        """
        edit_profile_dialog: EditProfileDialog = self.sender()
        profile_name = edit_profile_dialog.get_profile_name()
        if len(profile_name) == 0:
            QMessageBox.critical(self, "Profile error", "Profile name cannot be empty !")
            return

        profile_id = edit_profile_dialog.get_existing_profile_id()
        if profile_id is None:
            profile = self.__config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT).generate_profile()
        else:
            profile = self.__config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT).get_config_for_profile(profile_id)

        profile.set_name(profile_name)
        profile.set_queues_id(edit_profile_dialog.get_profile_queues_id())
        profile.set_positions(edit_profile_dialog.get_profile_positions())

        if edit_profile_dialog.get_existing_profile_id() is None:
            self.auto_champion_select_champion_profile_combobox.addItem(profile.get_name(), profile.get_id())
            self.auto_champion_select_champion_profile_combobox.setCurrentIndex(self.auto_champion_select_champion_profile_combobox.count()-1)
        else:
            self.auto_champion_select_champion_profile_combobox.setItemText(self.auto_champion_select_champion_profile_combobox.currentIndex(), profile_name)
        self.configUpdatedSignal.emit()

    @pyqtSlot()
    def on_auto_champion_select_champion_profile_remove_button_clicked(self) -> None:
        """
        Called when clicking the "Remove" profile button.
        """
        index = self.auto_champion_select_champion_profile_combobox.currentIndex()
        if index < 0:
            return

        profile_id = self.auto_champion_select_champion_profile_combobox.itemData(index, Qt.ItemDataRole.UserRole)
        self.__config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT).remove_profile(profile_id)
        self.auto_champion_select_champion_profile_combobox.removeItem(index)
        self.configUpdatedSignal.emit()

    def __get_current_profile(self) -> ConfigAutoChampionSelectProfile | None:
        """
        :return: the id of the current selected profile in the "Profile" combobox.
        """
        profile_id = self.auto_champion_select_champion_profile_combobox.currentData(Qt.ItemDataRole.UserRole)
        return None if profile_id is None else self.__config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT).get_config_for_profile(profile_id)

    @pyqtSlot(int)
    def on_auto_champion_select_champion_profile_combobox_currentIndexChanged(self) -> None:
        """
        Called when the current selected item in the "Profile" combobox changes.
        Updates the rest of the UI with data from the profile's configuration.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        profile = self.__get_current_profile()
        ui_elements = [self.auto_champion_select_champion_profile_combobox,
                       self.auto_champion_select_champion_profile_edit_button,
                       self.auto_champion_select_champion_profile_remove_button,
                       self.auto_champion_select_champion_ban_list,
                       self.auto_champion_select_champion_ban_remove_button,
                       self.auto_champion_select_champion_pick_list,
                       self.auto_champion_select_champion_pick_remove_button,
                       self.auto_champion_select_champion_summoner_spell_unique_checkbox,
                       self.auto_champion_select_champion_rune_combobox,
                       self.auto_champion_select_champion_rune_unique_checkbox]

        for ui_element in ui_elements:
            ui_element.setEnabled(profile is not None)

        self.auto_champion_select_champion_ban_add_button.setEnabled(profile is not None and len(self.__champions_dict) > 0)
        self.auto_champion_select_champion_pick_add_button.setEnabled(profile is not None and len(self.__champions_dict) > 0)

        if profile is None:
            self.auto_champion_select_champion_ban_list.clear()
            self.auto_champion_select_champion_pick_list.clear()
            return
        champions_ban_id = profile.get_champions_ban_id()
        self.auto_champion_select_champion_ban_list.clear()
        for champion_id in champions_ban_id:
            champion_name = self.__champions_dict[champion_id].name() if champion_id in self.__champions_dict.keys() else f'#{champion_id}'
            item = QListWidgetItem(champion_name, self.auto_champion_select_champion_ban_list)
            item.setData(Qt.ItemDataRole.UserRole, champion_id)
            self.auto_champion_select_champion_ban_list.addItem(item)

        champions_pick_id = profile.get_champions_pick_id()
        self.auto_champion_select_champion_pick_list.clear()
        for champion_id in champions_pick_id:
            champion_name = self.__champions_dict[champion_id].name() if champion_id in self.__champions_dict.keys() else f'#{champion_id}'
            item = QListWidgetItem(champion_name, self.auto_champion_select_champion_pick_list)
            item.setData(Qt.ItemDataRole.UserRole, champion_id)
            self.auto_champion_select_champion_pick_list.addItem(item)

        self.__update_summoner_spells_comboboxes()
        self.__update_runes_combobox()
        self.auto_champion_select_champion_summoner_spell_unique_checkbox.setChecked(profile.is_using_individual_summoner_spell())
        self.auto_champion_select_champion_rune_unique_checkbox.setChecked(profile.is_using_individual_rune())

    @pyqtSlot(dict)
    def set_champions_dict(self, champions_dict: dict) -> None:
        """
        Called by the LCU worker, updates the widget's champions list and UI accordingly.
        :param champions_dict: dictionary of champions.
        """
        self.__champions_dict = champions_dict
        buttons_enabled = len(champions_dict) > 0 and self.auto_champion_select_champion_ban_remove_button.isEnabled()
        self.auto_champion_select_champion_ban_add_button.setEnabled(buttons_enabled)
        self.auto_champion_select_champion_pick_add_button.setEnabled(buttons_enabled)

        for row in range(self.auto_champion_select_champion_ban_list.count()):
            item = self.auto_champion_select_champion_ban_list.item(row)
            champion_id = item.data(Qt.ItemDataRole.UserRole)
            if champion_id in self.__champions_dict.keys():
                item.setText(self.__champions_dict[champion_id].name())

        for row in range(self.auto_champion_select_champion_pick_list.count()):
            item = self.auto_champion_select_champion_pick_list.item(row)
            champion_id = item.data(Qt.ItemDataRole.UserRole)
            if champion_id in self.__champions_dict.keys():
                item.setText(self.__champions_dict[champion_id].name())

    @pyqtSlot(dict)
    def set_summoner_spells_dict(self, summoner_spells_dict: dict) -> None:
        """
        Called by the LCU worker, updates the widget's summoner spells dictionary and UI accordingly.
        :param summoner_spells_dict: dictionary of summoner spells.
        """
        self.__summoner_spells_dict = summoner_spells_dict
        self.__update_summoner_spells_comboboxes()

    def __ask_user_to_select_champion(self, title: str = "Select a champion",
                                      label: str = "Select a champion :",
                                      filtered_out_champions_id: list[int] = None) -> Champion | None:
        """
        Shows a dialog with a list of champions and ask the user to pick one.
        :param title: Title of the dialog.
        :param label: Text of the dialog.
        :param filtered_out_champions_id: List of champions id to filter out of the champions list.
        :return: A Champion if one was selected or None if no champion was selected.
        """
        if filtered_out_champions_id is None:
            filtered_out_champions_id = []
        champion_names_dict = {champion.name(): champion for champion in self.__champions_dict.values()
                               if champion.id() not in filtered_out_champions_id}
        select_champion, ok = QInputDialog.getItem(self.parent(), title, label, champion_names_dict.keys(), 0, False)

        return champion_names_dict[select_champion] if ok else None

    @pyqtSlot()
    def on_auto_champion_select_champion_ban_add_button_clicked(self) -> None:
        """
        Called when clicking the add button under the "Champion ban" list.
        """
        champion = self.__ask_user_to_select_champion(label="Select a champion to ban :",
                                                      filtered_out_champions_id=self.__get_champions_ban_id_list() +
                                                                             self.__get_champions_pick_id_list())
        if champion is not None:
            item = QListWidgetItem(champion.name(), self.auto_champion_select_champion_ban_list)
            item.setData(Qt.ItemDataRole.UserRole, champion.id())
            self.auto_champion_select_champion_ban_list.addItem(item)
            self.__save_champions_ban_config()

    @pyqtSlot()
    def on_auto_champion_select_champion_ban_remove_button_clicked(self) -> None:
        """
        Called when clicking the remove button under the "Champion ban" list.
        """
        current_row = self.auto_champion_select_champion_ban_list.currentRow()
        if current_row >= 0:
            self.auto_champion_select_champion_ban_list.takeItem(current_row)
            self.__save_champions_ban_config()

    def __get_champions_ban_id_list(self) -> list[int]:
        """
        :return: list of champions ids to ban ordered by priority descending.
        """
        return [self.auto_champion_select_champion_ban_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.auto_champion_select_champion_ban_list.count())]

    @pyqtSlot()
    def __save_champions_ban_config(self) -> None:
        self.__get_current_profile().set_champions_ban_id(self.__get_champions_ban_id_list())
        self.configUpdatedSignal.emit()

    @pyqtSlot()
    def on_auto_champion_select_champion_pick_add_button_clicked(self) -> None:
        """
        Called when clicking the add button under the "Champion pick" list.
        """
        champion = self.__ask_user_to_select_champion(label="Select a champion to pick :",
                                                      filtered_out_champions_id=self.__get_champions_ban_id_list() +
                                                                             self.__get_champions_pick_id_list())
        if champion is not None:
            item = QListWidgetItem(champion.name(), self.auto_champion_select_champion_pick_list)
            item.setData(Qt.ItemDataRole.UserRole, champion.id())
            self.auto_champion_select_champion_pick_list.addItem(item)
            self.__save_champions_pick_config()

    @pyqtSlot()
    def on_auto_champion_select_champion_pick_remove_button_clicked(self) -> None:
        """
        Called when clicking the remove button under the "Champion pick" list.
        """
        current_row = self.auto_champion_select_champion_pick_list.currentRow()
        if current_row >= 0:
            self.auto_champion_select_champion_pick_list.takeItem(current_row)
            self.__save_champions_pick_config()

    @pyqtSlot()
    def on_auto_champion_select_champion_pick_list_itemSelectionChanged(self) -> None:
        """
        Called when a champion is selected in the "Champion pick" list.
        """
        # pylint: disable=invalid-name
        if self.auto_champion_select_champion_summoner_spell_unique_checkbox.isChecked():
            self.__update_summoner_spells_comboboxes()
        if self.auto_champion_select_champion_rune_unique_checkbox.isChecked():
            self.__update_runes_combobox()

    def __get_champions_pick_id_list(self) -> list[int]:
        """
        :return: list of champions ids to pick ordered by priority descending.
        """
        return [self.auto_champion_select_champion_pick_list.item(i).data(Qt.ItemDataRole.UserRole)
                for i in range(self.auto_champion_select_champion_pick_list.count())]

    @pyqtSlot()
    def __save_champions_pick_config(self) -> None:
        """
        Saves the champions pick configuration.
        """
        self.__get_current_profile().set_champions_pick_id(self.__get_champions_pick_id_list())
        self.configUpdatedSignal.emit()

    def __update_summoner_spells_comboboxes(self) -> None:
        """
        Updates the summoner spells comboboxes and show the list of summoner spells, select the one requested by the user.
        """
        self.auto_champion_select_champion_summoner_spell_combobox_1.clear()
        self.auto_champion_select_champion_summoner_spell_combobox_2.clear()
        self.__previous_summoner_spell_1 = None
        self.__previous_summoner_spell_2 = None

        current_profile = self.__get_current_profile()
        if current_profile is not None:
            if current_profile.is_using_individual_summoner_spell():
                selected_champion_pick = self.auto_champion_select_champion_pick_list.selectedItems()
                if len(selected_champion_pick) > 0:
                    current_profile_summoner_spells_id = current_profile.get_summoner_spells_id_per_champion_id(selected_champion_pick[0].data(Qt.ItemDataRole.UserRole))
                else:
                    current_profile_summoner_spells_id = None
            else:
                current_profile_summoner_spells_id = current_profile.get_summoner_spells_id_global()

            queues = [queue for queue in self.__queues_dict.values() if queue.id() in current_profile.get_queues_id()]
            queues_gamemode = {queue.gamemode() for queue in queues}

            filtered_summoner_spells_dict = {spell_id: spell for spell_id, spell in self.__summoner_spells_dict.items()
                                             if any(gamemode in queues_gamemode for gamemode in spell.gamemodes())}

            if len(filtered_summoner_spells_dict) > 0:
                for spell in filtered_summoner_spells_dict.values():
                    self.auto_champion_select_champion_summoner_spell_combobox_1.addItem(spell.name(), spell.id())
                    self.auto_champion_select_champion_summoner_spell_combobox_2.addItem(spell.name(), spell.id())
                    if current_profile_summoner_spells_id is not None:
                        if current_profile_summoner_spells_id[0] == spell.id():
                            self.auto_champion_select_champion_summoner_spell_combobox_1.setCurrentIndex(self.auto_champion_select_champion_summoner_spell_combobox_1.count()-1)
                        if current_profile_summoner_spells_id[1] == spell.id():
                            self.auto_champion_select_champion_summoner_spell_combobox_2.setCurrentIndex(self.auto_champion_select_champion_summoner_spell_combobox_2.count()-1)
                self.auto_champion_select_champion_summoner_spell_combobox_1.setEnabled(not current_profile.is_using_individual_summoner_spell() or len(selected_champion_pick) > 0)
                self.auto_champion_select_champion_summoner_spell_combobox_2.setEnabled(not current_profile.is_using_individual_summoner_spell() or len(selected_champion_pick) > 0)
                if current_profile_summoner_spells_id is None:
                    self.auto_champion_select_champion_summoner_spell_combobox_2.setCurrentIndex(min(len(filtered_summoner_spells_dict)-1, 1))
            else:
                self.auto_champion_select_champion_summoner_spell_combobox_1.setEnabled(False)
                self.auto_champion_select_champion_summoner_spell_combobox_2.setEnabled(False)
                if current_profile_summoner_spells_id is not None:
                    self.auto_champion_select_champion_summoner_spell_combobox_1.addItem(f"#{current_profile_summoner_spells_id[0]}", current_profile_summoner_spells_id[0])
                    self.auto_champion_select_champion_summoner_spell_combobox_2.addItem(f"#{current_profile_summoner_spells_id[1]}", current_profile_summoner_spells_id[1])
        else:
            self.auto_champion_select_champion_summoner_spell_combobox_1.setEnabled(False)
            self.auto_champion_select_champion_summoner_spell_combobox_2.setEnabled(False)
        self.__previous_summoner_spell_1 = self.auto_champion_select_champion_summoner_spell_combobox_1.currentIndex()
        self.__previous_summoner_spell_2 = self.auto_champion_select_champion_summoner_spell_combobox_2.currentIndex()

    @pyqtSlot(int)
    def on_auto_champion_select_champion_summoner_spell_unique_checkbox_stateChanged(self, state: Qt.CheckState) -> None:
        """
        Called when the "Unique per champion pick" summoner spells checkbox state changes.
        :param state: Current state of the checkbox (Checked or Unchecked).
        """
        # pylint: disable=invalid-name
        self.__get_current_profile().set_using_individual_summoner_spell(state == Qt.CheckState.Checked)
        self.__update_summoner_spells_comboboxes()
        self.configUpdatedSignal.emit()

    @pyqtSlot(int)
    def on_auto_champion_select_champion_summoner_spell_combobox_1_currentIndexChanged(self, index: int) -> None:
        """
        Called when the currently selected item in the "Summoner spell 1" combobox changes.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        if index >= 0:
            if index == self.auto_champion_select_champion_summoner_spell_combobox_2.currentIndex() and self.__previous_summoner_spell_1 is not None:
                self.auto_champion_select_champion_summoner_spell_combobox_2.setCurrentIndex(self.__previous_summoner_spell_1)
            else:
                self.__save_summoner_spells()
            self.__previous_summoner_spell_1 = index

    @pyqtSlot(int)
    def on_auto_champion_select_champion_summoner_spell_combobox_2_currentIndexChanged(self, index: int) -> None:
        """
        Called when the currently selected item in the "Summoner spell 2" combobox changes.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        if index >= 0:
            if index == self.auto_champion_select_champion_summoner_spell_combobox_1.currentIndex() and self.__previous_summoner_spell_2 is not None:
                self.auto_champion_select_champion_summoner_spell_combobox_1.setCurrentIndex(self.__previous_summoner_spell_2)
            else:
                self.__save_summoner_spells()
            self.__previous_summoner_spell_2 = index

    def __save_summoner_spells(self) -> None:
        """
        Saves the current summoner spell configuration as selected by the user in the UI.
        """
        if self.auto_champion_select_champion_summoner_spell_combobox_1.currentIndex() < 0 or \
           self.auto_champion_select_champion_summoner_spell_combobox_2.currentIndex() < 0 or \
           not self.auto_champion_select_champion_summoner_spell_combobox_1.isEnabled() or \
           not self.auto_champion_select_champion_summoner_spell_combobox_2.isEnabled():
            return

        summoner_spell_1_id = self.auto_champion_select_champion_summoner_spell_combobox_1.currentData()

        summoner_spell_2_id = self.auto_champion_select_champion_summoner_spell_combobox_2.currentData()
        if self.auto_champion_select_champion_summoner_spell_unique_checkbox.isChecked():
            selected_champion_pick = self.auto_champion_select_champion_pick_list.selectedItems()
            if len(selected_champion_pick) > 0:
                self.__get_current_profile().set_summoner_spells_id_per_champion_id(selected_champion_pick[0].data(Qt.ItemDataRole.UserRole),
                                                                                    summoner_spell_1_id, summoner_spell_2_id)
        else:
            self.__get_current_profile().set_summoner_spells_id_global(summoner_spell_1_id, summoner_spell_2_id)

        self.configUpdatedSignal.emit()

    def __update_runes_combobox(self) -> None:
        """
        Update the runes combobox and show the list of runes that are available, select the one requested by the user.
        """
        self.auto_champion_select_champion_rune_combobox.clear()
        current_profile = self.__get_current_profile()
        if current_profile is not None:
            if current_profile.is_using_individual_rune():
                selected_champion_pick = self.auto_champion_select_champion_pick_list.selectedItems()
                if len(selected_champion_pick) > 0:
                    current_profile_rune_id = current_profile.get_rune_id_per_champion(selected_champion_pick[0].data(Qt.ItemDataRole.UserRole))
                else:
                    current_profile_rune_id = 0
            else:
                current_profile_rune_id = current_profile.get_rune_id_global()

            if len(self.__runes_dict) > 0:
                for rune in self.__runes_dict.values():
                    self.auto_champion_select_champion_rune_combobox.addItem(rune.name(), rune.id())
                    if current_profile_rune_id == rune.id():
                        self.auto_champion_select_champion_rune_combobox.setCurrentIndex(self.auto_champion_select_champion_rune_combobox.count() - 1)
                self.auto_champion_select_champion_rune_combobox.setEnabled(not current_profile.is_using_individual_rune() or len(selected_champion_pick) > 0)
                if current_profile_rune_id == 0:
                    self.on_auto_champion_select_champion_rune_combobox_currentIndexChanged(0)
            else:
                self.auto_champion_select_champion_rune_combobox.setEnabled(False)
                if current_profile_rune_id > 0:
                    self.auto_champion_select_champion_rune_combobox.addItem(f"#{current_profile_rune_id}", current_profile_rune_id)
        else:
            self.auto_champion_select_champion_rune_combobox.setEnabled(False)

    @pyqtSlot(int)
    def on_auto_champion_select_champion_rune_unique_checkbox_stateChanged(self, state: Qt.CheckState) -> None:
        """
        Called when the "Unique per champion pick" rune checkbox state changes.
        :param state: Current state of the checkbox (Checked or Unchecked).
        """
        # pylint: disable=invalid-name
        self.__get_current_profile().set_using_individual_rune(state == Qt.CheckState.Checked)
        self.__update_runes_combobox()
        self.configUpdatedSignal.emit()

    @pyqtSlot(int)
    def on_auto_champion_select_champion_rune_combobox_currentIndexChanged(self, index: int) -> None:
        """
        Called when the currently selected item in the "Rune" combobox changes.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        if index < 0 or not self.auto_champion_select_champion_rune_combobox.isEnabled():
            return

        rune_id = self.auto_champion_select_champion_rune_combobox.currentData(Qt.ItemDataRole.UserRole)

        if self.auto_champion_select_champion_rune_unique_checkbox.isChecked():
            selected_champion_pick = self.auto_champion_select_champion_pick_list.selectedItems()
            if len(selected_champion_pick) > 0:
                self.__get_current_profile().set_rune_id_per_champion(selected_champion_pick[0].data(Qt.ItemDataRole.UserRole),
                                                                      rune_id)
        else:
            self.__get_current_profile().set_rune_id_global(rune_id)

        self.configUpdatedSignal.emit()
