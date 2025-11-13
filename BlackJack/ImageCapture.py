"""
===========================================================
Program Name: ImageCapture.py
Author: Matthew Fuentes
Date: 11/12/25
Description:
    This program takes a screenshot of a specific window, plugs it into an image analysis program, and deletes
        the screenshot after use.
    It is designed to capture an image for analysis in order to determine the best odds when playing gambling games
        involving cards.
    
Usage:
    Run the script using Python 3.9.21 or greater. 
    
    Dependances:
    - Pillow


    *Ensure all dependencies
    are installed before execution.

===========================================================
"""
import time
import os
from PIL import ImageGrab

running = True

# Checks which OS the program is running on and creates appropriate directory for program screenshots to be stored
osname = os.name

if osname.lower() == 'nt':
    newpath = r'C:\CardCounter'
    if newpath:
        pass
    else:
        os.makedirs(newpath)

elif osname.lower() == 'posix':
    newpath = r'./CardCounter'
    if newpath:
        pass
    else:
        os.makedirs(newpath)

elif osname.lower() == 'macos':
    newpath = r'.\CardCounter'
    if newpath:
        pass
    else:
        os.makedirs(newpath)

# Screenshot function
while running == True:

    print("Press Ctrl + C to stop screenshots")

    # Capture the blackjack screen for analysis
    screenshot = ImageGrab.grab(bbox=(5, 157, 2062, 1387))

    # Save the screenshot to a file and store in variable
    imagecapture = screenshot.save("./CardCounter/imagecapture.png")

    # Close the screenshot
    screenshot.close()
    print("Screenshot taken")

    time.sleep(5)
