from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QLabel, QApplication


class ScrollLabel(QScrollArea):
    # thanks to eyllanesc: https://stackoverflow.com/questions/47862036/scrollable-label-using-pyqt5-for-python-gui

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setWidgetResizable(True)

        content = QWidget(self)
        self.setWidget(content)
        lay = QVBoxLayout(content)

        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self.label)

        self.verticalScrollBar().rangeChanged.connect(self.scroll_to_bottom)
        self.cursor = None

    def enterEvent(self, a0):
        QApplication.setOverrideCursor(Qt.CursorShape.IBeamCursor)

    def leaveEvent(self, a0):
        QApplication.restoreOverrideCursor()

    @pyqtSlot(int, int)
    def scroll_to_bottom(self, min_val, max_val):
        # scroll down to ensure visibility of new text added
        self.verticalScrollBar().setValue(max_val)

    def setText(self, text):
        # replace existing text with the new one provided
        self.label.setText(text)

    def appendText(self, text):
        # append text to the label (max. 64K chars), keeping existing text
        self.label.setText(self.label.text()[-65536:] + "\n" + text)

    def text(self):
        return self.label.text()
    