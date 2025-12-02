# HiLoCounting.py
# -----------------------------------------------
# This file defines the "Brain" (the HiLoCounter class).
# It calculates the Running Count and True Count.

class HiLoCounter:
    """Tracks running and true count for a multi-deck shoe."""

    def __init__(self, decks=6):
        self.decks = decks
        self.total_cards = decks * 52
        self.cards_seen = 0
        self.running_count = 0

    def count_card(self, card):
        """Update running count based on Hi-Lo rules."""
        # We handle both string ranks ('2') and integers if passed
        high_cards = ['10', 'J', 'Q', 'K', 'A']
        low_cards = ['2', '3', '4', '5', '6']

        # Convert inputs to string just in case to avoid errors
        card_str = str(card)

        if card_str in low_cards:
            self.running_count += 1
        elif card_str in high_cards:
            self.running_count -= 1
        
        # 7, 8, 9 are neutral (0)
        
        self.cards_seen += 1

    def decks_remaining(self):
        """Estimate decks remaining in the shoe."""
        remaining = (self.total_cards - self.cards_seen) / 52.0
        return max(remaining, 0.01)

    def true_count(self):
        """Calculate true count = running count / decks remaining."""
        return round(self.running_count / self.decks_remaining(), 2)
    
    def reset_shoe(self):
        """Resets the count to 0 for a new game."""
        self.cards_seen = 0
        self.running_count = 0
        print("--- SHOE SHUFFLED / RESET ---")