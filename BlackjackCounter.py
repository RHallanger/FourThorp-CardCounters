# BlackjackCounter.py
# -------------------
# Simulates a Blackjack table with Hi-Lo card counting
# and calculates simplified win odds for each player.

class CardCounter:
    """Tracks running and true count for a multi-deck shoe."""

    def __init__(self, decks=6):
        self.decks = decks
        self.total_cards = decks * 52
        self.cards_seen = 0
        self.running_count = 0

    def count_card(self, card):
        """Update running count using Hi-Lo system."""
        high_cards = ['10', 'J', 'Q', 'K', 'A']
        low_cards = ['2', '3', '4', '5', '6']

        if card in low_cards:
            self.running_count += 1
        elif card in high_cards:
            self.running_count -= 1
        # 7-9 are neutral

        self.cards_seen += 1

    def decks_remaining(self):
        """Estimate remaining decks in the shoe."""
        remaining = (self.total_cards - self.cards_seen) / 52.0
        return max(remaining, 0.01)  # prevent division by zero

    def true_count(self):
        """Return the running count normalized by decks remaining."""
        return round(self.running_count / self.decks_remaining(), 2)


def calculate_win_odds(player_value, dealer_upcard, true_count):
    """
    Simplified win odds calculation based on player's hand value,
    dealer's upcard, and true count.
    Returns a float percentage (0-100).
    """
    # Base odds simplified for demonstration
    base_odds = {
        11: 58,
        12: 35,
        13: 40,
        14: 44,
        15: 47,
        16: 50,
        17: 69,
        18: 77,
        19: 85,
        20: 92,
        21: 100
    }

    odds = base_odds.get(player_value, 50)

    # Adjust for dealer upcard (very simplified)
    if dealer_upcard in ['7','8','9','10','J','Q','K','A']:
        odds -= 5

    # Adjust based on true count (rough approximation)
    odds += true_count * 2  # every positive count slightly improves player odds
    odds = max(min(odds, 100), 0)  # clamp between 0 and 100
    return round(odds, 2)


def simulate_table(player_values, dealer_upcard, counter):
    """
    Simulates a table for multiple players.
    player_values: list of integers representing each player's hand value
    dealer_upcard: string representing dealer's visible card
    counter: CardCounter instance
    Returns list of win odds for each player.
    """
    true_count = counter.true_count()
    return [calculate_win_odds(p, dealer_upcard, true_count) for p in player_values]


# --- Example Usage ---
if __name__ == "__main__":
    print("Blackjack Counter with Hi-Lo Card Counting")
    counter = CardCounter(decks=6)

    # Example cards already seen
    dealt_cards = ['2', '5', 'K', '6', '10', '3']
    for card in dealt_cards:
        counter.count_card(card)

    # Example table with multiple players
    player_hands = [16, 18, 20]  # hand values for 3 players
    dealer_card = '10'

    odds = simulate_table(player_hands, dealer_card, counter)

    print(f"Running count: {counter.running_count}")
    print(f"True count: {counter.true_count()}")
    for i, o in enumerate(odds, start=1):
        print(f"Player {i} ({player_hands[i-1]}) → Win Odds: {o}%")
