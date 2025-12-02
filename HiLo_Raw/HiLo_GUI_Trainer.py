"""
===========================================================
Program Name: HiLo_GUI_Trainer.py
Author: Ryan Vrbeta
Date: 2025-11-26
Description:
    A professional Blackjack Strategy & Counting Trainer using a 
    Button-Driven GUI. Features mode switching, error correction, 
    deck management, and live strategy feedback.
===========================================================
"""
import tkinter as tk
from tkinter import messagebox, Toplevel
from functools import partial

# --- LOGIC IMPORTS ---
from HiLoCounter import HiLoCounter 
import StrategyGuide 

# --- CONFIGURATION ---
VALID_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
DECK_OPTIONS = [1, 2, 4, 6, 8]

# --- STATE MANAGEMENT ---
HILO_BRAIN = HiLoCounter(decks=6)
current_mode = "COUNT ONLY" 
is_removing = False 
player_hand = []
dealer_hand = []
seen_card_counts = {rank: 0 for rank in VALID_RANKS}

# --- GUI SETUP ---
root = tk.Tk()
root.title("4Thorp Trainer")
root.geometry("360x680")
root.resizable(False, False)

# Reactive Variables
stats_text = tk.StringVar(value="RC: 0  |  TC: 0.00")
action_text = tk.StringVar(value="--")
mode_text = tk.StringVar(value="MODE: COUNT ONLY")
remove_text = tk.StringVar(value="ADDING (+)")
player_text = tk.StringVar(value="Player: []")
dealer_text = tk.StringVar(value="Dealer: []")
deck_count_var = tk.IntVar(value=6)


# --- CORE LOGIC FUNCTIONS ---

def update_gui():
    """Updates all UI labels to reflect current math and state."""
    # 1. Math
    rc = HILO_BRAIN.running_count
    tc = HILO_BRAIN.true_count()
    stats_text.set(f"RC: {rc}  |  TC: {tc}")
    
    p_total = StrategyGuide.calculate_hand_total(player_hand)
    d_total = StrategyGuide.calculate_hand_total(dealer_hand)
    
    # 2. Hands
    player_text.set(f"Player: {player_hand} ({p_total})")
    dealer_text.set(f"Dealer: {dealer_hand} ({d_total})")
    
    # 3. Strategy
    if len(player_hand) >= 2 and len(dealer_hand) >= 1:
        run_strategy()
    else:
        action_text.set("--")
        lbl_action.config(fg="black")

def process_card_math(rank, removing=False):
    """Handles the Hi-Lo counting math (Add vs Remove)."""
    global seen_card_counts
    if removing:
        if seen_card_counts[rank] > 0:
            seen_card_counts[rank] -= 1
            val = -1 if rank in ['2','3','4','5','6'] else 1 if rank in ['10','J','Q','K','A'] else 0
            HILO_BRAIN.running_count += val # Reverse the count
            HILO_BRAIN.cards_seen -= 1
    else:
        seen_card_counts[rank] += 1
        HILO_BRAIN.count_card(rank)

def card_button_clicked(rank):
    """Main handler for card input."""
    global player_hand, dealer_hand
    
    # 1. Update Count Logic
    process_card_math(rank, removing=is_removing)
    
    # 2. Update Hand Lists (Only if Adding)
    if not is_removing:
        if current_mode == "PLAYER HAND":
            player_hand.append(rank)
        elif current_mode == "DEALER UP-CARD":
            dealer_hand = [rank] # Dealer has only 1 up-card
            
    update_gui()

def run_strategy():
    """Calculates and displays the optimal move."""
    try:
        action = StrategyGuide.get_player_action(player_hand, dealer_hand, HILO_BRAIN.true_count())
        action_text.set(action)
        
        colors = {"HIT": "green", "STAND": "red", "DOUBLE": "blue"}
        color = next((v for k, v in colors.items() if k in action), "black")
        lbl_action.config(fg=color)
    except Exception as e:
        print(f"Strategy Error: {e}")


# --- CONTROL FUNCTIONS ---

def set_mode(new_mode):
    """Switches input mode and updates button styling."""
    global current_mode
    current_mode = new_mode
    mode_text.set(f"MODE: {current_mode}")
    
    # Visual Toggle Logic
    btn_count.config(relief=tk.SUNKEN if new_mode == "COUNT ONLY" else tk.RAISED, 
                     bg="#ADD8E6" if new_mode == "COUNT ONLY" else "#E0E0E0")
    btn_player.config(relief=tk.SUNKEN if new_mode == "PLAYER HAND" else tk.RAISED, 
                      bg="#ADD8E6" if new_mode == "PLAYER HAND" else "#E0E0E0")
    btn_dealer.config(relief=tk.SUNKEN if new_mode == "DEALER UP-CARD" else tk.RAISED, 
                      bg="#ADD8E6" if new_mode == "DEALER UP-CARD" else "#E0E0E0")

def toggle_remove():
    """Toggles Error Correction Mode."""
    global is_removing
    is_removing = not is_removing
    if is_removing:
        remove_text.set("REMOVING (-)")
        btn_remove.config(bg="#FF9999", relief=tk.SUNKEN)
    else:
        remove_text.set("ADDING (+)")
        btn_remove.config(bg="#90EE90", relief=tk.RAISED)

def reset_hand():
    """Clears hands but keeps the count."""
    global player_hand, dealer_hand
    player_hand = []
    dealer_hand = []
    update_gui()

def new_shoe():
    """Resets entire game state."""
    global HILO_BRAIN, seen_card_counts
    HILO_BRAIN = HiLoCounter(decks=deck_count_var.get())
    seen_card_counts = {rank: 0 for rank in VALID_RANKS}
    reset_hand()
    messagebox.showinfo("New Shoe", f"Started new {deck_count_var.get()}-deck shoe.")

def show_stats():
    """Popup for detailed card frequency."""
    win = Toplevel(root)
    win.title("Seen Cards")
    win.geometry("250x400")
    tk.Label(win, text="Cards Seen", font=("Arial", 12, "bold")).pack(pady=10)
    
    frame = tk.Frame(win)
    frame.pack()
    for i, rank in enumerate(VALID_RANKS):
        tk.Label(frame, text=f"Rank {rank}:   {seen_card_counts[rank]}", font=("Consolas", 10)).grid(row=i, column=0, sticky="w", padx=20)
    
    tk.Button(win, text="Close", command=win.destroy).pack(pady=20)


# --- GUI LAYOUT CONSTRUCTION ---

# 1. Header (Stats & Action)
frame_header = tk.Frame(root, pady=10); frame_header.pack()
tk.Label(frame_header, textvariable=stats_text, font=("Arial", 14, "bold")).pack()
lbl_action = tk.Label(frame_header, textvariable=action_text, font=("Arial", 18, "bold")); lbl_action.pack()

# 2. Info Display (Hands)
frame_hands = tk.Frame(root); frame_hands.pack()
tk.Label(frame_hands, textvariable=dealer_text, font=("Consolas", 10)).pack()
tk.Label(frame_hands, textvariable=player_text, font=("Consolas", 10)).pack()

# 3. Mode Controls
frame_modes = tk.Frame(root, pady=10); frame_modes.pack()
tk.Label(frame_modes, text="Select Input Mode:", font=("Arial", 8)).pack()

btn_count = tk.Button(frame_modes, text="Count Only", width=12, command=partial(set_mode, "COUNT ONLY"))
btn_count.pack(side=tk.LEFT, padx=2)
btn_player = tk.Button(frame_modes, text="Player Hand", width=12, command=partial(set_mode, "PLAYER HAND"))
btn_player.pack(side=tk.LEFT, padx=2)
btn_dealer = tk.Button(frame_modes, text="Dealer Card", width=12, command=partial(set_mode, "DEALER UP-CARD"))
btn_dealer.pack(side=tk.LEFT, padx=2)

# 4. Utility Buttons
frame_utils = tk.Frame(root, pady=5); frame_utils.pack()
btn_remove = tk.Button(frame_utils, textvariable=remove_text, width=15, bg="#90EE90", command=toggle_remove)
btn_remove.pack(side=tk.LEFT, padx=5)
tk.Button(frame_utils, text="View Stats", width=15, command=show_stats).pack(side=tk.LEFT, padx=5)

# 5. Card Grid (Keypad)
frame_grid = tk.Frame(root, pady=10); frame_grid.pack()
for i, rank in enumerate(VALID_RANKS):
    btn = tk.Button(frame_grid, text=rank, width=5, height=2, command=partial(card_button_clicked, rank))
    btn.grid(row=i//4, column=i%4, padx=2, pady=2)

# 6. Footer (Reset Controls)
frame_footer = tk.Frame(root, pady=20); frame_footer.pack(side=tk.BOTTOM, fill=tk.X)
tk.Button(frame_footer, text="Next Hand", bg="#FFD700", command=reset_hand).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

frame_deck = tk.Frame(frame_footer); frame_deck.pack(side=tk.RIGHT, padx=5)
tk.Label(frame_deck, text="Decks:").pack(side=tk.LEFT)
tk.OptionMenu(frame_deck, deck_count_var, *DECK_OPTIONS).pack(side=tk.LEFT, padx=2)
tk.Button(frame_deck, text="New Shoe", bg="#FF4500", fg="white", command=new_shoe).pack(side=tk.LEFT, padx=2)

# --- START ---
set_mode("COUNT ONLY")
update_gui()

if __name__ == '__main__':
    root.mainloop()