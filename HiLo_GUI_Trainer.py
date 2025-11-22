"""
===========================================================
Program Name: HiLo_GUI_Trainer.py
Author: Ryan Vrbeta
Date: 2025-11-22
Description:
    This program brings up a tkinter UI that asks for end-user input. The goal of this program is
    to count cards by entering numbers in a shoe and by using the interface you can also enter in the dealer's UP card
    and your own hand to have the program determine whether you should hit or stay.
    
Usage:
    Run the script using Python 3.x. Ensure all dependencies
    are installed before execution.

===========================================================
"""
import tkinter as tk
from tkinter import messagebox # For user error messages
from tkinter import simpledialog
import os
from pathlib import Path
from functools import partial

# --- IMPORT ESSENTIAL LOGIC ---
# These two files must be present in the same directory!
from HiLoCounter import HiLoCounter 
import StrategyGuide 

# --- 1. GLOBAL VARIABLES & CONFIGURATION ---

# Initialize Brains (Loaded once at startup)
HILO_BRAIN = HiLoCounter(decks=6) # Create the HiLoCounter object immediately
VALID_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

# Tkinter Setup
root = tk.Tk() 
root.title("FourThorpe Blackjack Trainer")

# StringVars for dynamic label updates
player_hand_display = tk.StringVar(root, value="Player Hand: [] (Total: 0)")
dealer_hand_display = tk.StringVar(root, value="Dealer Hand: [] (Total: 0)")
stats_display = tk.StringVar(root, value="RC: 0 | TC: 0.00 | ACTION: READY")
info_text_display = tk.StringVar(root, value="Enter a card rank (2-10, J, Q, K, A) and click 'Count Card'.")

# Frame and Text Area setup
content = tk.Frame(root) 
card_input_entry = tk.Entry(content, width=10) # The new non-CLI input box


# --- 2. CORE LOGIC FUNCTIONS ---

def normalize_input(card_str):
    """Converts various user inputs (1, 11, ace) into standard rank strings ('A', 'J')."""
    card = card_str.strip().upper()
    try:
        num = int(card)
        if num == 1: return 'A'
        if 2 <= num <= 10: return str(num)
        if num == 11: return 'J'
        if num == 12: return 'Q'
        if num == 13: return 'K'
    except ValueError:
        pass
    
    if card in VALID_RANKS:
        return card

    return None


def update_display(action, current_hand=None, d_card=None):
    """Updates all Tkinter labels after a count or decision is made."""
    
    rc = HILO_BRAIN.running_count
    tc = HILO_BRAIN.true_count()
    
    stats_display.set(f"RC: {rc} | TC: {tc} | ACTION: {action}")
    
    if current_hand is not None:
        p_total = StrategyGuide.calculate_hand_total(current_hand)
        d_total = StrategyGuide.calculate_hand_total(d_card) if d_card else 0
        
        player_hand_display.set(f"Player Hand: {', '.join(current_hand)} (Total: {p_total})")
        dealer_hand_display.set(f"Dealer Hand: {', '.join(d_card)} (Total: {d_total})")
    
    # Clears the input box after action
    card_input_entry.delete(0, tk.END)


# --- 3. COMMAND FUNCTIONS (Button Logic) ---

def handle_card_count():
    """Reads input from the entry box and sends it to the HiLo counter."""
    card_input = card_input_entry.get()
    card_rank = normalize_input(card_input)
    
    if card_rank and card_rank in VALID_RANKS:
        HILO_BRAIN.count_card(card_rank)
        info_text_display.set(f"Counted: {card_rank}. RC is now {HILO_BRAIN.running_count}")
        update_display("COUNTING...")
    else:
        messagebox.showerror("Invalid Card", f"'{card_input}' is not a valid rank. Use A, 2-10, J, Q, K.")
        
    card_input_entry.delete(0, tk.END)

# --- IN HiLo_GUI_Trainer.py ---

def handle_decision():
    """Gets player/dealer hands and provides the strategy recommendation using pop-ups."""
    
    # 1. Get Dealer Up-Card via Tkinter Pop-up
    dealer_input = tk.simpledialog.askstring("Dealer's Up Card", "Enter the Dealer's UP card (e.g., 7 or A):")
    
    # FIX: Check for the 'Cancel' button (which returns None)
    if dealer_input is None:
        return

    dealer_rank = normalize_input(dealer_input)
    
    if not dealer_rank:
        messagebox.showerror("Error", "Dealer card not valid. Please try again.")
        return

    # 2. Get Player Hand via Tkinter Pop-up
    player_hand_input = tk.simpledialog.askstring("Player Hand", "Enter your hand, separated by commas (e.g., K, 5, A):")
    
    # FIX: Check for the 'Cancel' button on the player hand pop-up
    if player_hand_input is None:
        return

    player_hand_ranks = [normalize_input(c) for c in player_hand_input.split(',') if normalize_input(c) in VALID_RANKS]

    if not player_hand_ranks:
        messagebox.showerror("Error", "Could not parse hand. Please use correct rank names.")
        return

    # 3. Get Strategy Decision
    try:
        # Pass the current True Count and the player/dealer hands to the Strategy Guide
        action = StrategyGuide.get_player_action(player_hand_ranks, [dealer_rank], HILO_BRAIN.true_count())
        player_total = StrategyGuide.calculate_hand_total(player_hand_ranks)
        
        # Update displays
        update_display(action, player_hand_ranks, [dealer_rank])
        info_text_display.set(f"Decision for {player_hand_ranks} vs {dealer_rank}: {action}")

    except Exception as e:
        messagebox.showerror("CRITICAL ERROR", f"Failed to get strategy. Check StrategyGuide.py. Error: {e}")



    # 3. Get Strategy Decision
    action = StrategyGuide.get_player_action(player_hand_ranks, [dealer_rank], HILO_BRAIN.true_count())
    
    # Update displays
    update_display(action, player_hand_ranks, [dealer_rank])
    info_text_display.set(f"Decision for {player_hand_ranks} vs {dealer_rank}: {action}")
    card_input_entry.delete(0, tk.END)


def reset_shoe_cmd():
    """Resets the entire shoe."""
    HILO_BRAIN.reset_shoe()
    update_display("NEW SHOE", current_hand=[], d_card=[])
    info_text_display.set("👟 SHOE RESET. RC/TC is zero.")
    player_hand_display.set("Player Hand: [] (Total: 0)")
    dealer_hand_display.set("Dealer Hand: [] (Total: 0)")


# --- 4. DRAW TKINTER GUI ---

root.geometry("600x300")
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

content.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
content.grid_columnconfigure(0, weight=1)
content.grid_columnconfigure(1, weight=1)
content.grid_columnconfigure(2, weight=1)

# Hand Display Labels (Top Right)
tk.Label(content, textvariable=stats_display, font=("Arial", 16, "bold"), fg='#B3C6E7').grid(column=2, row=0, sticky=tk.W, padx=10, pady=(15, 0))
tk.Label(content, textvariable=player_hand_display, font=("Arial", 12)).grid(column=2, row=1, sticky=tk.W, padx=10)
tk.Label(content, textvariable=dealer_hand_display, font=("Arial", 12)).grid(column=2, row=2, sticky=tk.W, padx=10)

# Input Section (Center Left)
tk.Label(content, text="Card Input / Decision Card:", font=("Arial", 10)).grid(column=0, row=0, sticky=tk.W, padx=10, pady=(15, 5))
card_input_entry.grid(column=0, row=1, sticky=(tk.W, tk.E), padx=10, pady=5)
tk.Label(content, textvariable=info_text_display, font=("Arial", 10), fg='gray').grid(column=0, row=2, columnspan=2, sticky=tk.W, padx=10)


# Control Buttons (Bottom Left/Center)
tk.Button(content, text="COUNT CARD (RC)", command=handle_card_count, bg='#66CC66').grid(column=0, row=3, padx=10, pady=10, sticky=(tk.W, tk.E))
tk.Button(content, text="GET STRATEGY", command=handle_decision, bg='#B3C6E7').grid(column=1, row=3, padx=10, pady=10, sticky=(tk.W, tk.E))
tk.Button(content, text="RESET SHOE", command=reset_shoe_cmd, bg='#CC6600').grid(column=0, row=4, padx=10, pady=10, sticky=(tk.W, tk.E))
tk.Button(content, text="QUIT", command=root.destroy, bg='#8B0000').grid(column=1, row=4, padx=10, pady=10, sticky=(tk.W, tk.E))


# Start the GUI
if __name__ == '__main__':
    root.mainloop()