# Simple Joystick Mapper
This script will help to map the buttons, d-pads, axis and triggers of (hopefully almost) any controller. It is not very sophisticated, but it is extremely simple and easy to use. Aimed to be used within arcade systems and similar situations.

It is built with PyGame and PyQt, so it can be used as a stand-alone tool or embedded in your own code (just like any other QMainWindow).

Some useful features included in this tool:
- Choose controller (if several connected)
- Choose controller layout (Most typical layouts are already included: Menu, Retro, Arcade, Modern gamepad, etc.)
- Add custom layouts of your choice (check the example included in 'custom_layouts.json')
- Load existing configurations
- Open "inspect" console which will show and save all events from all connected controllers. Very useful to debug.
- Show window rotated
- Show window in headless, non-interactive mode (suitable for non-mouse environments like an arcade system or menu)
- Show window in fullscreen or windowed modes
- Embed the tool in your own app, and even run class within your own code (*)

##### (*) Warning
If running JoystickMapper class within another script as a PyQt QMainWindow, the joystick listener included in this tool may interfere with other pygame event loops running. If this is the case, pause the existing loop or run the tool as a stand-alone application (running it with Python interpreter or using a tool like PyInstaller to pack an .exe file).

### Using an auxiliary keyboard
Although it is not strictly necessary, it is always recommendable to use a keyboard during configuration, allowing to: 

| Key | Description                                                                             |
|-----|-----------------------------------------------------------------------------------------|
| ↑ ↓ | Move up / down (and omit if button not assigned)                                        | 
| Del | Delete current button value and set as not assigned                                     | 
| Esc | Exit program (if in headless mode, config progress will be auto-saved, complete or not) | 

### Configuration output
After a successful configuration, find the output in '[LAYOUT]_[JOYSTICK NAME].json' (e.g. 'FULL_Xbox_360_Controller.json') file: 

| Section               | Key             | Values                                        | Description                                                                    |
|-----------------------|-----------------|-----------------------------------------------|--------------------------------------------------------------------------------|
| "joysticks_info"      |                 |                                               | List and info of all connected controllers:                                    |
|                       | "instance_id"   |                                               | Instance id of the controller (may change when re-connected, etc.)             |
|                       |                 | "name"                                        | Human-readable name of the controller                                          |
|                       |                 | "guid"                                        | Internal id of the controller. Should be unique for brand / model              |
|                       |                 | "id"                                          | Id of the controller in the system (does not change within session)            |
| "layout"              |                 |                                               | Controller layout used in configuration as per joystickMapper.Mode.*           |
| "joystick_configured" |                 |                                               | Instance id of the configured controller (use it as key to get config info)    |
| "instance_id"         |                 |                                               | Configuration info for joystick assigned to instance id value                  |
|                       | "type"          |                                               | Event type as per pygame values:                                               |
|                       |                 | "1539"                                        | Button (down)                                                                  | 
|                       |                 | "1538"                                        | Hat (aka D-Pad or Directional Pad)                                             | 
|                       |                 | "1536"                                        | Axis (aka Analog Joysticks and Triggers)                                       | 
|                       | "description"   |                                               | human-readable description of event type:                                      |
|                       |                 | "BUTTON"                                      |                                                                                |
|                       |                 | "D-PAD"                                       |                                                                                |
|                       |                 | "ANALOG JOYSTICK / TRIGGER"                   |                                                                                |
|                       | "hat" or "axis" | [#HAT]<br>[#AXIS]                             | value to identify which hat or axis has been pressed (not present for buttons) |
|                       | "value"         | [#BUTTON]<br>[#VALUE]<br>([#AXIS], [#VALUE])  | value returned by button, hat or axis when pressed (hat will be a tuple)       |

All values are integer or tuples of integers, representing:

- #BUTTON value returned by the controller when a button is pressed. It depends on the controller model
- #HAT value identifying the D-PAD pressed, typically numbered from 0 to N (in case the controller has more than one)
- #AXIS value referencing the axis of the D_PAD or analog joystick pressed, also usually numbered from 0 to N. Triggers, like L2 and R2, will also be recognized as axis
- #VALUE will contain the value returned by the controller when the button/hat/axis is pressed (usually 1 or -1, thus returning 0 when coming back to idle position)

See example output at the end of this file.

### Usage

    python joystickmapper.py [ARGS] [OPTIONS]

ARGS:

| Argument | Description                                                                                                                                                                                                                                                                                                                                                     |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| -l       | Select controller layout. Choose one of these values: ['INSPECT', 'Menu', 'Retro', 'Retro Plus', 'Arcade', 'Arcade Plus', 'Gamepad', 'Gamepad Plus', 'Full']<br>'INSPECT' mode will show and save (to 'joystickmapper_inspect.json' file) all controllers events.<br>Add custom layouts of your choice just creating/adding them to 'custom_layouts.json' file. |
| -j       | Select controller instance. If not selected, the tool will address the first in which any button is pressed.                                                                                                                                                                                                                                                    |
| -a       | Select window rotation on screen. Choose one of these values: [90, 180, 270].<br>If the window is rotated (angle not equal 0), it will show in fullscreen mode.                                                                                                                                                                                                 |
| -o       | Set custom configuration output file.                                                                                                                                                                                                                                                                                                                           |

OPTIONS:

| Option | Description                                                                                                                                                                                   |
|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| --s    | Headless mode: suitable for non-mouse environments (e.g. an arcade system or menu).<br>Headless mode will automatically save and exit when last button is successfully configured or omitted. |
| --w    | Rotated and Headless modes show in fullscreen by default. Use this option to show windowed (and frameless).                                                                                   |
| --f    | Force to properly configure all buttons before closing (not leaving any as omitted or not assigned).                                                                                          |


### Output Example

    {
        "joysticks_info": {
            "0": {
                "name": "Xbox Series X Controller",
                "guid": "0300509d5e040000130b000001057200",
                "id": "0"
            },
            "1": {
                "name": "Xbox 360 Controller",
                "guid": "030003f05e0400008e02000000007200",
                "id": "1"
            }
        },
        "layout": "Completo",
        "joystick_configured": "1",
        "1": {
            "D-UP": {
                "type": 1538,
                "description": "D-PAD",
                "hat": 0,
                "value": [
                    0,
                    1
                ]
            },
            "D-DOWN": {
                "type": 1538,
                "description": "D-PAD",
                "hat": 0,
                "value": [
                    0,
                    -1
                ]
            },
            "D-LEFT": {
                "type": 1538,
                "description": "D-PAD",
                "hat": 0,
                "value": [
                    -1,
                    0
                ]
            },
            "D-RIGHT": {
                "type": 1538,
                "description": "D-PAD",
                "hat": 0,
                "value": [
                    1,
                    0
                ]
            },
            "LEFT ANALOG UP": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 1,
                "value": -1
            },
            "LEFT ANALOG DOWN": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 1,
                "value": 1
            },
            "LEFT ANALOG LEFT": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 0,
                "value": -1
            },
            "LEFT ANALOG RIGHT": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 0,
                "value": 1
            },
            "RIGHT ANALOG UP": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 3,
                "value": -1
            },
            "RIGHT ANALOG DOWN": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 3,
                "value": 1
            },
            "RIGHT ANALOG LEFT": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 2,
                "value": -1
            },
            "RIGHT ANALOG RIGHT": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 2,
                "value": 1
            },
            "A": {
                "type": 1540,
                "description": "BUTTON",
                "value": 0
            },
            "B": {
                "type": 1540,
                "description": "BUTTON",
                "value": 1
            },
            "X": {
                "type": 1540,
                "description": "BUTTON",
                "value": 2
            },
            "Y": {
                "type": 1540,
                "description": "BUTTON",
                "value": 3
            },
            "L1": {
                "type": 1540,
                "description": "BUTTON",
                "value": 4
            },
            "L2": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 4,
                "value": 1
            },
            "L3": {
                "type": 1540,
                "description": "BUTTON",
                "value": 8
            },
            "R1": {
                "type": 1540,
                "description": "BUTTON",
                "value": 5
            },
            "R2": {
                "type": 1536,
                "description": "ANALOG JOYSTICK / TRIGGER",
                "axis": 5,
                "value": -1
            },
            "R3": {
                "type": 1540,
                "description": "BUTTON",
                "value": 9
            },
            "SELECT": {
                "type": 1540,
                "description": "BUTTON",
                "value": 6
            },
            "START": {
                "type": 1540,
                "description": "BUTTON",
                "value": 7
            },
            "HOME": {
                "type": 1540,
                "description": "BUTTON",
                "value": 10
            }
        }
    }
