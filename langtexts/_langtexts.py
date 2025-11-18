import sys

from joystickmapper import layouts, angles


def getInitMessage(lang="es"):
    if "python" in sys.executable.lower():
        target_exe = "python joystickmapper.py"
    else:
        target_exe = "JoystickMapper.exe"

    return "\nThis script will help to map the buttons, axes and triggers of (hopefully almost) any controller.\n" \
           "Although it is not strictly necessary, it is always recommendable to use a keyboard during configuration:\n" \
           "\t↑ ↓ : Move up / down (and omit if button not assigned)\n" \
           "\tDel : Delete current button value and set as not assigned\n" \
           "\tEsc : Exit program (if in headless mode, config will be auto-saved, complete or not)\n" \
           "After a successful configuration, find the output in '[LAYOUT]_[JOYSTICK NAME].json' file:\n" \
           '\t"type": event type as per pygame values:\n' \
           "\t\t1539: Button (down)\n" \
           "\t\t1538: Hat (aka D-Pad or Directional Pad)\n" \
           "\t\t1536: Axis (aka Analog Joysticks. Triggers, like L2 and R2, will also be recognized as axis)\n" \
           '\t"description": human-readable description of event type\n' \
           '\t"value": value returned by button, hat or axis when pressed (hat and axis will be tuples)\n' \
           '\t"hat" or "axis": value which identifies which hat or axis has been pressed (not present for buttons)\n\n' \
           "USAGE:\n\n" \
           "\t" + target_exe + " [ARGS] [OPTIONS]\n\n" \
           "\tARGS:\n" \
           "\t\t-l\tSelect controller layout. Choose one of these values: " + str(['INSPECT'] + list(layouts.keys())) + ".\n" \
           "\t\t\t'INSPECT' mode will show and save (to 'joystickmapper_inspect.json' file) all controllers events. Very useful to DEBUG.\n" \
           "\t\t\tAdd custom layouts of your choice just creating/adding them to 'custom_layouts.json' file (check the example included).\n" \
           "\t\t-j\tSelect controller instance. If not selected, the tool will address the first in which any button is pressed.\n" \
           "\t\t-a\tSelect window rotation on screen. Choose one of these values: " + str(angles) + ".\n" \
           "\t\t\tIf the window is rotated (angle not equal 0), it will show in fullscreen mode.\n" \
           "\t\t-o\tSet custom configuration output file.\n" \
           "\tOPTIONS:\n" \
           "\t\t--s\tHeadless mode: suitable for non-mouse environments (e.g. an arcade system or menu).\n" \
           "\t\t\tHeadless mode will automatically save and exit when last button is successfully configured or omitted.\n" \
           "\t\t--w\tHeadless mode shows in fullscreen by default. Use this option to show windowed (and frameless).\n\n"


def getJoysticksMessages(lang="es"):
    if lang == "es":
        headerMsg = "MANDOS ENCONTRADOS!"
    else:
        headerMsg = "CONTROLLERS FOUND!"
    joyMsg = "\t%s\n" \
             "\t\tINSTANCE: %s\n" \
             "\t\tGUID: %s\n" \
             "\t\tID: %s\n"
    return headerMsg, joyMsg


def getHeaderText(text, lang="es"):
    if text == "joy":
        if lang == "es":
            return "Mando:"
        else:
            return "Controller:"

    elif text == "lay":
        if lang == "es":
            return "Tipo:"
        else:
            return "Layout:"

    elif text == "norm":
        if lang == "es":
            return "Modo NORMAL"
        else:
            return "NORMAL Mode"

    elif text == "deb":
        if lang == "es":
            return "Modo DEBUG"
        else:
            return "DEBUG Mode"

    elif text == "save":
        if lang == "es":
            return "Guardar"
        else:
            return "Save"


def getButtonValueText(text, lang="es"):
    if text == "no":
        if lang == "es":
            return "No asignado"
        else:
            return "Not assigned"

    elif text == "rep":
        if lang == "es":
            return "Ya asignado"
        else:
            return "Already assigned"

    elif text == "omi":
        if lang == "es":
            return "OMITIDO"
        else:
            return "OMITTED"


def getStatusText(text, lang="es"):
    if text == "home":
        if lang == "es":
            return "Puedes asignar cualquier botón como 'HOME', aunque ya esté asignado previamente"
        else:
            return "You can assign any button as 'HOME', even though it is already assigned"
    elif text == "repeated":
        if lang == "es":
            return "Ya asignado. Intenta con otro botón o mantén pulsado para ignorar"
        else:
            return "Already assigned. Try another button or keep any button pressed to omit"
    elif text == "default":
        if lang == "es":
            return "Presiona para ASIGNAR a la función seleccionada o mantén pulsado para OMITR"
        else:
            return "Press to ASSIGN to the selected function or keep pressed to OMIT"


def getDialogsText(text, lang="es"):
    if text == "changed":
        if lang == "es":
            return "Los mandos conectados han cambiado.\n" \
                   "Por favor, comienza de nuevo la configuración.\n\n"
        else:
            return "Connected controllers have changed.\n" \
                   "Please, re-start the configuration.\n\n"

    elif text == "changed_headless":
        if lang == "es":
            return "Los mandos conectados han cambiado.\n" \
                   "Por favor, comienza de nuevo la configuración.\n\n" \
                   "Esta ventana se cerrará en 3 segundos.\n\n"
        else:
            return "Connected controllers have changed.\n" \
                   "Please, restart the configuration.\n\n" \
                   "This dialog will automatically close in 3 seconds.\n\n"

    elif text == "no":
        if lang == "es":
            return "No se ha encontrado ningún mando.\n" \
                   "Por favor, conecta al menos uno.\n\n"
        else:
            return "No controller found.\n" \
                   "Please, connect at least one.\n\n"

    elif text == "no_headless":
        if lang == "es":
            return "No se ha encontrado ningún mando.\n" \
                   "Por favor, conecta al menos uno.\n\n" \
                   "Esta ventana se cerrará en 3 segundos\n\n"
        else:
            return "No controller found.\n" \
                   "Please, connect at least one.\n\n" \
                   "This dialog will automatically close in 3 seconds.\n\n"

    elif text == "disconnected":
        if lang == "es":
            return "Los mandos se han desconectado.\n" \
                   "Por favor, vuelve a conectarlos.\n\n"
        else:
            return "Controllers have disconnected.\n" \
                   "Please, reconnect them again.\n\n"

    elif text == "disconnected_headless":
        if lang == "es":
            return "El mando se ha desconectado.\n" \
                   "Por favor, conéctalo y vuelve a intentarlo.\n\n" \
                   "Esta ventana se cerrará en 3 segundos.\n\n"
        else:
            return "The controller has disconnected.\n" \
                   "Please, reconnect and try again.\n\n" \
                   "This dialog will automatically close in 3 seconds.\n\n"

    elif text == "success_headless":
        if lang == "es":
            return "Mando configurado corretamente!!!\n\n" \
                   "Esta ventana se cerrará en 3 segundos.\n\n"
        else:
            return "The controller has been correcly configured!!!\n\n" \
                   "This dialog will automatically close in 3 seconds.\n\n"

    elif text == "cancel":
        if lang == "es":
            return "Si cancelas ahora, perderás toda la configuración.\n" \
                   "Para salvarla, pulsa 'Guardar' antes de salir.\n\n" \
                   "¿Deseas salir ahora?"
        else:
            return "All progress will be lost if you quit now.\n" \
                   "To save the current configuration, press 'Save' before exit.\n\n" \
                   "Do you want to quit now?"

    elif text == "change":
        if lang == "es":
            return "Si cambias ahora, perderás toda la configuración.\n" \
                   "Para salvarla, pulsa 'Guardar' antes de cambiar.\n\n" \
                   "¿Deseas cambiar ahora?"
        else:
            return "If you change now, all progress will be lost.\n" \
                   "To save the current configuration, press 'Save' before changing.\n\n" \
                   "Do you want to change now?"

    elif text == "save":
        if lang  == "es":
            return "Estás a punto de guardar esta configuración.\n\n" \
                   "¿Deseas guardar ahora?"
        else:
            return "You are about to save the current configuration.\n\n" \
                   "Do you want to save now?"

    elif text == "saved":
        if lang == "es":
            return "Configuración guardada con éxito!!!\n\n"
        else:
            return "Configuration has been successfully saved!!!\n\n"


def getButtonsText(text, lang="es"):
    if text == "accept":
        if lang == "es":
            return "Aceptar"
        else:
            return "Accept"

    elif text == "cancel":
        if lang == "es":
            return "Cancelar"
        else:
            return "Cancel"

    elif text == "change":
        if lang == "es":
            return "Cambiar"
        else:
            return "Change"

    elif text == "save":
        if lang == "es":
            return "Guardar"
        else:
            return "Save"

    elif text == "quit":
        if lang == "es":
            return "Salir"
        else:
            return "Quit"


def getErrorText(text, lang="es"):
    if text == "layout_mismatch":
        if lang == "es":
            return "ERROR de sintaxis en los formatos custom. Comprueba el contenido y reinicia"
        else:
            return "ERROR: Custom layouts mismatch. Please check and re-run this tool if necessary."
    elif text == "layout":
        if lang == "es":
            return f"Layout errónea. Selecciona uno de estos valores: {str(['INSPECT'] + list(layouts.keys()))}"
        else:
            return f"Wrong layout value. Please select one of these values: {str(['INSPECT'] + list(layouts.keys()))}"
    elif text == "angle":
        if lang == "es":
            return f"Ángulo de rotación erróneo. Selecciona una de estos valores: {str(angles)}"
        else:
            return f"Wrong angle value. Please select one of these values: {str(angles)}"
