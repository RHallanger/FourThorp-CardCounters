"""
===========================================================
Program Name: HiLo_GUI_Trainer.py
Author: Ryan Vrbeta
Date: 2025-11-26
Description:
    A Button-Driven Blackjack Strategy & Counting Trainer.
    
    Architecture:
    - GUI Framework: Tkinter (Python's standard GUI library).
    - Design Pattern: Event-Driven State Machine.
    - Logic Separation: Imports math from 'HiLoCounter' and rules from 'StrategyGuide'.
===========================================================
"""
import tkinter as tk
from tkinter import messagebox, Toplevel
import os
from functools import partial # Used to pass arguments to button commands

# --- IMPORT LOGIC MODULES ---
# We import these classes to keep the math separate from the GUI code.
from HiLoCounter import HiLoCounter 
import StrategyGuide 

# --- 1. SETUP & GLOBALS ---

# Initialize the Logic Brain (Persistent State)
# This object stays alive for the whole session to track the Running Count.
HILO_BRAIN = HiLoCounter(decks=6) 

VALID_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# --- APPLICATION STATE VARIABLES ---
# These variables track "Where we are" in the game flow.
current_mode = "COUNT ONLY" # The active input mode (State Machine)
is_removing = False         # Boolean flag for Error Correction mode
player_hand = []            # List to store Player's current cards
dealer_hand = []            # List to store Dealer's current cards

# Dictionary to track frequency stats (e.g. How many Kings have we seen?)
seen_card_counts = {rank: 0 for rank in VALID_RANKS}

# Tkinter Window Setup
root = tk.Tk()
root.title("4Thorp Trainer")
root.geometry("360x680") 
root.resizable(False, False)

# UI Variables (Reactive Data Binding)
# Changing these variables automatically updates the text on the screen.
stats_text = tk.StringVar(value="RC: 0  |  TC: 0.00")
action_text = tk.StringVar(value="--")
mode_text = tk.StringVar(value="MODE: COUNT ONLY")
remove_text = tk.StringVar(value="ADDING (+)")
player_text = tk.StringVar(value="Player: []")
dealer_text = tk.StringVar(value="Dealer: []")
deck_count_var = tk.IntVar(value=6) # Default deck count for new shoes


# --- 2. LOGIC FUNCTIONS ---

def update_gui():
    """
    Refreshes all dynamic labels to match the current program state.
    Acts as the 'View Updater', pulling data from the Logic layer.
    """
    # 1. Fetch Math from the Brain
    rc = HILO_BRAIN.running_count
    tc = HILO_BRAIN.true_count()
    stats_text.set(f"RC: {rc}  |  TC: {tc}")
    
    # 2. Calculate Hand Totals using the Strategy Engine
    p_total = StrategyGuide.calculate_hand_total(player_hand)
    d_total = StrategyGuide.calculate_hand_total(dealer_hand)
    
    # Update the StringVars (which automatically updates the GUI labels)
    player_text.set(f"Player: {player_hand} ({p_total})")
    dealer_text.set(f"Dealer: {dealer_hand} ({d_total})")
    
    # 3. Auto-Run Strategy
    # If we have enough data (2 player cards + 1 dealer card), run strategy immediately.
    if len(player_hand) >= 2 and len(dealer_hand) >= 1:
        get_strategy()
    else:
        action_text.set("--")
        lbl_action.config(fg="black")

def process_card_logic(rank, removing=False):
    """
    Handles the math for adding OR removing a card.
    Encapsulates the Hi-Lo logic to support error correction.
    """
    global seen_card_counts
    
    if removing:
        # ERROR CORRECTION LOGIC:
        # If the user made a mistake, we reverse the math.
        if seen_card_counts[rank] > 0:
            seen_card_counts[rank] -= 1
            
            # Inverse Hi-Lo values to 'undo' the count
            if rank in ['2','3','4','5','6']: HILO_BRAIN.running_count -= 1
            elif rank in ['10','J','Q','K','A']: HILO_BRAIN.running_count += 1
            
            # Decrement total cards seen
            HILO_BRAIN.cards_seen -= 1
    else:
        # STANDARD LOGIC: Add to stats and update brain
        seen_card_counts[rank] += 1
        HILO_BRAIN.count_card(rank) 

def card_button_clicked(rank):
    """
    The central event handler for the card grid.
    Routes the card to the correct list based on 'current_mode'.
    """
    global player_hand, dealer_hand
    
    # 1. Update the Math (Add or Remove based on toggle)
    process_card_logic(rank, removing=is_removing)
    
    # 2. Update the Hand Lists (Only if we are ADDING cards)
    # We do not modify hands if we are in 'Correction' mode
    if not is_removing:
        if current_mode == "PLAYER HAND":
            player_hand.append(rank) # Append allows multiple cards (Hit/Split)
        elif current_mode == "DEALER UP-CARD":
            if len(dealer_hand) == 0:
                 dealer_hand.append(rank)
            else:
                 dealer_hand[0] = rank # Overwrite ensures only 1 dealer up-card
        
    update_gui()

def get_strategy():
    """
    Retrieves the optimal move from the StrategyGuide based on 
    Player Hand, Dealer Card, and the current True Count.
    """
    try:
        action = StrategyGuide.get_player_action(player_hand, dealer_hand, HILO_BRAIN.true_count())
        action_text.set(action)
        
        # Visual Feedback: Color code the action for faster reading
        if "HIT" in action: lbl_action.config(fg="green")
        elif "STAND" in action: lbl_action.config(fg="red")
        elif "DOUBLE" in action: lbl_action.config(fg="blue")
        else: lbl_action.config(fg="black")
    except Exception as e:
        print(f"Strategy Error: {e}")


# --- 3. COMMAND FUNCTIONS (User Interactions) ---

def set_mode(new_mode):
    """
    Directly sets the input mode from the 3-button panel.
    Updates button visuals (Sunken/Raised) to show active state.
    """
    global current_mode
    current_mode = new_mode
    mode_text.set(f"MODE: {current_mode}")
    
    # Visual Toggle Logic: Only the active button looks 'pressed' (Sunken)
    # This gives the user immediate feedback on which state is active.
    btn_count.config(relief=tk.SUNKEN if new_mode == "COUNT ONLY" else tk.RAISED, 
                     bg="#ADD8E6" if new_mode == "COUNT ONLY" else "#E0E0E0")
    btn_player.config(relief=tk.SUNKEN if new_mode == "PLAYER HAND" else tk.RAISED, 
                      bg="#ADD8E6" if new_mode == "PLAYER HAND" else "#E0E0E0")
    btn_dealer.config(relief=tk.SUNKEN if new_mode == "DEALER UP-CARD" else tk.RAISED, 
                      bg="#ADD8E6" if new_mode == "DEALER UP-CARD" else "#E0E0E0")

def toggle_remove():
    """Switches the entire interface between ADDING mode and CORRECTION mode."""
    global is_removing
    is_removing = not is_removing
    
    if is_removing:
        remove_text.set("REMOVING (-)")
        btn_remove.config(bg="#FF9999", relief=tk.SUNKEN) # Red for Warning
    else:
        remove_text.set("ADDING (+)")
        btn_remove.config(bg="#90EE90", relief=tk.RAISED) # Green for Go

def show_stats():
    """Opens a secondary popup window to show detailed frequency stats."""
    stats_win = Toplevel(root)
    stats_win.title("Seen Cards")
    stats_win.geometry("250x400")
    
    tk.Label(stats_win, text="Cards Seen in Shoe", font=("Arial", 12, "bold")).pack(pady=10)
    stat_frame = tk.Frame(stats_win)
    stat_frame.pack()
    
    r = 0
    for rank in VALID_RANKS:
        count = seen_card_counts[rank]
        tk.Label(stat_frame, text=f"Rank {rank}:   {count}", font=("Consolas", 10)).grid(row=r, column=0, sticky="w", padx=20)
        r += 1
    tk.Button(stats_win, text="Close", command=stats_win.destroy).pack(pady=20)

def reset_hand():
    """Clears player/dealer hands for the next round, but PRESERVES the count."""
    global player_hand, dealer_hand
    player_hand = []
    dealer_hand = []
    update_gui()

def new_shoe():
    """Resets the Brain, Stats, and Hands for a fresh game."""
    global HILO_BRAIN, seen_card_counts
    
    # Get Deck Count from Dropdown
    d_count = deck_count_var.get()
        
    # Re-Initialize Brain with new settings
    HILO_BRAIN = HiLoCounter(decks=d_count)
    seen_card_counts = {rank: 0 for rank in VALID_RANKS}
    
    reset_hand()
    messagebox.showinfo("New Shoe", f"Started new shoe with {d_count} decks.")


# --- 4. GUI LAYOUT (GRID SYSTEM) ---

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

# Mode Selection Buttons
frame_modes = tk.Frame(root, pady=10)
frame_modes.pack()
tk.Label(frame_modes, text="Select Input Mode:", font=("Arial", 8)).pack()

# We use 'partial' here to pass arguments to the set_mode function
btn_count = tk.Button(frame_modes, text="Count Only", command=partial(set_mode, "COUNT ONLY"), width=12)
btn_count.pack(side=tk.LEFT, padx=2)
btn_player = tk.Button(frame_modes, text="Player Hand", command=partial(set_mode, "PLAYER HAND"), width=12)
btn_player.pack(side=tk.LEFT, padx=2)
btn_dealer = tk.Button(frame_modes, text="Dealer Card", command=partial(set_mode, "DEALER UP-CARD"), width=12)
btn_dealer.pack(side=tk.LEFT, padx=2)

# Utility Buttons (Add/Remove + Stats)
frame_utils = tk.Frame(root, pady=5)
frame_utils.pack()
btn_remove = tk.Button(frame_utils, textvariable=remove_text, command=toggle_remove, width=15, bg="#90EE90")
btn_remove.pack(side=tk.LEFT, padx=5)
tk.Button(frame_utils, text="View Stats", command=show_stats, width=15).pack(side=tk.LEFT, padx=5)

# Card Grid (Dynamic Generation)
frame_grid = tk.Frame(root, pady=10)
frame_grid.pack()
r = 0; c = 0
for rank in VALID_RANKS:
    # Dynamically create buttons for every rank in the list
    # 'partial' freezes the 'rank' argument into the button's command function
    btn = tk.Button(frame_grid, text=rank, width=5, height=2, command=partial(card_button_clicked, rank))
    btn.grid(row=r, column=c, padx=2, pady=2)
    c += 1
    if c > 3: # Wrap grid after 4 columns
        c = 0; r += 1

# Footer Controls
frame_footer = tk.Frame(root, pady=20)
frame_footer.pack(side=tk.BOTTOM, fill=tk.X)

# Next Hand
tk.Button(frame_footer, text="Next Hand", command=reset_hand, bg="#FFD700").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

# New Shoe + Deck Selection
frame_deck = tk.Frame(frame_footer)
frame_deck.pack(side=tk.RIGHT, padx=5)
tk.Label(frame_deck, text="Decks:").pack(side=tk.LEFT)

# Dropdown for Deck Count (Prevents invalid input)
deck_options = [1, 2, 4, 6, 8]
deck_dropdown = tk.OptionMenu(frame_deck, deck_count_var, *deck_options)
deck_dropdown.config(width=2)
deck_dropdown.pack(side=tk.LEFT, padx=2)

tk.Button(frame_deck, text="New Shoe", command=new_shoe, bg="#FF4500", fg="white").pack(side=tk.LEFT, padx=2)

# Initialize Default State
set_mode("COUNT ONLY")
update_gui()

if __name__ == '__main__':
    root.mainloop()