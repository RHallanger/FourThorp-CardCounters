from operator import truediv
import tkinter as tk
import os
from pathlib import Path
import threading
import time
from functools import partial

# --- YOLO & VISION LIBRARIES ---
import cv2
import numpy as np
import pyautogui
from ultralytics import YOLO
import glob
from pynput import mouse
from PIL import ImageGrab 

# NOTE: HiLoCounter and StrategyGuide MUST be in the same directory!
from HiLoCounter import HiLoCounter 
import StrategyGuide 

# --- 1. GLOBAL VARIABLES & CONFIGURATION ---
CONFIDENCE_THRESHOLD = 0.05
home = Path.home()
(home/"fourthorpe_cache").mkdir(exist_ok=True, parents=True)

# Threading and State
is_running = threading.Event()
vision_thread = None

# Shared Image Data (For thread-safe display)
SHARED_DEALER_IMG = np.zeros((200, 300, 3), dtype=np.uint8)
SHARED_PLAYER_IMG = np.zeros((200, 300, 3), dtype=np.uint8)

# Coordinates (Will be updated by user's mouse drag)
playerCoords = {"px1":0, "py1":0, "px2":0, "py2":0}
dealerCoords = {"dx1":0, "dy1":0, "dx2":0, "dy2":0}
guiTextList = {'welcome':'Hello, please assign the player and dealer hands below.'}

# Initialize Brains (Loaded once at startup)
AI_MODEL = None
HILO_BRAIN = None


# --- 2. CREATE TKINTER OBJECTS (MUST BE DEFINED FIRST) ---
# FIX 1: Creates 'root' and other essential objects so functions can use them.
root = tk.Tk() 
root.title("FourThorpe Blackjack Analyzer")

# StringVars for dynamic label updates
player_hand_display = tk.StringVar(root, value="Player Hand: [] (Total: 0)")
dealer_hand_display = tk.StringVar(root, value="Dealer Hand: [] (Total: 0)")
stats_display = tk.StringVar(root, value="RC: 0 | TC: 0.00 | ACTION: READY")

# Frame and Text Area setup
content = tk.Frame(root) 
text = tk.Text(content, wrap="word", height=10, width=50, borderwidth=2, relief="groove")


# --- 3. TKINTER HELPER FUNCTIONS (The Definitions) ---

def guiTextDel(removeKey):
    """Removes a line of text from the GUI instructions."""
    global guiTextList, text
    if removeKey in guiTextList:
        del guiTextList[removeKey]
        text.config(state='normal')
        text.delete(1.0, tk.END)
        text.insert(tk.END, '\n'.join(guiTextList.values()))
        text.config(state=tk.DISABLED)
        root.update()

def guiTextAdd(addKey, addValue):
    """Adds a line of text to the GUI instructions."""
    global guiTextList, text
    guiTextList[addKey] = addValue
    text.config(state='normal')
    text.delete(1.0, tk.END)
    text.insert(tk.END, '\n'.join(guiTextList.values()))
    text.config(state=tk.DISABLED)
    root.update()

def update_gui(player_hand, p_total, dealer_hand, d_total, action, rc, tc, new_card_detected):
    """Safely updates the Tkinter GUI labels from the background thread."""
    global player_hand_display, dealer_hand_display, stats_display
    
    player_hand_display.set(f"Player Hand: {', '.join(player_hand)} (Total: {p_total})")
    dealer_hand_display.set(f"Dealer Hand: {', '.join(dealer_hand)} (Total: {d_total})")
    stats_display.set(f"RC: {rc} | TC: {tc} | ACTION: {action}")
    
    if new_card_detected:
         guiTextAdd('count', f'Counted {len(player_hand) + len(dealer_hand)} cards.') 
         
    root.update_idletasks()

def playerOnClick(x, y, button, pressed):
    """Records player zone coordinates."""
    global playerCoords
    if pressed:
        playerCoords["px1"], playerCoords["py1"] = x, y
    else:
        playerCoords["px2"], playerCoords["py2"] = x, y
        return False

def dealerOnClick(x, y, button, pressed):
    """Records dealer zone coordinates."""
    global dealerCoords
    if pressed:
        dealerCoords["dx1"], dealerCoords["dy1"] = x, y
    else:
        dealerCoords["dx2"], dealerCoords["dy2"] = x, y
        return False

def quitApp():
    """Safely stops the thread and closes the GUI."""
    stop_vision()
    root.destroy()
    os._exit(0)

def stop_vision():
    """Safely stops the vision loop thread."""
    global vision_thread
    if is_running.is_set():
        is_running.clear()
        if vision_thread and vision_thread.is_alive():
            vision_thread.join(timeout=1)
        guiTextAdd('status', 'Analyzer STOPPED.')
        root.after(0, cv2.destroyAllWindows) 

# --- 4. CORE LOGIC HELPER FUNCTIONS ---

def get_card_ranks(results_list, model):
    """Parses YOLO class ID into Rank Name ('A', '2'...)."""
    ranks = []
    RANK_MAP = {0: '10', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7',
                7: '8', 8: '9', 9: 'A', 10: 'J', 11: 'K', 12: 'Q'}
    if results_list and len(results_list) > 0:
        r = results_list[0] 
        for box in r.boxes:
            if box.conf.cpu().numpy()[0] > CONFIDENCE_THRESHOLD: 
                cls_index = int(box.cls.cpu().numpy()[0])
                name = model.names.get(cls_index, RANK_MAP.get(cls_index, 'Unknown'))
                ranks.append(name)
    return ranks

def calculate_hand_total(cards):
    """Calculates the Blackjack value of a list of cards, handling Aces (1 or 11)."""
    total = 0; ace_count = 0
    card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                   '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11, 'jack': 10, 'queen': 10, 'king': 10, 'ace': 11}
    for card in cards:
        clean_card = str(card).upper().strip()
        if clean_card in card_values: 
            total += card_values[clean_card]
            if clean_card == 'A' or clean_card == 'ACE': ace_count += 1
    while total > 21 and ace_count > 0:
        total -= 10; ace_count -= 1
    return total

# --- 5. BUTTON COMMAND FUNCTIONS (FIX 2: Assignment functions must be defined before use) ---

def playerHandAssignment():
    """Starts mouse listener for player zone selection."""
    guiTextAdd('screenshot', 'Please click and drag from the top-left of the player\'s cards to the bottom-right')
    ImageGrab.grab(all_screens=True).save(home/'fourthorpe_cache/temp_ss.png') 
    with mouse.Listener(on_click=playerOnClick) as playerListener:
        playerListener.join()
        guiTextDel('player')
        guiTextAdd('player_loc', f'Player Zone Set: X:{playerCoords["px1"]} Y:{playerCoords["py1"]} to X2:{playerCoords["px2"]} Y2:{playerCoords["py2"]}')


def dealerHandAssignment():
    """Starts mouse listener for dealer zone selection."""
    guiTextAdd('screenshot', 'Please click and drag from the top-left of the dealer\'s cards to the bottom-right')
    ImageGrab.grab(all_screens=True).save(home/'fourthorpe_cache/temp_ss.png')
    with mouse.Listener(on_click=dealerOnClick) as dealerListener:
        dealerListener.join()
        guiTextDel('dealer')
        guiTextAdd('dealer_loc', f'Dealer Zone Set: X:{dealerCoords["dx1"]} Y:{dealerCoords["dy1"]} to X2:{dealerCoords["dx2"]} Y2:{dealerCoords["dy2"]}')

def display_windows(root):
    """Safely displays OpenCV windows and controls the loop in the main thread."""
    global SHARED_DEALER_IMG, SHARED_PLAYER_IMG
    
    if is_running.is_set():
        cv2.imshow("Dealer View", SHARED_DEALER_IMG)
        cv2.imshow("Player View", SHARED_PLAYER_IMG)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
             stop_vision()
             root.destroy()
             os._exit(0)
             
        root.after(100, display_windows, root) # Loop the display check


def start_vision():
    """Launches the vision loop thread and starts the display loop."""
    global vision_thread, AI_MODEL, HILO_BRAIN
    if not is_running.is_set() and playerCoords['px2'] != 0 and dealerCoords['dx2'] != 0:
        
        if AI_MODEL is None:
            # --- NEW LOAD LOGIC IN start_vision() ---
            # 1. Load the AI Model Directly
            # ⚠️ YOU MUST UPDATE THE FOLDER NAME HERE ⚠️
            FINAL_MODEL_PATH = r'C:\Users\shrek\source\repos\RHallanger\FourThorp-CardCounters\runs\detect\final_fine_tuned_model5\weights\best.pt' 
            
            try:
                AI_MODEL = YOLO(FINAL_MODEL_PATH)
                HILO_BRAIN = HiLoCounter(decks=6)
            except Exception as e:
                guiTextAdd('error_ai', f'CRITICAL ERROR: AI model not found at path: {FINAL_MODEL_PATH}. ({e})')
                return

        guiTextDel('status')
        guiTextAdd('status', 'ANALYZER ACTIVE: Counting cards now.')
        is_running.set()
        vision_thread = threading.Thread(target=vision_loop, args=(AI_MODEL, HILO_BRAIN, root))
        vision_thread.start()
        
        root.after(100, display_windows, root) # Start the display loop in the main thread
        
    elif playerCoords['px2'] == 0:
         guiTextAdd('error', 'ERROR: Please assign Player and Dealer Hand zones first.')


# --- 6. VISION ANALYZER LOGIC (Background Thread) ---
def vision_loop(model, brain, root):
    """Continuous analysis loop. Runs YOLO and updates shared global variables."""
    global playerCoords, dealerCoords, SHARED_DEALER_IMG, SHARED_PLAYER_IMG
    cards_counted_this_hand = [] 

    # 1. Calculate Zones from the Tkinter inputs
    p_x1, p_y1, p_x2, p_y2 = playerCoords['px1'], playerCoords['py1'], playerCoords['px2'], playerCoords['py2']
    d_x1, d_y1, d_x2, d_y2 = dealerCoords['dx1'], dealerCoords['dy1'], dealerCoords['dx2'], dealerCoords['dy2']

    p_x, p_y = min(p_x1, p_x2), min(p_y1, p_y2)
    p_w, p_h = abs(p_x2 - p_x1), abs(p_y2 - p_y1)
    d_x, d_y = min(d_x1, d_x2), min(d_y1, d_y2)
    d_w, d_h = abs(d_x2 - d_x1), abs(d_y2 - d_y1)
    
    if p_w <= 5 or p_h <= 5 or d_w <= 5 or d_h <= 5:
        guiTextAdd('error', 'ERROR: Capture zones are too small. Please re-assign.')
        is_running.clear()
        return

    # 2. Main continuous loop
    while is_running.is_set():
        # --- A. Capture & Crop ---
        dealer_img_raw = np.array(pyautogui.screenshot(region=(d_x, d_y, d_w, d_h)))
        player_img_raw = np.array(pyautogui.screenshot(region=(p_x, p_y, p_w, p_h)))
        dealer_img_bgr = cv2.cvtColor(dealer_img_raw, cv2.COLOR_RGB2BGR)
        player_img_bgr = cv2.cvtColor(player_img_raw, cv2.COLOR_RGB2BGR)

        # --- B. Run AI Detection ---
        dealer_results = model.predict(dealer_img_bgr, conf=CONFIDENCE_THRESHOLD, verbose=True)
        player_results = model.predict(player_img_bgr, conf=CONFIDENCE_THRESHOLD, verbose=True)
        
        # --- C. Parse and Count ---
        dealer_hand = get_card_ranks(dealer_results, model)
        player_hand = get_card_ranks(player_results, model)
        
        all_cards = dealer_hand + player_hand
        new_card_detected = False
        
        for card in all_cards:
            if card not in cards_counted_this_hand:
                brain.count_card(card)
                cards_counted_this_hand.append(card)
                new_card_detected = True

        # --- D. Strategy and Visualization Data ---
        p_total = calculate_hand_total(player_hand)
        d_total = calculate_hand_total(dealer_hand)
        action = StrategyGuide.get_player_action(player_hand, dealer_hand, brain.true_count())
        rc = brain.running_count
        tc = brain.true_count()

        # Update shared memory for display in the main thread
        SHARED_DEALER_IMG = dealer_results[0].plot()
        SHARED_PLAYER_IMG = player_results[0].plot()

        # Safely update the Tkinter GUI labels from the main thread
        root.after(0, update_gui, player_hand, p_total, dealer_hand, d_total, action, rc, tc, new_card_detected)
        
        time.sleep(0.05) 


# --- 7. DRAW TKINTER GUI (FINAL SECTION) ---

content.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

# Text Area for instructions
text.grid(column=0, row=0, columnspan=2, padx=5, pady=5)
text.insert(tk.END, guiTextList['welcome'])
text.config(state=tk.DISABLED)

# Hand Display Labels
tk.Label(content, textvariable=stats_display, font=("Arial", 14)).grid(column=2, row=0, sticky=tk.W, padx=10, pady=(5, 0))
tk.Label(content, textvariable=dealer_hand_display, font=("Arial", 12)).grid(column=2, row=1, sticky=tk.W, padx=10)
tk.Label(content, textvariable=player_hand_display, font=("Arial", 12)).grid(column=2, row=2, sticky=tk.W, padx=10)

# Buttons (Calling the functions defined in Section 5)
tk.Button(content, text="Assign Player Hand", command=playerHandAssignment).grid(column=0, row=3, padx=5, pady=5)
tk.Button(content, text="Assign Dealer Hand", command=dealerHandAssignment).grid(column=1, row=3, padx=5, pady=5)
tk.Button(content, text="START ANALYZER", command=start_vision, bg='green').grid(column=2, row=3, padx=5, pady=5)
tk.Button(content, text="STOP ANALYZER", command=stop_vision, bg='red').grid(column=3, row=3, padx=5, pady=5)
tk.Button(content, text="QUIT", command=quitApp).grid(column=4, row=3, padx=5, pady=5)

# Start the GUI
if __name__ == '__main__':
    root.mainloop()