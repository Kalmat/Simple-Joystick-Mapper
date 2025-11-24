import copy
import json
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QRectF, QEvent, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QStyle, QFileDialog

from ._listener import JoystickListener
from ._ui import MainWindow_UI
from ._layouts import homeButton, layouts
from ._angles import angles
from ._modes import Mode
from ._langtexts import *
from ._utils import *


class JoystickMapper(QMainWindow):

    _buttonValueSig = pyqtSignal(pygame.event.Event)
    _joysticksConnectedSig = pyqtSignal(dict)
    _toggleInspectModeSig = pyqtSignal(bool)

    def __init__(self, pad_layout, joystick_id=None, angle=0, headless_mode=False, windowed=False, output_file=None,
                 standalone_mode=False, force_complete_layout=False, mapper_closed_sig=None):
        super().__init__(None)

        self.standalone = standalone_mode
        if self.standalone:
            self.setWindowTitle("Simple Joystick Mapper")
            self.setWindowIcon(QIcon(os.path.join(resource_path("resources/joystick.ico"))))

        self.inspectMode = pad_layout == Mode.INSPECT
        self.mapperClosedSig = mapper_closed_sig

        self.layouts = layouts
        if os.path.exists("custom_layouts.json"):
            try:
                with open("custom_layouts.json", "r", encoding="utf8") as f:
                    custom_layouts = json.loads(f.read())
                layouts.update(custom_layouts)
            except:
                print(getErrorText("layout_mismatch"))

        if pad_layout in layouts.keys():
            self.selectedPadLayout = pad_layout
            self.padLayout = self.layouts[self.selectedPadLayout]
        else:
            if not self.inspectMode:
                raise getErrorText("layout")
            self.selectedPadLayout = Mode.FULL
            self.padLayout = self.layouts[self.selectedPadLayout]
        # address a given joystick (by instance number) or leave it empty so the script will point to the first pressed
        self.joystick_id = str(joystick_id) if joystick_id is not None else joystick_id
        if angle in angles:
            self.angle = angle
            self.rotateWidget = self.angle != 0
        else:
            raise getErrorText("angle")
        self.headlessMode = headless_mode
        self.windowed = windowed
        if self.headlessMode:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        if windowed and (self.headlessMode or self.rotateWidget):
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.outputFile = output_file
        self.forceCompleteLayout = force_complete_layout

        # get connected joysticks
        QTimer.singleShot(5000, self.checkJoysticks)

        # setup UI and signals
        self.ui = MainWindow_UI(self, self.rotateWidget, self.angle, self.headlessMode, self.inspectMode,
                                self.windowed, self.padLayout, self.layouts[Mode.FULL])
        self.connectUISignals()

        # set first button and variables
        self.currentIndex = 0
        self.currentButton = self.padLayout[0]
        self.updateNextButton(self.currentIndex, -1)

        self.padValues = {}
        self.joysticksInfo = {}

        self.configEnded = False
        self.forceCloseRequested = False
        self.changeJoystickRequested = None
        self.changeLayoutRequested = None
        self.layoutLoaded = False

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

    def connectUISignals(self):

        if not self.headlessMode:
            # connect UI signals
            self.ui.joyNameCombo.currentIndexChanged.connect(self.onChangeJoystick)
            self.ui.layoutCombo.addItems(list(self.layouts.keys()))
            self.ui.layoutCombo.setCurrentText(self.selectedPadLayout)
            self.ui.layoutCombo.currentIndexChanged.connect(self.onChangeLayout)
            self.ui.toggleInspect.clicked.connect(self.toggleInspectMode)
            self.ui.saveConfig_btn.clicked.connect(self.onSaveConfig)
            self.ui.loadConfig_btn.clicked.connect(self.loadConfig)

        # connect dialogs buttons
        self.ui.cancelDialog_btn.clicked.connect(self.forceClose)
        self.ui.changeDialog_btn.clicked.connect(self.changeSelected)
        self.ui.saveDialog_btn.clicked.connect(lambda checked: self.saveConfig(True))

    def show(self, force_full=False):
        self.listener_thread.start()
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

    def changeSelected(self):
        if self.changeJoystickRequested is not None:
            self.changeJoystick(self.changeJoystickRequested)

        elif self.changeLayoutRequested is not None:
            self.changeLayout(self.changeLayoutRequested)

    def onChangeJoystick(self, index):
        if self.ui.joyNameCombo.count() > 0:
            self.changeJoystickRequested = index
            if self.joystick_id is not None and self.joystick_id in self.padValues.keys() and self.padValues[self.joystick_id]["layout"]:
                self.ui.changeDialog.exec()
            else:
                self.changeJoystick(index)

    def changeJoystick(self, index):
        if self.ui.joyNameCombo.count() > 0:
            joystick_id = self.ui.joyNameCombo.itemText(index).split(":")[0]
            if joystick_id != self.joystick_id:
                if self.joystick_id in self.padValues.keys():
                    if self.layoutLoaded:
                        self.padValues[self.joystick_id]["layout"] = copy.deepcopy(self.padValues[joystick_id]["layout"])
                        self.padValues[joystick_id]["layout"] = {}
                    else:
                        self.padValues[self.joystick_id]["layout"] = {}
                self.joystick_id = joystick_id
                if not self.layoutLoaded:
                    self.changeLayout(self.ui.layoutCombo.currentIndex(), force=True)
        self.changeJoystickRequested = None

    def checkJoysticks(self):
        if not self.joysticksInfo:
            if self.headlessMode:
                QTimer.singleShot(3000, lambda: self.forceClose(dialog_to_close=self.ui.noControllersHeadlessDialog))
                self.ui.noControllersHeadlessDialog.exec()
            else:
                self.ui.noControllersDialog.exec()

    def onChangeLayout(self, index):
        self.changeLayoutRequested = index
        if self.joystick_id is not None and self.joystick_id in self.padValues.keys() and self.padValues[self.joystick_id]["layout"]:
            self.ui.changeDialog.exec()
        else:
            self.changeLayout(index)

    def changeLayout(self, index, force=False):
        pad_layout_name = ""
        if not self.headlessMode:
            pad_layout_name = self.ui.layoutCombo.itemText(index)

        if force or self.selectedPadLayout != pad_layout_name:
            if pad_layout_name:
                self.selectedPadLayout = pad_layout_name
            self.padLayout = self.layouts[self.selectedPadLayout]
            self.ui.updateLayoutGrid(self.padLayout, self.layouts[Mode.FULL])
            self.currentIndex = 0
            self.currentButton = self.padLayout[0]
            if self.joystick_id in self.padValues.keys():
                self.padValues[self.joystick_id]["layout"] = {}

        self.changeLayoutRequested = None
        self.layoutLoaded = False

    def toggleInspectMode(self, checked=False):

        self.inspectMode = not self.inspectMode

        if self.inspectMode:
            if self.headlessMode:
                self.joystick_widget.hide()
            else:
                self.ui.joyNameCombo.setDisabled(True)
                self.ui.layoutCombo.setDisabled(True)
                self.ui.saveConfig_btn.setDisabled(True)
                self.ui.loadConfig_btn.setDisabled(True)
            if not self.ui.inspectWidget.text():
                if os.path.exists("joystickmapper_inspect.txt"):
                    os.remove("joystickmapper_inspect.txt")
                self.getJoysticks(self.joysticksInfo)
            oldWidget = self.ui.scroll
            newWidget = self.ui.inspectWidget

        else:
            if self.headlessMode:
                self.joystick_widget.show()
            else:
                self.ui.joyNameCombo.setDisabled(False)
                self.ui.layoutCombo.setDisabled(False)
                self.ui.saveConfig_btn.setDisabled(False)
                self.ui.loadConfig_btn.setDisabled(False)
            oldWidget = self.ui.inspectWidget
            newWidget = self.ui.scroll

        if not self.headlessMode:
            self.ui.toggleInspect.setText(getHeaderText("norm") if self.inspectMode else getHeaderText("deb"))

        oldWidget.hide()
        self.ui.mainLayout.replaceWidget(oldWidget, newWidget)
        newWidget.show()
        self._toggleInspectModeSig.emit(self.inspectMode)

    def loadConfig(self, checked=False):

        filename, _ = QFileDialog.getOpenFileName(self, "Select file to load", ".", "*.json")
        if filename:
            filename = os.path.normpath(filename)
            with open(filename, "r", encoding="utf8") as f:
                layout = json.loads(f.read())

            try:
                self.selectedPadLayout = layout["layout"]
                if self.selectedPadLayout not in list(self.layouts.keys()):
                    raise "Wrong layout"
                joystick_id = layout["joystick_configured"]
                self.padLayout = self.layouts[self.selectedPadLayout]
                if self.joystick_id is not None:
                    self.padValues[self.joystick_id]["layout"] = {}
                new_padLayout = {}
                for button in layout[joystick_id].keys():
                    value = layout[joystick_id][button]["value"]
                    if "hat" in layout[joystick_id][button].keys():
                        valueDesc = f"HAT {str(value[0])}, {str(value[1])}"
                    elif "axis" in layout[joystick_id][button].keys():
                        valueDesc = f"AXIS {str(layout[joystick_id][button]["axis"])}, {str(value)}"
                    else:
                        valueDesc = str(value)
                    if self.joystick_id is not None:
                        self.padValues[self.joystick_id]["layout"][button] = layout[joystick_id][button]
                    new_padLayout[button] = valueDesc
                self.ui.loadNewLayoutGrid(new_padLayout, self.padLayout)
                self.ui.layoutCombo.setCurrentText(self.selectedPadLayout)
                self.layoutLoaded = True

            except:
                self.ui.loadLayoutErrorDialog.exec()

    def onSaveConfig(self):
        self.ui.saveDialog.exec()

    def saveConfig(self, force=False):

        if self.forceCompleteLayout and self.joystick_id is not None and len(self.padLayout) != len(list(self.padValues[self.joystick_id]["layout"].keys())):
            # warn user in case configuration is not complete, but it should
            if self.headlessMode:
                # in headless mode, the tool will exit since there is no other way (user can repeat process)
                QTimer.singleShot(3000, lambda: self.forceClose(dialog_to_close=self.ui.completeLayoutHeadlessDialog))
                self.ui.completeLayoutHeadlessDialog.exec()
            else:
                # in non-headless mode, no configuration is saved. User can work it out within the tool.
                self.ui.completeLayoutDialog.exec()

        else:

            if force or (self.headlessMode and not self.inspectMode):
                # force means that user has pressed the 'Save' button. Headless mode needs to automatically save.

                # joystick_id should not be None, but just in case...
                saveConfig = self.joystick_id is not None

                if saveConfig:
                    if not self.outputFile:
                        joyName = self.joysticksInfo[self.joystick_id]["name"]
                        padLayout = "FULL" if self.selectedPadLayout == "Completo" else self.selectedPadLayout.upper()
                        fileBaseName = get_valid_filename(padLayout + "_" + joyName)
                        fileName = f"{fileBaseName[0:64]}.json"
                        i = 0
                        while os.path.exists(fileName):
                            i += 1
                            fileName = f"{fileBaseName}_{i}.json"
                    else:
                        fileName = self.outputFile

                    output = {
                        "joysticks_info": self.joysticksInfo,
                        "layout": self.selectedPadLayout,
                        "joystick_configured": self.joystick_id,
                        self.joystick_id: self.padValues[self.joystick_id]["layout"]
                    }
                    with open(fileName, "w", encoding="utf8") as f:
                        json.dump(output, f, ensure_ascii=False, sort_keys=False, indent=4)

                    if self.headlessMode:
                        # warn the user the configuration was successful and exit tool
                        QTimer.singleShot(3000, lambda: self.forceClose(dialog_to_close=self.ui.controllerConfiguredHeadlessDialog))
                        self.ui.controllerConfiguredHeadlessDialog.exec()
                    else:
                        # warn the user the configuration was saved
                        self.ui.savedDialog.exec()

    @pyqtSlot(dict)
    def getJoysticks(self, joysticksInfo):

        if not self.headlessMode and not self.inspectMode:
            self.ui.joyNameCombo.clear()

        self.joysticksInfo = self.checkJoysticksInfo(joysticksInfo)

        if self.joysticksInfo:

            if self.inspectMode and not self.ui.inspectWidget.text():
                msg1, msg2 = getJoysticksMessages()
                self.drawButtonValue(msg1)
                for joystick in self.joysticksInfo.keys():
                    self.drawButtonValue(msg2 % (self.joysticksInfo[joystick]["name"],
                                                 joystick,
                                                 self.joysticksInfo[joystick]["guid"],
                                                 self.joysticksInfo[joystick]["id"]))

            else:

                if self.headlessMode:
                    joysticks = [self.joystick_id] if self.joystick_id is not None else []
                    self.changeLayout(0, force=True)

                else:
                    joysticks = list(joysticksInfo.keys())
                    comboItems = [f"{str(joystick)}: {joysticksInfo[joystick]["name"]}" for joystick in joysticks]
                    self.ui.joyNameCombo.addItems(comboItems)
                    self.ui.joyNameCombo.setCurrentIndex(0)
                    self.joystick_id = joysticks[0]
                    self.changeLayout(self.ui.layoutCombo.currentIndex(), force=True)

                for joystick in joysticks:
                    joystickInfo = joysticksInfo[joystick]
                    self.padValues[joystick] = {
                        "name": joystickInfo["name"],
                        "guid": joystickInfo["guid"],
                        "id": joystickInfo["id"],
                        "layout": {}
                    }

                    if self.headlessMode and self.joystick_id is not None and joystick == self.joystick_id:
                        self.ui.idLabel.setText(joystick + ":")
                        self.ui.nameLabel.setText(joystickInfo["name"])

    def checkJoysticksInfo(self, joysticksInfo):

        if not joysticksInfo:
            if self.headlessMode:
                QTimer.singleShot(3000, self.forceClose)
                self.ui.controllersDisconnectedHeadlessDialog.exec()
            else:
                if self.joysticksInfo:
                    self.ui.controllersDisconnectedDialog.exec()
                else:
                    self.ui.noControllersDialog.exec()
        else:
            if self.headlessMode:
                if (self.joystick_id is not None and self.joystick_id not in joysticksInfo.keys() or
                        (self.joystick_id in self.joysticksInfo.keys() and self.joystick_id in joysticksInfo.keys() and
                         self.joysticksInfo[self.joystick_id]["name"] != joysticksInfo[self.joystick_id]["name"])):
                    QTimer.singleShot(3000, lambda: self.forceClose(dialog_to_close=self.ui.controllersDisconnectedHeadlessDialog))
                    self.ui.controllersDisconnectedHeadlessDialog.exec()
            else:
                if self.joystick_id is not None and self.joysticksInfo != joysticksInfo:
                    self.ui.controllersChangedDialog.exec()

        return joysticksInfo


    @pyqtSlot(pygame.event.Event)
    def getButtonValue(self, event):

        if self.inspectMode:
            self.drawButtonValue(event)

        else:
            self.configButtonValue(event)

    def drawButtonValue(self, event):
        self.ui.inspectWidget.appendText(str(event))
        with open("joystickmapper_inspect.txt", "a", encoding="utf8") as f:
            f.write(str(event) + "\n")

    def configButtonValue(self, event):

        goToNext = False

        if event.type == -1:
            valueDesc = self.omittedText
            if self.currentButton in self.padValues[self.joystick_id]["layout"].keys():
                del self.padValues[self.joystick_id]["layout"][self.currentButton]
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

                print(self.currentIndex, self.currentButton)

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
                        "value": [int(value) for value in event.value]
                    }
                    valueDesc = f"HAT {str(event.value[0])}, {str(event.value[1])}"

                elif event.type == pygame.JOYAXISMOTION:
                    self.padValues[joystick_id]["layout"][currentButton] = {
                        "type": event.type,
                        "description": "ANALOG JOYSTICK / TRIGGER",
                        "axis": event.axis,
                        "value": int(event.value)
                    }
                    valueDesc = f"AXIS {str(event.axis)}, {str(int(event.value))}"

                currText = self.ui.content_layout.itemAt(self.currentIndex).widget().layout().itemAt(1).widget().text()
                eventAdded = event in self.padValues[self.joystick_id]["layout"].values()
                if not eventAdded or currText == valueDesc:
                    goToNext = True

                else:
                    self.ui.content_layout.itemAt(self.currentIndex).widget().layout().itemAt(1).widget().setText(self.alreadyAssignedText)
                    self.ui.statusLabel.setText(self.repeatedText)

        if goToNext:
            self.checkNextButton(valueDesc)

    def checkNextButton(self, valueDesc):
        prevIndex = self.currentIndex
        self.currentIndex += 1
        if self.currentIndex <= len(self.padLayout):
            if self.currentIndex == len(self.padLayout):
                if self.headlessMode:
                    self.endHeadlessConfig(prevIndex, valueDesc)
                else:
                    self.currentIndex = prevIndex
            if not self.configEnded:
                self.updateNextButton(self.currentIndex, prevIndex, valueDesc)

    def updateNextButton(self, index, prevIndex, valueDesc=""):
        if 0 <= prevIndex <= len(self.padLayout):
            prevWidget = self.ui.content_layout.itemAt(prevIndex).widget()
            prevWidget.setObjectName(self.ui.idle_style_tag)
            for i in range(prevWidget.layout().count()):
                w = prevWidget.layout().itemAt(i).widget()
                w.setObjectName(self.ui.idle_style_tag)
            prevWidget.setStyleSheet(self.ui.main_style)
            prevWidget.layout().itemAt(1).widget().setText(valueDesc)
        currWidget = self.ui.content_layout.itemAt(index).widget()
        currWidget.setObjectName(self.ui.selected_style_tag)
        for i in range(currWidget.layout().count()):
            w = currWidget.layout().itemAt(i).widget()
            w.setObjectName(self.ui.selected_style_tag)
        currWidget.setStyleSheet(self.ui.main_style)
        self.ui.scroll.ensureWidgetVisible(currWidget)
        self.currentButton = self.padLayout[index]
        if self.currentButton == homeButton:
            self.ui.statusLabel.setText(self.ui.homeText)
        else:
            self.ui.statusLabel.setText(self.ui.defaultText)

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
            prevText = self.ui.content_layout.itemAt(self.currentIndex).widget().layout().itemAt(1).widget().text()

            if a0.key() == Qt.Key.Key_Up:
                if self.currentIndex > 0:
                    self.currentIndex -= 1

            elif a0.key() == Qt.Key.Key_Down:
                if self.currentIndex < len(self.padLayout) - 1:
                    self.currentIndex += 1

            elif a0.key() == Qt.Key.Key_Delete:
                w = self.ui.content_layout.itemAt(prevIndex).widget()
                w.layout().itemAt(1).widget().setText(self.ui.notAssignedText)

            if prevIndex != self.currentIndex:
                if prevText in (self.ui.notAssignedText, self.ui.alreadyAssignedText):
                    valueDesc = self.ui.omittedText
                else:
                    valueDesc = prevText
                if self.headlessMode and prevIndex == len(self.padLayout) - 1 and valueDesc == self.ui.omittedText:
                    self.endHeadlessConfig(prevIndex, valueDesc)
                else:
                    self.updateNextButton(self.currentIndex, prevIndex, valueDesc)

        if self.ui.content_widget.isVisible():
            self.ui.content_widget.setFocus(Qt.FocusReason.NoFocusReason)

    def endHeadlessConfig(self, index, text):
        w = self.ui.content_layout.itemAt(index).widget()
        w.layout().itemAt(1).widget().setText(text)
        # force updating label content (blocked by dialogs in saveConfig() otherwise)
        w.update()
        w.hide()
        w.show()
        self.configEnded = True
        self.saveConfig()

    def forceClose(self, checked=False, dialog_to_close=None):
        self.forceCloseRequested = True
        if dialog_to_close is not None:
            dialog_to_close.accept()
        # using just self.close() it will not actually close!
        self.closeEvent()

    def closeEvent(self, a0=None):

        if self.forceCloseRequested or self.headlessMode:
            # quit listener, warn parent (if signal is not None) and close tool (if standalone)
            self.listener_thread.quit()
            if self.mapperClosedSig is not None:
                self.mapperClosedSig.emit(self.configEnded)
            if self.standalone:
                # only force exit if running in standalone mode
                sys.exit()

        else:
            # ask user. It user replies yes, closing will be forced using forceClose()
            a0.ignore()
            self.ui.cancelDialog.exec()
