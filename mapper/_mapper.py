import json
import os
import sys
import pkg_resources

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from PyQt5.QtGui import QFontMetrics, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRectF, QEvent, QTimer
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QMainWindow, QApplication, QStatusBar, QGraphicsView, \
    QGraphicsScene, QGraphicsProxyWidget, QScrollArea, QComboBox, QPushButton, QSizePolicy, QMessageBox, QStyle

import langtexts
import utils
from listener import JoystickListener
from joystickmapper._angles import angles
from joystickmapper._layouts import homeButton, layouts
from joystickmapper._modes import Mode
from scrolllabel import ScrollLabel


class JoystickMapper(QMainWindow):

    _buttonValueSig = pyqtSignal(pygame.event.Event)
    _joysticksConnectedSig = pyqtSignal(dict)
    _toggleInspectModeSig = pyqtSignal(bool)

    def __init__(self, pad_layout, joystick_id=None, angle=0, headless_mode=False, windowed=False, output_file=None,
                 mapper_closed_sig=None):
        super().__init__(None)

        self.setWindowTitle("Simple Joystick Mapper")
        self.setWindowIcon(QIcon(os.path.join(utils.resource_path("resources/joystick.ico"))))

        self.inspectMode = pad_layout == Mode.INSPECT
        self.mapperClosedSig = mapper_closed_sig

        self.layouts = layouts
        if os.path.exists("custom_layouts.json"):
            try:
                with open("custom_layouts.json", "r", encoding="utf8") as f:
                    custom_layouts = json.loads(f.read())
                layouts.update(custom_layouts)
            except:
                print(langtexts.getErrorText("layout_mismatch"))

        if pad_layout in layouts.keys():
            self.selectedPadLayout = pad_layout
            self.padLayout = self.layouts[self.selectedPadLayout]
        else:
            if not self.inspectMode:
                raise langtexts.getErrorText("layout")
            self.selectedPadLayout = Mode.FULL
            self.padLayout = self.layouts[self.selectedPadLayout]
        # address a given joystick (by instance number) or leave it empty so the script will point to the first pressed
        self.joystick_id = str(joystick_id) if joystick_id is not None else joystick_id
        if angle in angles:
            self.angle = angle
            self.rotateWidget = self.angle != 0
        else:
            raise langtexts.getErrorText("angle")
        self.headlessMode = headless_mode
        self.windowed = windowed
        if self.headlessMode:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        if windowed and (self.headlessMode or self.rotateWidget):
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.outputFile = output_file

        self.setupUI()
        self.setupUIInspect()
        self.setupDialogs()

        self.addedEvents = {}
        self.padValues = {}
        self.joysticksInfo = {}

        self.configEnded = False
        self.forceCloseRequested = False
        self.changeJoystickRequested = None
        self.changeLayoutRequested = None

        if self.inspectMode:
            if os.path.exists("joystickmapper_inspect.txt"):
                os.remove("joystickmapper_inspect.txt")

        self._buttonValueSig.connect(self.getButtonValue)
        self._joysticksConnectedSig.connect(self.getJoysticks)

        self.listener_thread = QThread()
        self.listener_obj = JoystickListener(self, self._joysticksConnectedSig, self._buttonValueSig,
                                             self._toggleInspectModeSig, self.inspectMode)
        self.listener_obj.moveToThread(self.listener_thread)
        self.listener_thread.setTerminationEnabled(True)
        self.listener_thread.started.connect(self.listener_obj.run)
        self.listener_thread.finished.connect(self.listener_obj.stop)
        self.listener_thread.start()

    def show(self, force_full=False):
        if force_full or ((self.headlessMode or self.rotateWidget) and not self.windowed):
            super().showFullScreen()
        else:
            super().show()
            if self.inspectMode:
                w, h = 860, 860
                if self.rotateWidget:
                    h, w = w, h
                    if self.windowed:
                        self.graphicsview.setGeometry(0, 0, w, h)
                        self.proxy.setGeometry(QRectF(0, 0, w, h))
                self.setGeometry(self.x(), self.y(), w, h)
            else:
                titleBarHeight = 0 if self.headlessMode else QApplication.style().pixelMetric(QStyle.PM_TitleBarHeight)
                x, y = self.x(), titleBarHeight
                w, h = 860, self.screen().availableSize().height() - titleBarHeight
                if self.rotateWidget:
                    h, w = w, h
                    self.graphicsview.setGeometry(0, 0, w, h)
                    self.proxy.setGeometry(QRectF(0, 0, h, w))
                if self.windowed:
                    x = (self.screen().availableSize().width() - w) // 2
                    y = (self.screen().availableSize().height() + titleBarHeight - h) // 2
                self.setGeometry(x, y, w, h)

    def setupUI(self):

        self.setMinimumWidth(860)

        self.header_style = open(utils.resource_path("qss/header.qss", module="joystickmapper"), "r").read()
        self.main_style = open(utils.resource_path("qss/main.qss", module="joystickmapper"), "r").read()
        self.selected_style_tag = "selected"
        self.idle_style_tag = "idle"

        self.mainWidget = QWidget()
        self.mainLayout = QGridLayout()
        if self.rotateWidget:
            self.mainLayout.setContentsMargins(5, 0, 5, 0)
        else:
            self.mainLayout.setContentsMargins(0, 5, 0, 5)

        if self.rotateWidget:
            self.widget2 = QWidget()
            self.myLayout2 = QGridLayout()
            self.myLayout2.setContentsMargins(0, 0, 0, 0)
            self.myLayout2.setSpacing(0)
            self.myLayout2.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

            self.graphicsview = QGraphicsView(self)
            self.graphicsview.setInteractive(True)
            self.graphicsview.installEventFilter(self)
            self.graphicsview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.graphicsview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scene = QGraphicsScene(self.graphicsview)
            self.graphicsview.setScene(self.scene)

            self.proxy = QGraphicsProxyWidget()
            self.proxy.setWidget(self.widget2)
            self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())
            self.scene.addItem(self.proxy)
            if not self.windowed:
                h, w = self.screen().size().width(), self.screen().size().height()
                self.graphicsview.setGeometry(0, 0, w, h)
                self.proxy.setGeometry(QRectF(0, 0, w, h))
            self.myLayout2.addWidget(self.graphicsview)

        self.buttonsFont = self.font()
        self.buttonsFont.setFamily("MS Shell Dlg 2")
        self.buttonsFont.setPointSize(self.buttonsFont.pointSize() + 4)
        self.buttonsFontHeight = QFontMetrics(self.buttonsFont).height()

        rowIndex = 0

        if not self.headlessMode:
            self.headerWidget = QWidget()
            self.headerWidget.setStyleSheet(self.header_style)
            font = self.headerWidget.font()
            font.setPointSize(font.pointSize() + 1)
            font.setFamily("MS Shell Dlg 2")
            self.headerWidget.setFont(font)
            self.headerLayout = QGridLayout()
            self.headerLayout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.headerWidget.setLayout(self.headerLayout)

            joyName_lbl = QLabel(langtexts.getHeaderText("joy"))
            joyName_lbl.setFont(font)
            self.headerLayout.addWidget(joyName_lbl, 0, 0)
            self.joyNameCombo = QComboBox()
            self.joyNameCombo.setFont(font)
            self.joyNameCombo.setMinimumWidth(300)
            self.joyNameCombo.setMaximumWidth(500)
            self.joyNameCombo.setMinimumHeight(30)
            self.joyNameCombo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.joyNameCombo.currentIndexChanged.connect(self.onChangeJoystick)
            self.headerLayout.addWidget(self.joyNameCombo, 0, 1, Qt.AlignmentFlag.AlignVCenter)
            QTimer.singleShot(5000, self.checkJoysticks)

            layout_lbl = QLabel(langtexts.getHeaderText("lay"))
            layout_lbl.setFont(font)
            self.headerLayout.addWidget(layout_lbl, 0, 2)
            self.layoutCombo = QComboBox()
            self.layoutCombo.setFont(font)
            self.layoutCombo.setMaximumWidth(200)
            self.layoutCombo.setMinimumHeight(30)
            self.layoutCombo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.layoutCombo.addItems(list(self.layouts.keys()))
            self.layoutCombo.setCurrentText(self.selectedPadLayout)
            self.layoutCombo.currentIndexChanged.connect(self.onChangeLayout)
            self.headerLayout.addWidget(self.layoutCombo, 0, 3, Qt.AlignmentFlag.AlignVCenter)

            self.toggleInspect = QPushButton()
            self.toggleInspect.setMinimumWidth(120)
            self.toggleInspect.setMinimumHeight(30)
            self.toggleInspect.setFont(font)
            self.toggleInspect.setText(langtexts.getHeaderText("norm") if self.inspectMode else langtexts.getHeaderText("deb"))
            self.toggleInspect.clicked.connect(self.toggleInspectMode)
            self.headerLayout.addWidget(self.toggleInspect, 0, 4)

            dummylabel = QLabel()
            self.headerLayout.addWidget(dummylabel, 0, 5)

            self.saveConfig_btn = QPushButton()
            self.saveConfig_btn.setMinimumWidth(120)
            self.saveConfig_btn.setMinimumHeight(30)
            self.saveConfig_btn.setFont(font)
            self.saveConfig_btn.setText(langtexts.getHeaderText("save"))
            self.saveConfig_btn.clicked.connect(self.onSaveConfig)
            self.headerLayout.addWidget(self.saveConfig_btn, 0, 6)

            self.headerLayout.setColumnStretch(0, 0)
            self.headerLayout.setColumnStretch(1, 0)
            self.headerLayout.setColumnStretch(2, 0)
            self.headerLayout.setColumnStretch(3, 0)
            self.headerLayout.setColumnStretch(4, 0)
            self.headerLayout.setColumnStretch(5, 1)
            self.headerLayout.setColumnStretch(6, 0)

            self.mainLayout.addWidget(self.headerWidget)
            rowIndex += 1

        self.joystick_widget = QWidget(self.widget2 if self.rotateWidget else self)
        self.joystick_widget.setStyleSheet(self.header_style)
        self.joystick_widget.setContentsMargins(5, 5, 5, 5)
        joystick_layout = QGridLayout()
        self.joystick_widget.setLayout(joystick_layout)
        self.idLabel = QLabel(self.widget2 if self.rotateWidget else self)
        self.idLabel.setStyleSheet(self.header_style)
        self.idLabel.setFont(self.buttonsFont)
        joystick_layout.addWidget(self.idLabel, 0, 0)
        self.nameLabel = QLabel(self.widget2 if self.rotateWidget else self)
        self.nameLabel.setStyleSheet(self.header_style)
        self.nameLabel.setFont(self.buttonsFont)
        joystick_layout.addWidget(self.nameLabel, 0, 1)
        joystick_layout.setColumnStretch(0, 0)
        joystick_layout.setColumnStretch(1, 1)
        if not self.inspectMode and self.headlessMode:
            self.mainLayout.addWidget(self.joystick_widget, rowIndex, 0, 1, 2)
            rowIndex += 1
        else:
            self.joystick_widget.hide()

        self.notAssignedText = langtexts.getButtonValueText("no")
        self.alreadyAssignedText = langtexts.getButtonValueText("rep")
        self.omittedText = langtexts.getButtonValueText("omi")

        self.setupLayoutGrid()

        self.scroll = QScrollArea(self.widget2 if self.rotateWidget else self)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content_widget)
        if self.inspectMode:
            self.scroll.hide()
        else:
            self.mainLayout.addWidget(self.scroll, rowIndex, 0, 1, 2)
            rowIndex += 1

        self.statusBar = QStatusBar()
        self.defaultText = langtexts.getStatusText("default")
        self.homeText = langtexts.getStatusText("home")
        self.repeatedText = langtexts.getStatusText("repeated")
        self.statusLabel = QLabel(self.defaultText)
        self.statusBar.addWidget(self.statusLabel)
        if not self.inspectMode:
            self.mainLayout.addWidget(self.statusBar, rowIndex, 0, 1, 2)

        self.checkNextButton(self.currentIndex, -1)
        self.scroll.verticalScrollBar().setValue(0)

        if self.rotateWidget:
            self.widget2.setLayout(self.mainLayout)
            self.mainWidget.setLayout(self.myLayout2)
            self.proxy.setRotation(self.angle)
        else:
            self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def setupLayoutGrid(self):

        self.currentIndex = 0
        self.currentButton = self.padLayout[0]

        self.button_widget_margin = 15
        self.content_widget = QWidget(self.widget2 if self.rotateWidget else self)
        self.content_widget.setStyleSheet(self.main_style)
        self.content_layout = QGridLayout()
        self.content_widget.setLayout(self.content_layout)

        for i, button in enumerate(self.layouts[Mode.FULL]):
            if i < len(self.padLayout):
                button = self.padLayout[i]
            if i == 0:
                objectName = self.selected_style_tag
            else:
                objectName = self.idle_style_tag
            button_widget = QWidget(self.widget2 if self.rotateWidget else self)
            button_widget.setObjectName(objectName)
            button_widget.setStyleSheet(self.main_style)
            button_widget.setContentsMargins(5, self.button_widget_margin, 5, self.button_widget_margin)
            button_layout = QGridLayout()
            button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            button_widget.setLayout(button_layout)
            button_label = QLabel(button, self.widget2 if self.rotateWidget else self)
            button_label.setObjectName(objectName)
            button_label.setFont(self.buttonsFont)
            button_layout.addWidget(button_label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            button_value = QLabel(self.notAssignedText, self.widget2 if self.rotateWidget else self)
            button_value.setObjectName(objectName)
            button_value.setFont(self.buttonsFont)
            button_layout.addWidget(button_value, 0, 1, 1, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            button_layout.setColumnStretch(0, 1)
            button_layout.setColumnStretch(1, 0)
            self.content_layout.addWidget(button_widget, i, 0, 1, 2)
            if i >= len(self.padLayout):
                button_widget.hide()

    def setupUIInspect(self):

        self.inspectWidget = ScrollLabel()
        self.inspectWidget.setStyleSheet(open(utils.resource_path("qss/inspect.qss", module="joystickmapper"), "r").read())

        if self.inspectMode:
            self.mainLayout.addWidget(self.inspectWidget, 0 if self.headlessMode else 1, 0, 1, 4)
        else:
            self.inspectWidget.hide()

    def setupDialogs(self):

        self.controllersChangedDialog = QMessageBox(self)
        self.controllersChangedDialog.setText(langtexts.getDialogsText("changed"))
        accept = self.controllersChangedDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

        self.controllersChangedHeadlessDialog = QMessageBox(self)
        self.controllersChangedHeadlessDialog.setText(langtexts.getDialogsText("changed_headless"))
        accept = self.controllersChangedHeadlessDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.controllersChangedHeadlessDialog.removeButton(accept)

        self.noControllersDialog = QMessageBox(self)
        self.noControllersDialog.setText(langtexts.getDialogsText("no"))
        accept = self.noControllersDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

        self.noControllersHeadlessDialog = QMessageBox(self)
        self.noControllersHeadlessDialog.setText(langtexts.getDialogsText("no_headless"))
        accept = self.noControllersHeadlessDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.noControllersHeadlessDialog.removeButton(accept)

        self.controllersDisconnectedDialog = QMessageBox(self)
        self.controllersDisconnectedDialog.setText(langtexts.getDialogsText("disconnected"))
        accept = self.controllersDisconnectedDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

        self.controllersDisconnectedHeadlessDialog = QMessageBox(self)
        self.controllersDisconnectedHeadlessDialog.setText(langtexts.getDialogsText("disconnected_headless"))
        accept = self.controllersDisconnectedHeadlessDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.controllersDisconnectedHeadlessDialog.removeButton(accept)

        self.controllerConfiguredHeadlessDialog = QMessageBox(self)
        self.controllerConfiguredHeadlessDialog.setText(langtexts.getDialogsText("success_headless"))
        accept = self.controllerConfiguredHeadlessDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.controllerConfiguredHeadlessDialog.removeButton(accept)

        self.cancelDialog = QMessageBox(self)
        self.cancelDialog.setText(langtexts.getDialogsText("cancel"))
        reject = self.cancelDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.RejectRole)
        accept = self.cancelDialog.addButton(langtexts.getButtonsText("quit"), QMessageBox.ButtonRole.AcceptRole)
        accept.clicked.connect(self.forceClose)

        self.changeDialog = QMessageBox(self)
        self.changeDialog.setText(langtexts.getDialogsText("change"))
        reject = self.changeDialog.addButton(langtexts.getButtonsText("cancel"), QMessageBox.ButtonRole.RejectRole)
        accept = self.changeDialog.addButton(langtexts.getButtonsText("change"), QMessageBox.ButtonRole.AcceptRole)
        accept.clicked.connect(self.changeSelected)

        self.saveDialog = QMessageBox(self)
        self.saveDialog.setText(langtexts.getDialogsText("save"))
        reject = self.saveDialog.addButton(langtexts.getButtonsText("cancel"), QMessageBox.ButtonRole.RejectRole)
        accept = self.saveDialog.addButton(langtexts.getButtonsText("save"), QMessageBox.ButtonRole.AcceptRole)
        accept.clicked.connect(lambda checked: self.saveConfig(True))

        self.savedDialog = QMessageBox(self)
        self.savedDialog.setText(langtexts.getDialogsText("saved"))
        accept = self.savedDialog.addButton(langtexts.getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

    def changeSelected(self):
        if self.changeJoystickRequested:
            self.changeJoystick(self.changeJoystickRequested)
            self.changeJoystickRequested = False

        elif self.changeLayoutRequested:
            self.changeLayout(self.changeLayoutRequested)
            self.changeLayoutRequested = False

    def onChangeJoystick(self, index):
        if self.joyNameCombo.count() > 0:
            self.changeJoystickRequested = index
            if self.joystick_id is not None and self.joystick_id in self.padValues.keys() and self.padValues[self.joystick_id]["layout"]:
                self.changeDialog.exec()
            else:
                self.changeJoystick(index)

    def changeJoystick(self, index):
        if self.joyNameCombo.count() > 0:
            joystick_id = self.joyNameCombo.itemText(index).split(":")[0]
            if joystick_id != self.joystick_id:
                if self.joystick_id in self.padValues.keys():
                    self.padValues[self.joystick_id]["layout"] = {}
                if self.joystick_id in self.addedEvents.keys():
                    self.addedEvents[self.joystick_id] = {}
                self.joystick_id = joystick_id
                self.changeLayout(self.layoutCombo.currentIndex(), force=True)

    def checkJoysticks(self):
        if not self.joysticksInfo:
            if self.headlessMode:
                QTimer.singleShot(3000, lambda: self.forceClose(dialog_to_close=self.noControllersHeadlessDialog))
                self.noControllersHeadlessDialog.exec()
            else:
                self.noControllersDialog.exec()

    def onChangeLayout(self, index):
        self.changeLayoutRequested = True
        if self.joystick_id is not None and self.joystick_id in self.padValues.keys() and self.padValues[self.joystick_id]["layout"]:
            self.changeDialog.exec()
        else:
            self.changeLayout(index)

    def changeLayout(self, index, force=False):
        pad_layout_name = ""
        if not self.headlessMode:
            if self.changeLayoutRequested:
                self.changeLayoutRequested = False
                pad_layout_name = self.layoutCombo.itemText(index)

        if force or self.selectedPadLayout != pad_layout_name:
            if pad_layout_name:
                self.selectedPadLayout = pad_layout_name
            self.padLayout = self.layouts[self.selectedPadLayout]
            for i, button in enumerate(self.layouts[Mode.FULL]):
                button_widget = self.content_layout.itemAt(i).widget()
                if i < len(self.padLayout):
                    objectName = self.selected_style_tag if i == 0 else self.idle_style_tag
                    button = self.padLayout[i]
                    button_widget.setStyleSheet(self.main_style)
                    button_widget.setObjectName(objectName)
                    button_label = button_widget.layout().itemAt(0).widget()
                    button_label.setText(button)
                    button_label.setObjectName(objectName)
                    button_value = button_widget.layout().itemAt(1).widget()
                    button_value.setText(self.notAssignedText)
                    button_value.setObjectName(objectName)
                    button_widget.show()
                else:
                    button_widget.hide()
            self.currentIndex = 0
            self.currentButton = self.padLayout[0]
            if self.joystick_id in self.padValues.keys():
                self.padValues[self.joystick_id]["layout"] = {}
            if self.joystick_id in self.addedEvents.keys():
                self.addedEvents[self.joystick_id] = {}

    def toggleInspectMode(self, checked=False):

        self.inspectMode = not self.inspectMode

        if self.inspectMode:
            if self.headlessMode:
                self.joystick_widget.hide()
            else:
                self.joyNameCombo.setDisabled(True)
                self.layoutCombo.setDisabled(True)
                self.saveConfig_btn.setDisabled(True)
            if not self.inspectWidget.text():
                if os.path.exists("joystickmapper_inspect.txt"):
                    os.remove("joystickmapper_inspect.txt")
                self.getJoysticks(self.joysticksInfo)
            oldWidget = self.scroll
            newWidget = self.inspectWidget

        else:
            if self.headlessMode:
                self.joystick_widget.show()
            else:
                self.joyNameCombo.setDisabled(False)
                self.layoutCombo.setDisabled(False)
                self.saveConfig_btn.setDisabled(False)
            oldWidget = self.inspectWidget
            newWidget = self.scroll

        if not self.headlessMode:
            self.toggleInspect.setText(langtexts.getHeaderText("norm") if self.inspectMode else langtexts.getHeaderText("deb"))

        oldWidget.hide()
        self.mainLayout.replaceWidget(oldWidget, newWidget)
        newWidget.show()
        self._toggleInspectModeSig.emit(self.inspectMode)

    def onSaveConfig(self):
        self.saveDialog.exec()

    def saveConfig(self, force=False):

        if force or (self.headlessMode and not self.inspectMode):

            if not self.outputFile:
                joyName = self.joysticksInfo[self.joystick_id]["name"]
                padLayout = "FULL" if self.selectedPadLayout == "Completo" else self.selectedPadLayout.upper()
                fileBaseName = utils.get_valid_filename(padLayout + "_" + joyName)
                fileName = f"{fileBaseName[0:64]}.json"
                i = 0
                while os.path.exists(fileName):
                    i += 1
                    fileName = f"{fileBaseName}_{i}.json"
            else:
                fileName = self.outputFile
            output = {
                "joysticks_info": self.joysticksInfo,
                "joystick_configured": self.joystick_id,
                self.joystick_id: self.padValues[self.joystick_id]["layout"]
            }
            with open(fileName, "w", encoding="utf8") as f:
                json.dump(output, f, ensure_ascii=False, sort_keys=False, indent=4)

            if not self.headlessMode:
                self.savedDialog.exec()

    @pyqtSlot(dict)
    def getJoysticks(self, joysticksInfo):

        if not self.headlessMode and not self.inspectMode:
            self.joyNameCombo.clear()

        if not joysticksInfo:
            self.joysticksInfo = joysticksInfo
            if self.headlessMode:
                QTimer.singleShot(3000, self.forceClose)
                self.controllersDisconnectedHeadlessDialog.exec()
            else:
                if self.joysticksInfo:
                    self.controllersDisconnectedDialog.exec()
                else:
                    self.noControllersDialog.exec()
            return
        else:
            if self.headlessMode:
                if (self.joystick_id is not None and self.joystick_id not in joysticksInfo.keys() or
                        (self.joystick_id in self.joysticksInfo.keys() and self.joystick_id in joysticksInfo.keys() and
                         self.joysticksInfo[self.joystick_id]["name"] != joysticksInfo[self.joystick_id]["name"])):
                    QTimer.singleShot(3000, lambda: self.forceClose(
                        dialog_to_close=self.controllersDisconnectedHeadlessDialog))
                    self.controllersDisconnectedHeadlessDialog.exec()
            else:
                if self.joystick_id is not None and self.joysticksInfo != joysticksInfo:
                    self.controllersChangedDialog.exec()
            self.joysticksInfo = joysticksInfo

        if self.inspectMode and not self.inspectWidget.text():
            msg1, msg2 = langtexts.getJoysticksMessages()
            self.drawButtonValue(msg1)
            for joystick in self.joysticksInfo.keys():
                self.drawButtonValue(msg2 % (self.joysticksInfo[joystick]["name"],
                                             joystick,
                                             self.joysticksInfo[joystick]["guid"],
                                             self.joysticksInfo[joystick]["id"]))

        else:
            if not self.headlessMode:
                joysticks = list(joysticksInfo.keys())
                comboItems = [f"{str(joystick)}: {joysticksInfo[joystick]["name"]}" for joystick in joysticks]
                self.joyNameCombo.addItems(comboItems)
                self.joyNameCombo.setCurrentIndex(0)
                self.joystick_id = joysticks[0]
                self.changeLayout(self.layoutCombo.currentIndex(), force=True)

            else:
                joysticks = [self.joystick_id] if self.joystick_id is not None else []
                self.changeLayout(0, force=True)

            for joystick in joysticks:
                joystickInfo = joysticksInfo[joystick]
                self.padValues[joystick] = {
                    "name": joystickInfo["name"],
                    "guid": joystickInfo["guid"],
                    "id": joystickInfo["id"],
                    "layout": {}
                }
                self.addedEvents[joystick] = {}

                if self.headlessMode and self.joystick_id is not None and joystick == self.joystick_id:
                    self.idLabel.setText(joystick + ":")
                    self.nameLabel.setText(joystickInfo["name"])

    @pyqtSlot(pygame.event.Event)
    def getButtonValue(self, event):

        if self.inspectMode:
            self.drawButtonValue(event)

        else:
            self.configButtonValue(event)

    def drawButtonValue(self, event):
        self.inspectWidget.appendText(str(event))
        with open("joystickmapper_inspect.txt", "a", encoding="utf8") as f:
            f.write(str(event) + "\n")

    def configButtonValue(self, event):

        goToNext = False

        if event.type == -1:
            valueDesc = self.omittedText
            if self.currentButton in self.padValues[self.joystick_id]["layout"].keys():
                del self.padValues[self.joystick_id]["layout"][self.currentButton]
            addedEventsKeys = list(self.addedEvents[self.joystick_id].keys())
            if ((self.currentButton != homeButton and self.currentButton in addedEventsKeys) or
                    (self.currentButton == homeButton and addedEventsKeys.count(self.currentButton) > 1)):
                del self.addedEvents[self.joystick_id][self.currentButton]
            goToNext = True

        else:

            if self.joystick_id is None:
                self.joystick_id = str(event.instance_id)
                # this is better done in async mode, whenever there is a change, invoking self.getJoysticks()
                # self.joysticksInfo = self.listener_obj.getJoysticksInfo()
                self.getJoysticks(self.joysticksInfo)

            valueDesc = ""

            joystick_id = str(event.instance_id)
            if self.joystick_id == joystick_id:

                currentButton = self.currentButton
                if "(" in currentButton:
                    currentButton = currentButton.split("(", 1)[0].strip()

                if event.type == pygame.JOYBUTTONUP:
                    self.padValues[joystick_id]["layout"][currentButton] = {
                        "type": event.type,
                        "description": "BUTTON",
                        "value": event.button
                    }
                    valueDesc = str(event.button)

                elif event.type == pygame.JOYHATMOTION:
                    self.padValues[joystick_id]["layout"][currentButton] = {
                        "type": event.type,
                        "description": "D-PAD",
                        "hat": event.hat,
                        "value": event.value
                    }
                    valueDesc = f"HAT {str(event.value[0])}, {str(event.value[1])}"

                elif event.type == pygame.JOYAXISMOTION:
                    self.padValues[joystick_id]["layout"][currentButton] = {
                        "type": event.type,
                        "description": "ANALOG JOYSTICK / TRIGGER",
                        "axe": event.axis,
                        "value": event.value
                    }
                    valueDesc = f"AXIS {str(event.axis)}, {str(int(event.value))}"

                currText = self.content_layout.itemAt(self.currentIndex).widget().layout().itemAt(1).widget().text()
                eventAdded = event in self.addedEvents[self.joystick_id].values()
                if not eventAdded or currText == valueDesc:
                    goToNext = True
                    if not eventAdded:
                        self.addedEvents[self.joystick_id][self.currentButton] = event

                else:
                    self.content_layout.itemAt(self.currentIndex).widget().layout().itemAt(1).widget().setText(self.alreadyAssignedText)
                    self.statusLabel.setText(self.repeatedText)

        if goToNext:
            prevIndex = self.currentIndex
            self.currentIndex += 1
            if self.currentIndex <= len(self.padLayout):
                if self.currentIndex == len(self.padLayout):
                    if self.headlessMode:
                        self.endConfig(prevIndex, valueDesc)
                    else:
                        self.currentIndex = prevIndex
                self.checkNextButton(self.currentIndex, prevIndex, valueDesc)

    def checkNextButton(self, index, prevIndex, valueDesc=""):
        if 0 <= prevIndex <= len(self.padLayout):
            prevWidget = self.content_layout.itemAt(prevIndex).widget()
            prevWidget.setObjectName(self.idle_style_tag)
            for i in range(prevWidget.layout().count()):
                w = prevWidget.layout().itemAt(i).widget()
                w.setObjectName(self.idle_style_tag)
            prevWidget.setStyleSheet(self.main_style)
            prevWidget.layout().itemAt(1).widget().setText(valueDesc)
        currWidget = self.content_layout.itemAt(index).widget()
        currWidget.setObjectName(self.selected_style_tag)
        for i in range(currWidget.layout().count()):
            w = currWidget.layout().itemAt(i).widget()
            w.setObjectName(self.selected_style_tag)
        currWidget.setStyleSheet(self.main_style)
        self.scroll.ensureWidgetVisible(currWidget)
        self.currentButton = self.padLayout[index]
        if self.currentButton == homeButton:
            self.statusLabel.setText(self.homeText)
        else:
            self.statusLabel.setText(self.defaultText)

    def eventFilter(self, source=None, event=None):
        # This is needed when widget is rotated (installed in graphicsview)
        if event is not None and event.type() == QEvent.Type.KeyRelease:
            self.keyReleaseEvent(event)
            return True
        return super().eventFilter(source, event)

    def keyReleaseEvent(self, a0):

        if a0.key() == Qt.Key.Key_Escape:
            if self.headlessMode:
                self.forceClose()
            else:
                self.close()

        elif a0.key() == Qt.Key.Key_F11:
            if not self.rotateWidget and not self.headlessMode:
                if self.isFullScreen():
                    self.showNormal()
                else:
                    self.show(force_full=True)

        if not self.inspectMode and 0 <= self.currentIndex <= len(self.padLayout):

            prevIndex = self.currentIndex
            prevText = self.content_layout.itemAt(self.currentIndex).widget().layout().itemAt(1).widget().text()

            if a0.key() == Qt.Key.Key_Up:
                if self.currentIndex > 0:
                    self.currentIndex -= 1

            elif a0.key() == Qt.Key.Key_Down:
                if self.currentIndex < len(self.padLayout) - 1:
                    self.currentIndex += 1

            elif a0.key() == Qt.Key.Key_Delete:
                w = self.content_layout.itemAt(prevIndex).widget()
                w.layout().itemAt(1).widget().setText(self.notAssignedText)

            if prevIndex != self.currentIndex:
                if prevText in (self.notAssignedText, self.alreadyAssignedText):
                    valueDesc = self.omittedText
                    if self.joystick_id is not None and self.joystick_id in self.addedEvents.keys() and self.currentButton in self.addedEvents[self.joystick_id].keys():
                        try:
                            del self.addedEvents[self.joystick_id][self.currentButton]
                        except:
                            pass
                else:
                    valueDesc = prevText
                if self.headlessMode and prevIndex == len(self.padLayout) - 1 and valueDesc == self.omittedText:
                    self.endConfig(prevIndex, valueDesc)
                else:
                    self.checkNextButton(self.currentIndex, prevIndex, valueDesc)

        if self.content_widget.isVisible():
            self.content_widget.setFocus(Qt.FocusReason.NoFocusReason)

    def endConfig(self, index, text):
        w = self.content_layout.itemAt(index).widget()
        w.layout().itemAt(1).widget().setText(text)
        # force updating label content (blocked by dialog otherwise)
        w.update()
        w.hide()
        w.show()
        self.configEnded = True
        QTimer.singleShot(3000, lambda: self.forceClose(dialog_to_close=self.controllerConfiguredHeadlessDialog))
        self.controllerConfiguredHeadlessDialog.exec()

    def forceClose(self, checked=False, dialog_to_close=None):
        self.forceCloseRequested = True
        if dialog_to_close is not None:
            dialog_to_close.accept()
        # using just self.close() it will not actually close!
        self.closeEvent()

    def closeEvent(self, a0=None):

        if self.forceCloseRequested or self.headlessMode:
            self.listener_thread.quit()
            self.saveConfig()
            if self.mapperClosedSig is not None:
                self.mapperClosedSig.emit(self.configEnded)
            sys.exit()

        else:
            a0.ignore()
            self.cancelDialog.exec()
