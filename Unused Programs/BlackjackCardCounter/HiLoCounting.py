# HiLoCounter.py
# -----------------------------------------------
# An interactive Hi-Lo card counting simulator for Blackjack training.
#
# This program helps you practice the core skill of card counting
# by tracking both the running count and true count as cards are entered.
# It accepts flexible input (numbers 1–13 or face cards A, J, Q, K)
# and dynamically updates the count based on Hi-Lo system rules:
#
#   - Low cards (2–6) increase the count (+1)
#   - High cards (10–A) decrease the count (–1)
#   - Neutral cards (7–9) do not affect the count
#
# The simulator also estimates decks remaining in the shoe
# and calculates the true count (running count ÷ decks remaining),
# helping you understand when the deck is favorable for the player.
#
# This script is a standalone learning tool for mastering
# Hi-Lo counting logic before applying it to full Blackjack simulations.


class HiLoCounter:
    """Tracks running and true count for a multi-deck shoe."""

    def __init__(self, decks=6):
        self.decks = decks
        self.total_cards = decks * 52
        self.cards_seen = 0
        self.running_count = 0

    def count_card(self, card):
        """Update running count based on Hi-Lo rules."""
        high_cards = ['10', 'J', 'Q', 'K', 'A']
        low_cards = ['2', '3', '4', '5', '6']

        if card in low_cards:
            self.running_count += 1
        elif card in high_cards:
            self.running_count -= 1
        # 7-9 are neutral → do nothing
        self.cards_seen += 1

    def decks_remaining(self):
        """Estimate decks remaining in the shoe."""
        remaining = (self.total_cards - self.cards_seen) / 52.0
        return max(remaining, 0.01)

    def true_count(self):
        """Calculate true count = running count / decks remaining."""
        return round(self.running_count / self.decks_remaining(), 2)


# --- Interactive Test ---
print("Welcome to the Hi-Lo Card Counting Simulator!")

while True:
    try:
        decks = int(input("Enter number of decks in the shoe (e.g., 6): "))
        if decks <= 0:
            print("Please enter a positive number of decks.")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter an integer.")

counter = HiLoCounter(decks=decks)

print("\nStart entering cards as they are dealt (e.g., 2, 5, K, A, 10). Type 'quit' to stop.\n")

while True:
    card = input("Card dealt: ").strip().upper()

    ### The string above suggests using 'quit' to stop, but the code below checks for 'QUIT'.
    ### you can use card.upper() or card.lower == 'quit' to standardize the input.
    ### The exit condition kind of results in an exit, but it uses the end of file implicit exit rather than an explicit exit.

    if card == 'QUIT':
        print("\nExiting simulator.")
        break

    ### The num variable can be simplified by using a dictionary mapping or switch-case structure. (It functions fine as is)
    ### ie: card_map = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}

    ### The user's input is strictly numeric and doesn't handle partial spelling or full spelling of face cards at all. The value error exception does not handle any input and allows for too broad of application.
    ### This can be improved by leaving the variable as a string and checking if a defining character is present, still use .upper()/.lower() to standardize input.

    # Map numeric input to standard card strings
    try:
        num = int(card)
        if num == 1:
            card = 'A'
        elif 2 <= num <= 10:
            card = str(num)
        elif num == 11:
            card = 'J'
        elif num == 12:
            card = 'Q'
        elif num == 13:
            card = 'K'
        else:
            print("Invalid card number. Use 1-13 for Ace-King.")
            continue
    except ValueError:
        # Keep face cards entered as letters
        card = card.upper()

    if card not in ['2','3','4','5','6','7','8','9','10','J','Q','K','A']:
        print("Invalid card. Try again.")
        continue

    # Update counter and show counts
    counter.count_card(card)
    print(f"Running count: {counter.running_count}, True count: {counter.true_count()}")
    print(f"Decks remaining (approx): {round(counter.decks_remaining(), 2)}\n")

### Overall, well done! The code shows the core logic of Hi-Lo counting clearly and interactively.
### If you want/are able to, consider incorporating additional features for Illustrious 18 and Fab 4 Surrenders.
### I used Wizard of Odds as a reference for the card counting rules and strategies.