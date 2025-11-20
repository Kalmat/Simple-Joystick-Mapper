import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

from PyQt5.QtCore import QThread, pyqtSlot


class JoystickListener(QThread):

    def __init__(self, parent, joysticksConnectedSig, buttonValueSig, toggleInspectModeSig, free_mode=False):
        super().__init__(parent)

        self.joysticksConnectedSig = joysticksConnectedSig
        self.buttonValueSig = buttonValueSig
        self.freeMode = free_mode
        self.keepListening = True

        toggleInspectModeSig.connect(self.toggleFreeMode)

        self.joysticks = []
        self.joysticksInfo = {}

        self.clock = pygame.time.Clock()
        self.fps = 60
        self.counter = None
        self.ignoreCount = self.fps * 3  # 3 seconds is the standard to skip a button
        self.ignoreNextButtonUp = False
        self.ignoreNextAxis = None

    @pyqtSlot(bool)
    def toggleFreeMode(self, enable):
        self.freeMode = enable

    def addJoysticks(self):

        joysticks = []
        joysticksInfo = {}
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joysticksInfo[str(joystick.get_instance_id())] = {
                "name": joystick.get_name(),
                "guid": joystick.get_guid(),
                "id": str(joystick.get_id())
            }
            joysticks.append(joystick)
            if not joystick.get_init():
                joystick.init()

        return joysticks, joysticksInfo

    def closeListener(self):
        if pygame.joystick.get_init() and not self.pygameJoystickPreInitialized:
            # pygame.joystick system might be initialized by "parent" script. Not quitting here
            for joystick in self.joysticks:
                if joystick.get_init():
                    try:
                        joystick.quit()
                    except:
                        pass
            try:
                pygame.joystick.quit()
            except:
                pass
        if pygame.get_init() and not self.pygamePreInitialized:
            # pygame might be initialized by "parent" script. Not quitting here
            try:
                pygame.quit()
            except:
                pass

    def run(self):

        # initialize everything if not previously initialized
        self.pygamePreInitialized = pygame.get_init()
        self.pygameJoystickPreInitialized = pygame.joystick.get_init()
        if not self.pygamePreInitialized:
            pygame.init()
        if not self.pygameJoystickPreInitialized:
            pygame.joystick.init()

        # get and emit connected joysticks info
        self.joysticks, self.joysticksInfo = self.addJoysticks()
        self.joysticksConnectedSig.emit(self.joysticksInfo)

        while self.keepListening:

            if self.counter is not None:
                self.counter += 1
                if self.counter > self.ignoreCount:
                    self.counter = None
                    fakeEvent = pygame.event.Event(-1, {})
                    self.ignoreNextButtonUp = True
                    self.buttonValueSig.emit(fakeEvent)

            for event in pygame.event.get():

                if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                    self.joysticks, joysticksInfo = self.addJoysticks()
                    if self.joysticksInfo != joysticksInfo:
                        # update joysticks info in case it changes
                        self.joysticksInfo = joysticksInfo
                        self.joysticksConnectedSig.emit(self.joysticksInfo)

                if self.freeMode:
                    print(event)
                    self.buttonValueSig.emit(event)

                else:

                    if event.type == pygame.JOYBUTTONDOWN:
                        self.counter = 0

                    elif event.type in (pygame.JOYBUTTONUP, pygame.JOYAXISMOTION, pygame.JOYHATMOTION):
                        print(event)

                        if event.type == pygame.JOYBUTTONUP:
                            self.counter = None
                            if not self.ignoreNextButtonUp:
                                self.buttonValueSig.emit(event)
                            self.ignoreNextButtonUp = False
                            self.ignoreNextAxis = None

                        elif event.type == pygame.JOYHATMOTION and event.value != (0, 0):
                            self.buttonValueSig.emit(event)
                            self.ignoreNextAxis = None

                        elif event.type == pygame.JOYAXISMOTION and abs(event.value) >= 1.0:
                            if (self.ignoreNextAxis is None or
                                    (self.ignoreNextAxis is not None and
                                     # this is totally empyrical: axis beyond 3 are typically triggers, not joysticks
                                     (self.ignoreNextAxis != event.axis or self.ignoreNextAxis <= 3))):
                                self.ignoreNextAxis = event.axis
                                self.buttonValueSig.emit(event)

            self.clock.tick(self.fps)

        self.closeListener()

    def getJoysticksInfo(self):
        if not pygame.joystick.get_init():
            self.joysticks, self.joysticksInfo = self.addJoysticks()
        return self.joysticksInfo

    def stop(self):
        self.keepListening = False