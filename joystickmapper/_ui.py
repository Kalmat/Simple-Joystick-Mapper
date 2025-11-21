from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QStatusBar, QGraphicsView, \
    QGraphicsScene, QGraphicsProxyWidget, QScrollArea, QComboBox, QPushButton, QSizePolicy, QMessageBox

from ._scrolllabel import ScrollLabel
from ._langtexts import *
from ._utils import *


class MainWindow_UI:

    def __init__(self, parent, rotate_widget, angle, headless_mode, inspect_mode, windowed, pad_layout, ref_pad_layout):

        self.parent = parent
        self.rotateWidget = rotate_widget
        self.angle = angle
        self.headlessMode = headless_mode
        self.inspectMode = inspect_mode
        self.windowed = windowed
        self.padLayout = pad_layout
        self.refPadLayout = ref_pad_layout

        self.setupUI()
        self.setupUIInspect()
        self.setupDialogs()

    def setupUI(self):

        self.parent.setMinimumWidth(860)

        self.header_style = open(resource_path("qss/header.qss", module="joystickmapper"), "r").read()
        self.main_style = open(resource_path("qss/main.qss", module="joystickmapper"), "r").read()
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

            self.graphicsview = QGraphicsView(self.parent)
            self.graphicsview.setInteractive(True)
            self.graphicsview.installEventFilter(self.parent)
            self.graphicsview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.graphicsview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scene = QGraphicsScene(self.graphicsview)
            self.graphicsview.setScene(self.scene)

            self.proxy = QGraphicsProxyWidget()
            self.proxy.setWidget(self.widget2)
            self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())
            self.scene.addItem(self.proxy)
            if not self.windowed:
                h, w = self.parent.screen().size().width(), self.parent.screen().size().height()
                self.graphicsview.setGeometry(0, 0, w, h)
                self.proxy.setGeometry(QRectF(0, 0, w, h))
            self.myLayout2.addWidget(self.graphicsview)

        self.buttonsFont = self.parent.font()
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

            joyName_lbl = QLabel(getHeaderText("joy"))
            joyName_lbl.setFont(font)
            self.headerLayout.addWidget(joyName_lbl, 0, 0)
            self.joyNameCombo = QComboBox()
            self.joyNameCombo.setFont(font)
            self.joyNameCombo.setMinimumWidth(300)
            self.joyNameCombo.setMaximumWidth(500)
            self.joyNameCombo.setMinimumHeight(30)
            self.joyNameCombo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.headerLayout.addWidget(self.joyNameCombo, 0, 1, Qt.AlignmentFlag.AlignVCenter)

            layout_lbl = QLabel(getHeaderText("lay"))
            layout_lbl.setFont(font)
            self.headerLayout.addWidget(layout_lbl, 0, 2)
            self.layoutCombo = QComboBox()
            self.layoutCombo.setFont(font)
            self.layoutCombo.setMaximumWidth(200)
            self.layoutCombo.setMinimumHeight(30)
            self.layoutCombo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.headerLayout.addWidget(self.layoutCombo, 0, 3, Qt.AlignmentFlag.AlignVCenter)

            self.toggleInspect = QPushButton()
            self.toggleInspect.setMinimumWidth(120)
            self.toggleInspect.setMinimumHeight(30)
            self.toggleInspect.setFont(font)
            self.toggleInspect.setText(getHeaderText("norm") if self.inspectMode else getHeaderText("deb"))
            self.headerLayout.addWidget(self.toggleInspect, 0, 4)

            dummylabel = QLabel()
            self.headerLayout.addWidget(dummylabel, 0, 5)

            self.saveConfig_btn = QPushButton()
            self.saveConfig_btn.setMinimumWidth(120)
            self.saveConfig_btn.setMinimumHeight(30)
            self.saveConfig_btn.setFont(font)
            self.saveConfig_btn.setText(getHeaderText("save"))
            self.headerLayout.addWidget(self.saveConfig_btn, 0, 6)

            self.loadConfig_btn = QPushButton()
            self.loadConfig_btn.setMinimumWidth(120)
            self.loadConfig_btn.setMinimumHeight(30)
            self.loadConfig_btn.setFont(font)
            self.loadConfig_btn.setText(getHeaderText("load"))
            self.headerLayout.addWidget(self.loadConfig_btn, 0, 7)

            self.headerLayout.setColumnStretch(0, 0)
            self.headerLayout.setColumnStretch(1, 0)
            self.headerLayout.setColumnStretch(2, 0)
            self.headerLayout.setColumnStretch(3, 0)
            self.headerLayout.setColumnStretch(4, 0)
            self.headerLayout.setColumnStretch(5, 1)
            self.headerLayout.setColumnStretch(6, 0)
            self.headerLayout.setColumnStretch(7, 0)

            self.mainLayout.addWidget(self.headerWidget)
            rowIndex += 1

        self.joystick_widget = QWidget(self.widget2 if self.rotateWidget else self.parent)
        self.joystick_widget.setStyleSheet(self.header_style)
        self.joystick_widget.setContentsMargins(5, 5, 5, 5)
        joystick_layout = QGridLayout()
        self.joystick_widget.setLayout(joystick_layout)
        self.idLabel = QLabel(self.widget2 if self.rotateWidget else self.parent)
        self.idLabel.setStyleSheet(self.header_style)
        self.idLabel.setFont(self.buttonsFont)
        joystick_layout.addWidget(self.idLabel, 0, 0)
        self.nameLabel = QLabel(self.widget2 if self.rotateWidget else self.parent)
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

        self.notAssignedText = getButtonValueText("no")
        self.alreadyAssignedText = getButtonValueText("rep")
        self.omittedText = getButtonValueText("omi")

        self.setupLayoutGrid(self.padLayout, self.refPadLayout)

        self.scroll = QScrollArea(self.widget2 if self.rotateWidget else self.parent)
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
        self.defaultText = getStatusText("default")
        self.homeText = getStatusText("home")
        self.repeatedText = getStatusText("repeated")
        self.statusLabel = QLabel(self.defaultText)
        self.statusBar.addWidget(self.statusLabel)
        if not self.inspectMode:
            self.mainLayout.addWidget(self.statusBar, rowIndex, 0, 1, 2)

        self.scroll.verticalScrollBar().setValue(0)

        if self.rotateWidget:
            self.widget2.setLayout(self.mainLayout)
            self.mainWidget.setLayout(self.myLayout2)
            self.proxy.setRotation(self.angle)
        else:
            self.mainWidget.setLayout(self.mainLayout)
        self.parent.setCentralWidget(self.mainWidget)

    def setupLayoutGrid(self, pad_layout, ref_pad_layout):

        self.button_widget_margin = 15
        self.content_widget = QWidget(self.widget2 if self.rotateWidget else self.parent)
        self.content_widget.setStyleSheet(self.main_style)
        self.content_layout = QGridLayout()
        self.content_widget.setLayout(self.content_layout)

        if len(pad_layout) > len(ref_pad_layout):
            ref_pad_layout = pad_layout

        for i, button in enumerate(ref_pad_layout):
            if i < len(pad_layout):
                button = pad_layout[i]
            objectName = self.selected_style_tag if i == 0 else self.idle_style_tag
            button_widget = QWidget(self.widget2 if self.rotateWidget else self.parent)
            button_widget.setObjectName(objectName)
            button_widget.setStyleSheet(self.main_style)
            button_widget.setContentsMargins(5, self.button_widget_margin, 5, self.button_widget_margin)
            button_layout = QGridLayout()
            button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            button_widget.setLayout(button_layout)
            button_label = QLabel(button, self.widget2 if self.rotateWidget else self.parent)
            button_label.setObjectName(objectName)
            button_label.setFont(self.buttonsFont)
            button_layout.addWidget(button_label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            button_value = QLabel(self.notAssignedText, self.widget2 if self.rotateWidget else self.parent)
            button_value.setObjectName(objectName)
            button_value.setFont(self.buttonsFont)
            button_layout.addWidget(button_value, 0, 1, 1, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            button_layout.setColumnStretch(0, 1)
            button_layout.setColumnStretch(1, 0)
            self.content_layout.addWidget(button_widget, i, 0, 1, 2)
            if i >= len(pad_layout):
                button_widget.hide()

    def updateLayoutGrid(self, pad_layout, ref_pad_layout):

        if len(pad_layout) > len(ref_pad_layout):
            ref_pad_layout = pad_layout

        for i, button in enumerate(ref_pad_layout):
            button_widget = self.content_layout.itemAt(i).widget()
            if i < len(pad_layout):
                objectName = self.selected_style_tag if i == 0 else self.idle_style_tag
                button = pad_layout[i]
                button_widget.setObjectName(objectName)
                button_widget.setStyleSheet(self.main_style)
                button_label = button_widget.layout().itemAt(0).widget()
                button_label.setText(button)
                button_label.setObjectName(objectName)
                button_label.setStyleSheet(self.main_style)
                button_value = button_widget.layout().itemAt(1).widget()
                value = self.notAssignedText
                button_value.setText(value)
                button_value.setObjectName(objectName)
                button_value.setStyleSheet(self.main_style)
                button_widget.show()
            else:
                button_widget.hide()

    def loadNewLayoutGrid(self, pad_layout, ref_pad_layout):

        if len(pad_layout) > len(ref_pad_layout):
            ref_pad_layout = pad_layout

        pad_keys = list(pad_layout.keys())

        for i, button in enumerate(ref_pad_layout):
            button_widget = self.content_layout.itemAt(i).widget()
            if i < len(pad_layout):
                objectName = self.selected_style_tag if i == 0 else self.idle_style_tag
                button_widget.setObjectName(objectName)
                button_widget.setStyleSheet(self.main_style)
                button_label = button_widget.layout().itemAt(0).widget()
                button_label.setText(button)
                button_label.setObjectName(objectName)
                button_label.setStyleSheet(self.main_style)
                button_value = button_widget.layout().itemAt(1).widget()
                if button in pad_keys:
                    value = pad_layout[button]
                else:
                    value = self.notAssignedText
                button_value.setText(value)
                button_value.setObjectName(objectName)
                button_value.setStyleSheet(self.main_style)
                button_widget.show()

        for i in range(len(ref_pad_layout), self.content_layout.count()):
            button_widget = self.content_layout.itemAt(i).widget()
            button_widget.hide()

    def setupUIInspect(self):

        self.inspectWidget = ScrollLabel()
        self.inspectWidget.setStyleSheet(open(resource_path("qss/inspect.qss", module="joystickmapper"), "r").read())

        if self.inspectMode:
            self.mainLayout.addWidget(self.inspectWidget, 0 if self.headlessMode else 1, 0, 1, 4)
        else:
            self.inspectWidget.hide()

    def setupDialogs(self):

        self.controllersChangedDialog = QMessageBox(self.parent)
        self.controllersChangedDialog.setText(getDialogsText("changed"))
        accept = self.controllersChangedDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

        self.controllersChangedHeadlessDialog = QMessageBox(self.parent)
        self.controllersChangedHeadlessDialog.setText(getDialogsText("changed_headless"))
        accept = self.controllersChangedHeadlessDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.controllersChangedHeadlessDialog.removeButton(accept)

        self.noControllersDialog = QMessageBox(self.parent)
        self.noControllersDialog.setText(getDialogsText("no"))
        accept = self.noControllersDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

        self.noControllersHeadlessDialog = QMessageBox(self.parent)
        self.noControllersHeadlessDialog.setText(getDialogsText("no_headless"))
        accept = self.noControllersHeadlessDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.noControllersHeadlessDialog.removeButton(accept)

        self.controllersDisconnectedDialog = QMessageBox(self.parent)
        self.controllersDisconnectedDialog.setText(getDialogsText("disconnected"))
        accept = self.controllersDisconnectedDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)

        self.controllersDisconnectedHeadlessDialog = QMessageBox(self.parent)
        self.controllersDisconnectedHeadlessDialog.setText(getDialogsText("disconnected_headless"))
        accept = self.controllersDisconnectedHeadlessDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.controllersDisconnectedHeadlessDialog.removeButton(accept)

        self.controllerConfiguredHeadlessDialog = QMessageBox(self.parent)
        self.controllerConfiguredHeadlessDialog.setText(getDialogsText("success_headless"))
        accept = self.controllerConfiguredHeadlessDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.controllerConfiguredHeadlessDialog.removeButton(accept)

        self.cancelDialog = QMessageBox(self.parent)
        self.cancelDialog.setText(getDialogsText("cancel"))
        reject = self.cancelDialog.addButton(getButtonsText("cancel"), QMessageBox.ButtonRole.RejectRole)
        self.cancelDialog_btn = self.cancelDialog.addButton(getButtonsText("quit"), QMessageBox.ButtonRole.AcceptRole)

        self.changeDialog = QMessageBox(self.parent)
        self.changeDialog.setText(getDialogsText("change"))
        reject = self.changeDialog.addButton(getButtonsText("cancel"), QMessageBox.ButtonRole.RejectRole)
        self.changeDialog_btn = self.changeDialog.addButton(getButtonsText("change"), QMessageBox.ButtonRole.AcceptRole)

        self.completeLayoutDialog = QMessageBox(self.parent)
        self.completeLayoutDialog.setText(getDialogsText("complete"))
        accept = self.completeLayoutDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.RejectRole)

        self.completeLayoutHeadlessDialog = QMessageBox(self.parent)
        self.completeLayoutHeadlessDialog.setText(getDialogsText("complete_headless"))
        accept = self.completeLayoutHeadlessDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
        self.completeLayoutHeadlessDialog.removeButton(accept)

        self.saveDialog = QMessageBox(self.parent)
        self.saveDialog.setText(getDialogsText("save"))
        reject = self.saveDialog.addButton(getButtonsText("cancel"), QMessageBox.ButtonRole.RejectRole)
        self.saveDialog_btn = self.saveDialog.addButton(getButtonsText("save"), QMessageBox.ButtonRole.AcceptRole)

        self.savedDialog = QMessageBox(self.parent)
        self.savedDialog.setText(getDialogsText("saved"))
        accept = self.savedDialog.addButton(getButtonsText("accept"), QMessageBox.ButtonRole.AcceptRole)
