"""Module containing the main window of AutoSummoner."""
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSlot, QFile
from PyQt5.QtWidgets import QMainWindow, QLabel, QCheckBox, QComboBox

from AutoSummoner.Config.Configuration import Configuration
from AutoSummoner.Config.MainFeatures import MainFeatures
from AutoSummoner.Config.Features.ConfigAutoChampionSelect import ConfigAutoChampionSelect
from AutoSummoner.Config.Features.ConfigAutoLobby import ConfigAutoLobby
from AutoSummoner.Config.Features.ConfigAutoQueue import ConfigAutoQueue
from AutoSummoner.LcuInterface.LcuWorker import LcuWorker
from AutoSummoner.LcuInterface.Position import Position
from AutoSummoner.LcuInterface.Assets.AssetsWorker import AssetsWorker
from AutoSummoner.LcuInterface.Assets.Queue import Queue
from AutoSummoner.Ui.AutoChampionSelectWidget import AutoChampionSelectWidget


class MainWindow(QMainWindow):
    """Main window of the AutoSummoner UI."""

    # pylint: disable=too-many-instance-attributes
    lcuWorker = LcuWorker()
    lcuThread = QThread()

    assertsWorker = AssetsWorker()
    assertsThread = QThread()

    config = Configuration()

    last_first_preference = None
    last_second_preference = None

    def __init__(self) -> None:
        """
        Initializes the UI and links UI elements to variables.
        """
        # pylint: disable=line-too-long
        super().__init__()

        # Load UI
        ui_file = QFile(":/designer/mainwindow.ui")
        ui_file.open(QFile.ReadOnly)
        uic.loadUi(ui_file, self)
        ui_file.close()

        self.main_status_label: QLabel = self.findChild(QLabel, 'main_status_label')
        self.main_mainfeatures_autolobby_checkbox: QCheckBox = self.findChild(QCheckBox, 'main_mainfeatures_autolobby_checkbox')
        self.main_mainfeatures_autoqueue_checkbox: QCheckBox = self.findChild(QCheckBox, 'main_mainfeatures_autoqueue_checkbox')
        self.main_mainfeatures_autochampionselect_checkbox: QCheckBox = self.findChild(QCheckBox, 'main_mainfeatures_autochampionselect_checkbox')

        self.main_autolobby_autoselectqueue_checkbox: QCheckBox = self.findChild(QCheckBox, 'main_autolobby_autoselectqueue_checkbox')
        self.main_autolobby_autoselectqueue_combobox: QComboBox = self.findChild(QComboBox, 'main_autolobby_autoselectqueue_combobox')

        self.main_autolobby_autoselectroles_checkbox: QCheckBox = self.findChild(QCheckBox, 'main_autolobby_autoselectroles_checkbox')
        self.main_autolobby_autoselectroles_firstpreference_combobox: QComboBox = self.findChild(QComboBox, 'main_autolobby_autoselectroles_firstpreference_combobox')
        self.main_autolobby_autoselectroles_secondpreference_combobox: QComboBox = self.findChild(QComboBox, 'main_autolobby_autoselectroles_secondpreference_combobox')

        self.main_autoqueue_auto_start_queue_checkbox: QCheckBox = self.findChild(QCheckBox,'main_autoqueue_auto_start_queue_checkbox')
        self.main_autoqueue_auto_accept_match_checkbox: QCheckBox = self.findChild(QCheckBox,'main_autoqueue_auto_accept_match_checkbox')

        self.main_autochampionselect_profile_widget: AutoChampionSelectWidget = self.findChild(AutoChampionSelectWidget, "main_autochampionselect_profile_widget")
        self.main_autochampionselect_profile_widget.configUpdatedSignal.connect(self.on_main_autochampionselect_profile_widget_config_updated)

        # Init UI
        for position in Position.get_all_positions():
            self.main_autolobby_autoselectroles_firstpreference_combobox.addItem(position.value)
            self.main_autolobby_autoselectroles_secondpreference_combobox.addItem(position.value)

        self.load_config()
        self.main_autochampionselect_profile_widget.load_config()

        # Init LCU
        self.lcuWorker.moveToThread(self.lcuThread)

        self.main_autochampionselect_profile_widget.configUpdatedSignal.connect(self.lcuWorker.load_config)
        self.lcuThread.started.connect(self.lcuWorker.run)
        self.lcuWorker.update_status.connect(self.on_lcu_worker_update_status)
        self.lcuWorker.update_queues.connect(self.on_lcuWorker_updateQueues)
        self.lcuWorker.update_queues.connect(self.main_autochampionselect_profile_widget.on_lcuWorker_updateQueues)
        self.lcuWorker.update_runes.connect(self.main_autochampionselect_profile_widget.on_lcuWorker_updateRunes)

        self.lcuThread.start()

        # Init AssertsWorker
        self.assertsWorker.moveToThread(self.assertsThread)
        self.assertsThread.started.connect(self.assertsWorker.run)
        self.assertsWorker.champions_loaded.connect(self.main_autochampionselect_profile_widget.set_champions_dict)
        self.assertsWorker.summoner_spells_loaded.connect(self.main_autochampionselect_profile_widget.set_summoner_spells_dict)

        self.assertsThread.start()

    def load_config(self) -> None:
        """
        Loads the user configuration and updates the UI accordingly.
        """
        self.config.load_config()
        config_auto_lobby: ConfigAutoLobby = self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY)
        config_auto_queue: ConfigAutoQueue = self.config.get_feature_configuration(MainFeatures.AUTO_QUEUE)
        config_auto_champion_select: ConfigAutoChampionSelect = self.config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT)

        self.main_mainfeatures_autolobby_checkbox.setChecked(config_auto_lobby.is_enabled())
        self.main_mainfeatures_autoqueue_checkbox.setChecked(config_auto_queue.is_enabled())
        self.main_mainfeatures_autochampionselect_checkbox.setChecked(config_auto_champion_select.is_enabled())

        self.main_autolobby_autoselectqueue_checkbox.setChecked(config_auto_lobby.is_auto_select_queue_enabled())

        self.main_autolobby_autoselectroles_checkbox.setChecked(config_auto_lobby.is_auto_select_roles_enabled())
        config_auto_select_roles_positions = config_auto_lobby.get_auto_select_roles()
        self.main_autolobby_autoselectroles_firstpreference_combobox.setCurrentIndex(config_auto_select_roles_positions[0].get_index())
        self.main_autolobby_autoselectroles_secondpreference_combobox.setCurrentIndex(config_auto_select_roles_positions[1].get_index())
        self.last_first_preference = config_auto_select_roles_positions[0]
        self.last_second_preference = config_auto_select_roles_positions[1]

        self.main_autoqueue_auto_start_queue_checkbox.setChecked(config_auto_queue.is_auto_start_queue_enabled())
        self.main_autoqueue_auto_accept_match_checkbox.setChecked(config_auto_queue.is_auto_accept_match_enabled())

    def propagate_updated_config(self) -> None:
        """
        Called when the user changes the configuration in the main window.
        Propagates the updated configuration to other parts of the application.
        """
        self.main_autochampionselect_profile_widget.load_config()
        self.lcuWorker.load_config()

    @pyqtSlot()
    def on_main_autochampionselect_profile_widget_config_updated(self) -> None:
        """
        Called by the auto champion select profile widget when the user changes its configuration.
        """
        self.load_config()
        self.lcuWorker.load_config()

    @pyqtSlot(bool)
    def on_main_mainfeatures_autolobby_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto lobby" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY).set_enabled(checked)
        self.propagate_updated_config()

    @pyqtSlot(bool)
    def on_main_mainfeatures_autoqueue_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto queue" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        self.config.get_feature_configuration(MainFeatures.AUTO_QUEUE).set_enabled(checked)
        self.propagate_updated_config()

    @pyqtSlot(bool)
    def on_main_mainfeatures_autochampionselect_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto champion select" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        self.config.get_feature_configuration(MainFeatures.AUTO_CHAMPION_SELECT).set_enabled(checked)
        self.propagate_updated_config()

    @pyqtSlot(bool)
    def on_main_autolobby_autoselectqueue_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto select queue" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        selected_queue_id = self.main_autolobby_autoselectqueue_combobox.currentData()
        if selected_queue_id is None:
            selected_queue_id = 0
        self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY).set_auto_select_queue(selected_queue_id, checked)
        self.propagate_updated_config()

    @pyqtSlot(str)
    def on_lcu_worker_update_status(self, status: str) -> None:
        """
        Called by the LCU worker thread to update the status text in the UI.
        :param status: The new status string to display in the main window.
        """
        self.main_status_label.setText(status)

    @pyqtSlot(list)
    def on_lcuWorker_updateQueues(self, queue_list: list[Queue]) -> None:
        """
        Called by the LCU worker thread when updated queues are retried.
        This function updates the UI with the queues' information.
        :param queue_list: list of queues.
        """
        # pylint: disable=invalid-name
        self.main_autolobby_autoselectqueue_combobox.clear()
        queue_list: list[Queue] = sorted(queue_list, key=lambda elem: elem.name())

        set_to_index = 0
        config_auto_select_queue_id = self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY).get_auto_select_queue_id()

        for index, queue in enumerate(queue_list):
            self.main_autolobby_autoselectqueue_combobox.addItem(queue.name(), queue.id())
            if queue.id() == config_auto_select_queue_id:
                set_to_index = index

        self.main_autolobby_autoselectqueue_combobox.setCurrentIndex(set_to_index)

    @pyqtSlot(int)
    def on_main_autolobby_autoselectqueue_combobox_currentIndexChanged(self, index: int) -> None:
        """
        Called when the currently selected item in the "Auto select queue" combobox changes.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        if index >= 0:
            (self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY)
             .set_auto_select_queue(self.main_autolobby_autoselectqueue_combobox.itemData(index),
                                    self.main_autolobby_autoselectqueue_checkbox.isChecked()))
            self.propagate_updated_config()

    @pyqtSlot(bool)
    def on_main_autolobby_autoselectroles_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto select roles" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY).set_auto_select_roles_enabled(checked)
        self.propagate_updated_config()

    @pyqtSlot(int)
    def on_main_autolobby_autoselectroles_firstpreference_combobox_currentIndexChanged(self, index: int) -> None:
        """
        Called when the currently selected item in the "Auto select roles - first preference" combobox changes.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        if self.last_first_preference is None:
            return
        second_preference_index = self.main_autolobby_autoselectroles_secondpreference_combobox.currentIndex()
        first_preference = Position.from_index(index)
        if second_preference_index == index:
            self.main_autolobby_autoselectroles_secondpreference_combobox.setCurrentIndex(
                self.last_first_preference.get_index())
        else:
            second_preference = Position.from_index(second_preference_index)
            (self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY)
             .set_auto_select_roles_preferences(first_preference, second_preference))
            self.propagate_updated_config()
        self.last_first_preference = first_preference

    @pyqtSlot(int)
    def on_main_autolobby_autoselectroles_secondpreference_combobox_currentIndexChanged(self, index: int) -> None:
        """
        Called when the currently selected item in the "Auto select roles - second preference" combobox changes.
        :param index: index of the selected item in the combobox.
        """
        # pylint: disable=invalid-name
        if self.last_second_preference is None:
            return
        first_preference_index = self.main_autolobby_autoselectroles_firstpreference_combobox.currentIndex()
        second_preference = Position.from_index(index)
        if first_preference_index == index:
            self.main_autolobby_autoselectroles_firstpreference_combobox.setCurrentIndex(
                self.last_second_preference.get_index())
        else:
            first_preference = Position.from_index(first_preference_index)
            (self.config.get_feature_configuration(MainFeatures.AUTO_LOBBY)
             .set_auto_select_roles_preferences(first_preference, second_preference))
            self.propagate_updated_config()
        self.last_second_preference = second_preference

    @pyqtSlot(bool)
    def on_main_autoqueue_auto_start_queue_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto start queue" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        self.config.get_feature_configuration(MainFeatures.AUTO_QUEUE).set_auto_start_queue_enabled(checked)
        self.propagate_updated_config()

    @pyqtSlot(bool)
    def on_main_autoqueue_auto_accept_match_checkbox_clicked(self, checked: bool) -> None:
        """
        Called when the "Auto accept match" checkbox is clicked.
        :param checked: true if the checkbox is checked, false if the checkbox is unchecked.
        """
        self.config.get_feature_configuration(MainFeatures.AUTO_QUEUE).set_auto_accept_match_enabled(checked)
        self.propagate_updated_config()
