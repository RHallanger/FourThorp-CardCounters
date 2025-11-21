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
    -PIL
    -pynput
    -tkinter
    -os
    -pathlib


NOTICE:
Pyautogui struggles with multiple monitors, please use the main monitor for the gameplay and screenshots.
This is a known issue that has not been resolved.

===========================================================
"""

from pynput import mouse
from PIL import ImageGrab
import tkinter as tk
import os
from pathlib import Path

root = tk.Tk()
home = Path.home()
text = tk.Text(root)
(home/"fourthorpe_cache").mkdir(exist_ok=True,parents=True)

### Global variables to keep records of player and dealer screenshot locs
# This will let the user to drag to select the region for both screenshots to be recorded
playerCoords= {"px1":0, "py1":0, "px2":0, "py2":0}
dealerCoords= {"dx1":0, "dy1":0, "dx2":0, "dy2":0}
guiTextList = {'welcome':'Hello, welcome to the FourThorpe - Blackjack Counting Tool...\nPlease click and drag from the top-left of the area of the hand to the bottom-right', 'player':'Please assign the player\'s hand using \'Player Hand Assignment\'.', 'dealer':'Please assign the dealer\'s hand using \'Dealer Hand Assignment', 'screenshot':'You can screenshot the hands using \'New Hand\'.'}
guiTextDisplay = ''
for (key, value) in guiTextList.items():
    guiTextDisplay += value + '\n'
screenCount = 0

### THIS PORTION WILL TAKE SCREEN SHOTS


### THIS PORTION WILL HANDLE USER INPUTS FOR RECORDING REGIONS TO TAKE SCREENSHOTS
# This function will remove a line of text from the GUI instructions
def guiTextDel(removeKey):
    global guiTextList
    global guiTextDisplay
    del guiTextList[removeKey]
    text.config(state='normal')
    text.delete(1.0, tk.END)
    root.update
    guiTextDisplay = ''
    for (key, value) in guiTextList.items():
        guiTextDisplay += value + '\n'
    text.insert(tk.END, guiTextDisplay)
    text.config(state=tk.DISABLED)
    root.update
    return

# This function will add a line of text to the GUI instructions
# More for giving feedback to the user
def guiTextAdd(addKey, addValue):
    global guiTextList, guiTextDisplay, screenCount
    if screenCount > 20:
        guiTextDel((screenCount - 20))
    guiTextList[addKey] = addValue
    text.config(state='normal')
    text.delete(1.0, tk.END)
    root.update
    guiTextDisplay = ''
    for (key, value) in guiTextList.items():
        guiTextDisplay += value + '\n'
    text.insert(tk.END, guiTextDisplay)
    text.config(state=tk.DISABLED)
    root.update
    return

def playerHand():
    global guiTextList
    print("Please click and drag from the top-left of the area of the player's cards to the bottom-right")
    with mouse.Listener(on_click=playerOnClick) as playerListener:
        playerListener.join()
        if "player" in guiTextList:
            guiTextDel('player')
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
    global guiTextList
    print("Please click and drag from the top-left of the area of the dealer's cards to the bottom-right")
    with mouse.Listener(on_click=dealerOnClick) as dealerListener:
        dealerListener.join()
        if 'dealer' in guiTextList:
            guiTextDel('dealer')
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
    global dealerCoords, playerCoords, screenCount
    # Clean up old pics
    if (home/"fourthorpe_cache/playerHand.png").exists():
        os.unlink(home/"fourthorpe_cache/playerHand.png")
    if (home/"fourthorpe_cache/dealerHand.png").exists():
        os.unlink(home/"fourthorpe_cache/dealerHand.png")
    # Screenshot new pics
    try:
        playerHandPNG = ImageGrab.grab(bbox=(playerCoords['px1'],playerCoords['py1'],playerCoords['px2'],playerCoords['py2']), all_screens=True)
        dealerHandPNG = ImageGrab.grab(bbox=(dealerCoords['dx1'],dealerCoords['dy1'],dealerCoords['dx2'],dealerCoords['dy2']), all_screens=True)
        playerHandPNG.save(home/'fourthorpe_cache/playerHand.png')
        dealerHandPNG.save(home/'fourthorpe_cache/dealerHand.png')
        screenCount += 1
        guiTextAdd(screenCount, f'Hand {screenCount} screenshot taken successfully.')
    except:
        guiTextAdd('player', 'Please re-assign the player\'s hand using \'Player Hand Assignment\'.')
        guiTextAdd('dealer', 'Please re-assign the dealer\'s hand using \'Dealer Hand Assignment\'.')
        guiTextAdd('error', 'ERROR: The capture was drawn from the wrong direction.\n\nPlease re-draw the hands.')
        return
    return

def quitApp():
    # When they close the program, it will automatically clean up our files.
    if (home/"fourthorpe_cache/playerHand.png").exists() or (home/"fourthorpe_cache/dealerHand.png").exists():
        os.unlink(home/"fourthorpe_cache/playerHand.png")
        os.unlink(home/"fourthorpe_cache/dealerHand.png")
        os.rmdir(home/"fourthorpe_cache")
    root.destroy()
    quit

### DRAW GUI
root.title("FourThorpe-Screenshot")
content = tk.Frame(root)
frame = tk.Frame(content, borderwidth=5, relief="ridge", width=384, height=100)
button1=tk.Button(root,text="Player Hand Assignment", command=playerHand)
button2=tk.Button(root,text="Dealer Hand Assignment", command=dealerHand)
button3=tk.Button(root,text="Quit", command=quitApp)
button5=tk.Button(root,text="New Hand", command=handSS)

text.grid(column=0, row = 0, columnspan=4)
text.insert(tk.END, guiTextDisplay)
text.config(state=tk.DISABLED)
frame.grid(column=0, row=0, columnspan=3, rowspan=2)
button1.grid(column=0, row=3)
button2.grid(column=1, row=3)
button3.grid(column=3, row=3)
#button4.grid(column=4, row=3)
button5.grid(column=2, row=3)

root.mainloop()