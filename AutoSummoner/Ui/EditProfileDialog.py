"""Module containing the edit profile dialog."""
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSlot, QFile
from PyQt5.QtWidgets import QDialog, QLineEdit, QListWidget, QCheckBox, QListWidgetItem

from AutoSummoner.Config.Features.ConfigAutoChampionSelectProfile import ConfigAutoChampionSelectProfile
from AutoSummoner.LcuInterface.Position import Position
from AutoSummoner.LcuInterface.Assets.Queue import Queue


class EditProfileDialog(QDialog):
    """Dialog for adding profiles and editing profiles information."""

    __queues_dict: dict[int:Queue] = {}
    __existing_profile_id: int = None

    def __init__(self, queues_dict: dict, existing_profile_config: ConfigAutoChampionSelectProfile = None, parent=None) -> None:
        """
        Initializes the edit profile dialog.
        :param queues_dict: list of available queues.
        :param existing_profile_config: existing profile configuration in case the user wants to edit an existing profile.
        :param parent: parent widget.
        """
        super().__init__(parent)
        self.__queues_dict = queues_dict
        self.__existing_profile_id = existing_profile_config.get_id() if existing_profile_config is not None else None

        # Load UI
        ui_file = QFile(":/designer/dialog_edit_profile.ui")
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self.dialog_edit_profile_name_lineedit: QLineEdit = self.findChild(QLineEdit, "dialog_edit_profile_name_lineedit")

        self.dialog_edit_profile_queues_list: QListWidget = self.findChild(QListWidget, "dialog_edit_profile_queues_list")

        self.dialog_edit_profile_positions_list: QListWidget = self.findChild(QListWidget, "dialog_edit_profile_positions_list")
        self.dialog_edit_profile_positions_any_checkbox: QCheckBox = self.findChild(QCheckBox, "dialog_edit_profile_positions_any_checkbox")

        if existing_profile_config is not None:
            self.dialog_edit_profile_name_lineedit.setText(existing_profile_config.get_name())
            checked_queues_id = existing_profile_config.get_queues_id()
            checked_positions = existing_profile_config.get_positions()
        else:
            checked_queues_id = []
            checked_positions = []

        for position in Position.get_all_positions():
            item = QListWidgetItem(position.value, self.dialog_edit_profile_positions_list)
            item.setData(Qt.ItemDataRole.UserRole, position.get_index())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if position in checked_positions:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.dialog_edit_profile_positions_list.addItem(item)

        if existing_profile_config is not None:
            self.dialog_edit_profile_positions_any_checkbox.setChecked(len(existing_profile_config.get_positions()) == 0)
        else:
            self.dialog_edit_profile_positions_any_checkbox.setChecked(True)

        for queue in self.__queues_dict.values():
            item = QListWidgetItem(queue.name(), self.dialog_edit_profile_queues_list)
            item.setData(Qt.ItemDataRole.UserRole, queue.id())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if queue.id() in checked_queues_id:
                item.setCheckState(Qt.CheckState.Checked)
                checked_queues_id.remove(queue.id())
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.dialog_edit_profile_queues_list.addItem(item)

        for queue_id in checked_queues_id:
            item = QListWidgetItem(f"#{queue_id}", self.dialog_edit_profile_queues_list)
            item.setData(Qt.ItemDataRole.UserRole, queue_id)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)
            self.dialog_edit_profile_queues_list.addItem(item)

        self.dialog_edit_profile_queues_list.sortItems()

    def get_profile_name(self) -> str:
        """
        :return: name of the profile.
        """
        return self.dialog_edit_profile_name_lineedit.text()

    def get_profile_queues_id(self) -> list[int]:
        """
        :return: list of queues id associated with this profile.
        """
        result = []
        for row in range(self.dialog_edit_profile_queues_list.count()):
            item = self.dialog_edit_profile_queues_list.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                result.append(item.data(Qt.ItemDataRole.UserRole))
        return result

    def get_profile_positions(self) -> list[Position]:
        """
        :return: list of positions assigned to this profile or empty list if no positions are assigned (or "Any" is assigned).
        """
        if self.dialog_edit_profile_positions_any_checkbox.isChecked():
            return []

        result = []
        for row in range(self.dialog_edit_profile_positions_list.count()):
            item = self.dialog_edit_profile_positions_list.item(row)
            if item.checkState() == Qt.CheckState.Checked:
                result.append(Position.from_index(item.data(Qt.ItemDataRole.UserRole)))
        return result

    def get_existing_profile_id(self) -> int | None:
        """
        :return: the id of the profile if it exists, otherwise returns None.
        """
        return self.__existing_profile_id

    @pyqtSlot(int)
    def on_dialog_edit_profile_positions_any_checkbox_stateChanged(self, state: Qt.CheckState) -> None:
        """
        Called when the "Any" position checkbox state changes.
        :param state: Current state of the checkbox (Checked or Unchecked).
        """
        # pylint: disable=invalid-name
        self.dialog_edit_profile_positions_list.setEnabled(state == Qt.CheckState.Unchecked)
        items = [self.dialog_edit_profile_positions_list.item(row) for row in range(self.dialog_edit_profile_positions_list.count())]
        for item in items:
            item.setCheckState(state)
