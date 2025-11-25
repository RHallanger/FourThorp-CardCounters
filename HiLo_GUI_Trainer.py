"""
===========================================================
Program Name: HiLo_GUI_Trainer.py
Author: Ryan Vrbeta
Date: 2025-11-22
Description:
    A Button-Driven Blackjack Strategy & Counting Trainer.
    - Quick Select buttons for cards.
    - Toggle between "Count Mode", "Player Hand", and "Dealer Hand".
    - Instant RC/TC updates.
===========================================================
"""
import tkinter as tk
from tkinter import messagebox
import os
from functools import partial

# --- IMPORT LOGIC ---
# Ensure HiLoCounter.py and StrategyGuide.py are in the same folder!
from HiLoCounter import HiLoCounter 
import StrategyGuide 

# --- 1. SETUP & GLOBALS ---
HILO_BRAIN = HiLoCounter(decks=6)
VALID_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# State Variables
current_mode = "COUNT ONLY" # Modes: COUNT ONLY, PLAYER HAND, DEALER UP-CARD
player_hand = []
dealer_hand = []

# Tkinter Window Setup
root = tk.Tk()
root.title("4Thorp Trainer")
root.geometry("320x500") # Narrow width as requested
root.resizable(False, False)

# UI Variables
stats_text = tk.StringVar(value="RC: 0  |  TC: 0.00")
action_text = tk.StringVar(value="--")
mode_text = tk.StringVar(value="MODE: COUNT ONLY")
player_text = tk.StringVar(value="Player: []")
dealer_text = tk.StringVar(value="Dealer: []")


# --- 2. LOGIC FUNCTIONS ---

def update_gui():
    """Refreshes all labels based on current state."""
    # Update Counts
    rc = HILO_BRAIN.running_count
    tc = HILO_BRAIN.true_count()
    stats_text.set(f"RC: {rc}  |  TC: {tc}")
    
    # Update Hands
    p_total = StrategyGuide.calculate_hand_total(player_hand)
    d_total = StrategyGuide.calculate_hand_total(dealer_hand)
    
    player_text.set(f"Player: {player_hand} ({p_total})")
    dealer_text.set(f"Dealer: {dealer_hand} ({d_total})")
    
    # Update Mode Button Text
    mode_text.set(f"MODE: {current_mode}")
    
    # Auto-Run Strategy if hands are ready
    if len(player_hand) >= 2 and len(dealer_hand) >= 1:
        get_strategy()
    else:
        action_text.set("--")
        lbl_action.config(fg="black")

def card_button_clicked(rank):
    """Called when a Card Button (2-A) is pressed."""
    global player_hand, dealer_hand
    
    # 1. Always count the card (Hi-Lo)
    HILO_BRAIN.count_card(rank)
    
    # 2. Add to specific hand if in that mode
    if current_mode == "PLAYER HAND":
        player_hand.append(rank)
    elif current_mode == "DEALER UP-CARD":
        # Dealer only needs 1 up-card for strategy
        dealer_hand = [rank] 
        
    update_gui()

def toggle_mode():
    """Cycles: Count -> Player -> Dealer -> Count"""
    global current_mode
    if current_mode == "COUNT ONLY":
        current_mode = "PLAYER HAND"
        btn_mode.config(bg="#ADD8E6") # Light Blue
    elif current_mode == "PLAYER HAND":
        current_mode = "DEALER UP-CARD"
        btn_mode.config(bg="#FFCCCB") # Light Red
    else:
        current_mode = "COUNT ONLY"
        btn_mode.config(bg="#E0E0E0") # Gray
    update_gui()

def get_strategy():
    """Calculates Hit/Stand based on hands and True Count."""
    try:
        action = StrategyGuide.get_player_action(player_hand, dealer_hand, HILO_BRAIN.true_count())
        action_text.set(action)
        
        # Color Coding
        if "HIT" in action: lbl_action.config(fg="green")
        elif "STAND" in action: lbl_action.config(fg="red")
        elif "DOUBLE" in action: lbl_action.config(fg="blue")
        else: lbl_action.config(fg="black")
    except Exception as e:
        print(f"Strategy Error: {e}")

def reset_hand():
    """Clears hands for next round, KEEPS the count."""
    global player_hand, dealer_hand
    player_hand = []
    dealer_hand = []
    update_gui()

def new_shoe():
    """Resets EVERYTHING (Count goes to 0)."""
    HILO_BRAIN.reset_shoe()
    reset_hand()


# --- 3. GUI LAYOUT ---

# Stats Header
frame_header = tk.Frame(root, pady=10)
frame_header.pack()
tk.Label(frame_header, textvariable=stats_text, font=("Arial", 14, "bold")).pack()
lbl_action = tk.Label(frame_header, textvariable=action_text, font=("Arial", 18, "bold"))
lbl_action.pack()

# Hands Display
frame_hands = tk.Frame(root)
frame_hands.pack()
tk.Label(frame_hands, textvariable=dealer_text, font=("Consolas", 10)).pack()
tk.Label(frame_hands, textvariable=player_text, font=("Consolas", 10)).pack()

# Mode Switcher
tk.Label(root, text=" ").pack() # Spacer
btn_mode = tk.Button(root, textvariable=mode_text, command=toggle_mode, height=2, bg="#E0E0E0")
btn_mode.pack(fill=tk.X, padx=20)

# Card Grid (Buttons)
frame_grid = tk.Frame(root, pady=10)
frame_grid.pack()

r = 0
c = 0
for rank in VALID_RANKS:
    btn = tk.Button(frame_grid, text=rank, width=5, height=2, 
                    command=partial(card_button_clicked, rank))
    btn.grid(row=r, column=c, padx=2, pady=2)
    c += 1
    if c > 3: # 4 columns
        c = 0
        r += 1

# Footer Controls
frame_footer = tk.Frame(root, pady=20)
frame_footer.pack(side=tk.BOTTOM, fill=tk.X)

tk.Button(frame_footer, text="Next Hand", command=reset_hand, bg="#FFD700").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
tk.Button(frame_footer, text="New Shoe", command=new_shoe, bg="#FF4500").pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)

# Start
update_gui()
if __name__ == '__main__':
    root.mainloop()