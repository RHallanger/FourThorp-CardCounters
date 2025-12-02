import pyautogui

print("Taking a screenshot in 3 seconds...")
print("Switch to your game window NOW!")

# Gives you 3 seconds to make sure the game is visible
import time
time.sleep(3)

# 1. Take the screenshot using Python's eyes
screenshot = pyautogui.screenshot()

# 2. Save it exactly as Python sees it
screenshot.save("raw_python_view.png")

print("Saved 'raw_python_view.png'. Open this file in Paint to look for the coordinates!")