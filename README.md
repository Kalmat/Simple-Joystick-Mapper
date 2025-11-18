# Simple Joystick Mapper
This script will help to map the buttons, d-pads, axes and triggers of (hopefully almost) any controller. It is not very sophisticated, but it is extremely simple and easy to use. Aimed to be used within arcade systems and similar situations.

It is built with PyGame and PyQt, so it can be used as a stand-alone tool or embedded in your own code (just like any other QMainWindow).

Some useful features included in this tool:
- Choose controller (if several connected)
- Choose controller layout (Most typical layouts are already included: Menu, Retro, Arcade, Modern gamepad, etc.)
- Add custom layouts of your choice (check the example included in 'custom_layouts.json')
- Open "inspect" console which will show and save all events from all connected controllers. Very useful to debug.
- Show window rotated
- Show window in headless, non-interactive mode (suitable for non-mouse environments like an arcade system or menu)
- Show window in fullscreen or windowed modes
- Run class within your own code (*)

##### (*) Warning
If running JoystickMapper class within another script as a PyQt QMainWindow, the joystick listener included in this tool may interfere with other pygame event loops running. If this is the case, pause the existing loop or run the tool as a stand-alone application (running it with Python interpreter or using a tool like PyInstaller to pack an .exe file).

### Using an auxiliary keyboard
Although it is not strictly necessary, it is always recommendable to use a keyboard during configuration, allowing to: 

| Key | Description                                                         |
|-----|---------------------------------------------------------------------|
| ↑ ↓ | Move up / down (and omit if button not assigned)                    | 
| Del | Delete current button value and set as not assigned                 | 
| Esc | Exit program (if in headless mode, all non-saved data will be lost) | 

### Configuration output
After a successful configuration, find the output in '[LAYOUT]_[JOYSTICK NAME].json' (e.g. 'FULL_Xbox_360_Controller.json') file: 

| Key            | Values                          | Description                                                                       |
|----------------|---------------------------------|-----------------------------------------------------------------------------------|
| "type"         |                                 | event type as per pygame values:                                                  |
|                | "1539"                          | Button (down)                                                                     | 
|                | "1538"                          | Hat (aka D-Pad or Directional Pad)                                                | 
|                | "1536"                          | Axe (aka Analog Joysticks. Triggers will also be recognized as axes)              | 
| "description"  |                                 | human-readable description of event type:                                         |
|                | "BUTTON"                        |                                                                                   |
|                | "D-PAD"                         |                                                                                   |
|                | "ANALOG JOYSTICK / TRIGGER"     |                                                                                   |
| "hat" or "axe" | [#HAT] / [#AXE]                 | value to identify which hat or axis has been pressed (not present for buttons)    |
| "value"        | [#BUTTON] / ([#AXIS], [#VALUE]) | value returned by button, hat or axis when pressed (hat and axis will be tuples)  |

All values are integer or tuples of integers, representing:

- #BUTTON value returned by the controller when a button is pressed. It depends on the controller model
- #HAT value identifying the D-PAD pressed, typically numbered from 0 to N (in case the controller has more than one)
- #AXE value referencing the analog joystick pressed, also usually numbered from 0 to N. Triggers, like L2 and R2, will also be recognized as axes
- #AXIS value identifying the axis of the hat/axe used. They are usually numbered from 0 to N, but adding the vertical/horizontal differentiation of the axis used
- #VALUE will contain the value returned by the controller when the hat/axe is pressed (usually 1 or -1, thus returning 0 when coming back to idle position)

### Usage

    python joystickmapper.py [ARGS] [OPTIONS]

ARGS:

<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">-l</td>
    <td style="border: 1px solid transparent; padding: 8px;">Select controller layout. Choose one of these values: ['INSPECT', 'Menu', 'Retro', 'Retro Plus', 'Arcade', 'Arcade Plus', 'Gamepad', 'Gamepad Plus', 'Full']<br>
                                                             'INSPECT' mode will show and save (to 'joystickmapper_inspect.json' file) all controllers events.<br>
                                                             Add custom layouts of your choice just creating/adding them to 'custom_layouts.json' file.</td>
  </tr>
  <tr>
    <td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">-j</td>
    <td style="border: 1px solid transparent; padding: 8px;">Select controller instance. If not selected, the tool will address the first in which any button is pressed.</td>
  </tr>
  <tr>
    <td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">-a</td>
    <td style="border: 1px solid transparent; padding: 8px;">Select window rotation on screen. Choose one of these values: [90, 180, 270].<br>  
                                                             If the window is rotated (angle not equal 0), it will show in fullscreen mode.</td>
  </tr>
  <tr>
    <td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">-o</td>
    <td style="border: 1px solid transparent; padding: 8px;">Set custom configuration output file.</td>
  </tr>
</table>

OPTIONS:

<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">--s</td>
    <td style="border: 1px solid transparent; padding: 8px;">Headless mode: suitable for non-mouse environments (e.g. an arcade system or menu).<br>
                                                             Headless mode will automatically save and exit when last button is successfully configured.</td>
  </tr>
  <tr>
    <td style="border: 1px solid transparent; padding: 8px; vertical-align: top;">--w</td>
    <td style="border: 1px solid transparent; padding: 8px;">Rotated and Headless modes show in fullscreen by default. Use this option to show windowed (and frameless).</td>
  </tr>
</table>
