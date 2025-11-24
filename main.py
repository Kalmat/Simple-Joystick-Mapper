import signal
import sys
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from joystickmapper._utils import is_packaged
from joystickmapper import Mode, Angle
from joystickmapper._mapper import JoystickMapper
from joystickmapper._langtexts import getInitMessage


def showInitMessage():
    print(getInitMessage())


def getArgs():
    pad_layout = Mode.FULL
    joystick_id = None
    angle = Angle.NOT_ROTATED
    output_file = None
    headless_mode = "--s" in sys.argv
    windowed = "--w" in sys.argv
    force_complete_layout = "--f" in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == "-l":
            pad_layout = str(sys.argv[i + 1])
            if pad_layout == "Full":
                pad_layout = "Completo"
        elif arg == "-j":
            joystick_id = str(sys.argv[i + 1])
        elif arg == "-a":
            angle = int(sys.argv[i + 1])
        elif arg == "-o":
            output_file = str(sys.argv[i + 1])
    return pad_layout, joystick_id, angle, headless_mode, windowed, output_file, force_complete_layout


def sigint_handler(*args):
    # https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co
    app.closeAllWindows()


def exception_hook(exctype, value, tb):
    # https://stackoverflow.com/questions/56991627/how-does-the-sys-excepthook-function-work-with-pyqt5
    traceback_formated = traceback.format_exception(exctype, value, tb)
    traceback_string = "".join(traceback_formated)
    print(traceback_string)
    sys.exit(1)


if __name__ == "__main__":

    if not is_packaged():
        # This will allow to manage Ctl-C interruption (e.g. when running from IDE)
        signal.signal(signal.SIGINT, sigint_handler)
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(500)

    # This will allow to catch and show some tracebacks (not all, anyway)
    sys._excepthook = sys.excepthook
    sys.excepthook = exception_hook

    showInitMessage()

    app = QApplication(sys.argv)
    app.setApplicationName("Simple Joystick Mapper")
    pad_layout, joystick_id, angle, headless_mode, windowed, output_file, force_complete_layout = getArgs()
    win = JoystickMapper(pad_layout, joystick_id, angle, headless_mode, windowed, output_file,
                         standalone_mode=True, force_complete_layout=force_complete_layout)
    win.show()
    app.exec()
