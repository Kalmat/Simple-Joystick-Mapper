homeButton = "HOME"

# these values will be used to display buttons and as keys in the output dictionary
# content between parenthesis "(...)", will be shown on screen, but ignored in the dictionary keys
layouts = {
    "Menu": ["UP", "DOWN", "LEFT", "RIGHT",
             "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "R1",
             "SELECT", "START"],
    "Retro": ["UP", "DOWN", "LEFT", "RIGHT",
              "A (SOUTH)", "B (EAST)",
              "SELECT", "START"],
    "Retro Plus": ["UP", "DOWN", "LEFT", "RIGHT",
                   "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "R1",
                   "SELECT", "START"],
    "Arcade": ["ANALOG UP", "ANALOG DOWN", "ANALOG LEFT", "ANALOG RIGHT",
               "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "R1",
               "SELECT", "START"],
    "Arcade Plus": ["ANALOG UP", "ANALOG DOWN", "ANALOG LEFT", "ANALOG RIGHT",
                    "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "L2", "R1", "R2",
                    "SELECT", "START", homeButton],
    "Gamepad": ["D-UP", "D-DOWN", "D-LEFT", "D-RIGHT",
                "ANALOG UP", "ANALOG DOWN", "ANALOG LEFT", "ANALOG RIGHT",
                "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "R1",
                "SELECT", "START"],
    "Gamepad Plus": ["D-UP", "D-DOWN", "D-LEFT", "D-RIGHT",
                     "ANALOG UP", "ANALOG DOWN", "ANALOG LEFT", "ANALOG RIGHT",
                     "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "L2", "R1", "R2",
                     "SELECT", "START", homeButton],
    "Completo": ["D-UP", "D-DOWN", "D-LEFT", "D-RIGHT",
                 "LEFT ANALOG UP", "LEFT ANALOG DOWN", "LEFT ANALOG LEFT", "LEFT ANALOG RIGHT",
                 "RIGHT ANALOG UP", "RIGHT ANALOG DOWN", "RIGHT ANALOG LEFT", "RIGHT ANALOG RIGHT",
                 "A (SOUTH)", "B (EAST)", "X (WEST)", "Y (NORTH)", "L1", "L2", "L3", "R1", "R2", "R3",
                 "SELECT", "START", homeButton]
}