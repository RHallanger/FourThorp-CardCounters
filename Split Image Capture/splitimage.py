"""
===========================================================
Program Name: Split Image Capture
Author: Robert Hallanger
Date: 2025-11-19
Description:
    This program provides a small GUI to select separate locations to take screenshots for use in an image analyzer.
    It is designed to [specific purpose or goal].
    
Usage:
    Run the script using Python 3.13. 
    Ensure all dependencies are installed before execution.
    (Most should be installed by default)
    -pyautogui
    -PIL
    -functools
    -pynput
    -tkinter
    -os
    -pathlib
    -threading
    -time


NOTICE:
Pyautogui struggles with multiple monitors, please use the main monitor for the gameplay and screenshots.
This is a known issue that has not been resolved.

===========================================================
"""

#import pyautogui
from pynput import mouse
# from threading import Thread
# from time import sleep
from PIL import ImageGrab
from functools import partial
import tkinter as tk
import os
from pathlib import Path

root = tk.Tk()
home = Path.home()
(home/"fourthorpe_cache").mkdir(exist_ok=True,parents=True)

### Global variables to keep records of player and dealer screenshot locs
# This will let the user to drag to select the region for both screenshots to be recorded
playerCoords= {"px1":0, "py1":0, "px2":0, "py2":0}
dealerCoords= {"dx1":0, "dy1":0, "dx2":0, "dy2":0}

### THIS PORTION WILL TAKE SCREEN SHOTS


### THIS PORTION WILL HANDLE USER INPUTS FOR RECORDING REGIONS TO TAKE SCREENSHOTS
def playerHand():
    print("Please click and drag from the top-left of the area of the player's cards to the bottom-right")
    with mouse.Listener(on_click=playerOnClick) as playerListener:
        playerListener.join()
    return

def playerOnClick(x, y, button, pressed):
    global playerCoords
    if pressed:
        # Store the position when the mouse is pressed
        playerCoords["px1"], playerCoords["py1"] = x, y
    else:
        # Store the position when the mouse is released
        playerCoords["px2"], playerCoords["py2"] = x, y
        # Print or process the positions
        print(f'Pressed at ({playerCoords["px1"]}, {playerCoords["py1"]}) and released at ({playerCoords["px2"]}, {playerCoords["py2"]})')
        return False # These return Falses quit the listening thread

def dealerHand():
    print("Please click and drag from the top-left of the area of the dealer's cards to the bottom-right")
    with mouse.Listener(on_click=dealerOnClick) as dealerListener:
        dealerListener.join()
    return

def dealerOnClick(x, y, button, pressed):
    global dealerCoords
    if pressed:
        # Store the position when the mouse is pressed
        dealerCoords["dx1"], dealerCoords["dy1"] = x, y
    else:
        # Store the position when the mouse is released
        dealerCoords["dx2"], dealerCoords["dy2"] = x, y
        print(f'Pressed at ({dealerCoords["dx1"]}, {dealerCoords["dy1"]}) and released at ({dealerCoords["dx2"]}, {dealerCoords["dy2"]})')
        return False

def handSS():
    global dealerCoords
    global playerCoords

    # These two loops will verify that it is not an empty dictionary
    totalValue = 0
    for index, (coordinate, value) in enumerate(playerCoords.items()):
        totalValue += value
        
        #if coordinate == ""

        if totalValue != 0:
            break
        elif index == len(playerCoords) - 1:
            print("The player's hand was not drawn...")
            print("Please select 'Player Hand Assignment' on the program to draw the region.")
            return
    totalValue = 0
    for index, (coordinate, value) in enumerate(dealerCoords.items()):
        totalValue += value

        if totalValue != 0:
            break
        elif index == len(dealerCoords) - 1:
            print("The dealer's hand was not drawn...")
            print("Please select 'Dealer Hand Assignment' on the program to draw the region.")
            return

    # Clean up old pics
    if (home/"fourthorpe_cache/playerHand.png").exists() or (home/"fourthorpe_cache/deakerHand.png").exists():
        os.unlink(home/"fourthorpe_cache/playerHand.png")
        os.unlink(home/"fourthorpe_cache/dealerHand.png")
    # Screenshot new pics
    try:
        playerHandPNG = ImageGrab.grab(bbox=(playerCoords['px1'],playerCoords['py1'],playerCoords['px2'],playerCoords['py2']), all_screens=True)
        dealerHandPNG = ImageGrab.grab(bbox=(dealerCoords['dx1'],dealerCoords['dy1'],dealerCoords['dx2'],dealerCoords['dy2']), all_screens=True)
        playerHandPNG.save(home/'fourthorpe_cache/playerHand.png')
        dealerHandPNG.save(home/'fourthorpe_cache/dealerHand.png')
    except:
        print('ERROR: The capture was either drawn from the wrong direction or user is not using their primary monitor.\n\nPlease re-draw the hands.')
        return
    return

def coordRead():
    global dealerCoords
    global playerCoords
    print(f'Dealer[ X: {dealerCoords["dx1"]}, Y: {dealerCoords["dy1"]}, X2: {dealerCoords["dx2"]}, Y2: {dealerCoords["dy2"]} ]')
    print(f'Player[ X: {playerCoords["px1"]}, Y: {playerCoords["py1"]}, X2: {playerCoords["px2"]}, Y2: {playerCoords["py2"]} ]')

def quitApp():
    # When they close the program, it will automatically clean up our files.
    if (home/"fourthorpe_cache/playerHand.png").exists() or (home/"fourthorpe_cache/deakerHand.png").exists():
        os.unlink(home/"fourthorpe_cache/playerHand.png")
        os.unlink(home/"fourthorpe_cache/dealerHand.png")
        os.rmdir(home/"fourthorpe_cache")
    root.destroy()

### DRAW GUI
root.title("FourThorpe-Screenshot")
content = tk.Frame(root)
frame = tk.Frame(content, borderwidth=5, relief="ridge", width=384, height=100)
button1=tk.Button(root,text="Player Hand Assignment", command=playerHand)
button2=tk.Button(root,text="Dealer Hand Assignment", command=dealerHand)
button3=tk.Button(root,text="Quit", command=quitApp)
# button4=tk.Button(root,text="Coordinates", command=coordRead)
button5=tk.Button(root,text="New Hand", command=handSS)

content.grid(column=0, row = 0, columnspan=4)
frame.grid(column=0, row=0, columnspan=3, rowspan=2)
button1.grid(column=0, row=3)
button2.grid(column=1, row=3)
button3.grid(column=3, row=3)
#button4.grid(column=4, row=3)
button5.grid(column=2, row=3)

root.mainloop()