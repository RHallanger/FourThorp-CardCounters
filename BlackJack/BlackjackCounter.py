# BlackjackCounter.py - Now deals with completely randomized variables for simulating a blackjack table with card counting.
# All calculations are done using the Hi-Lo card counting system.
import random

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
        return max(remaining, 0.01)

    def true_count(self):
        """Return the running count normalized by decks remaining."""
        return round(self.running_count / self.decks_remaining(), 2)


def calculate_win_odds(player_value, dealer_upcard, true_count):
    """
    Simplified win odds calculation based on player's hand value,
    dealer's upcard, and true count.
    Returns a float percentage (0–100).
    """
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

    # Adjust for dealer upcard (simplified)
    if dealer_upcard in ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
        odds -= 5

    # Adjust based on true count (favorable decks help the player)
    odds += true_count * 2
    odds = max(min(odds, 100), 0)
    return round(odds, 2)


def simulate_table(num_players, counter):
    """Simulates a table for multiple players with random hands."""
    player_hands = [random.randint(12, 21) for _ in range(num_players)]
    dealer_upcard = random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])
    true_count = counter.true_count()

    results = []
    for p in player_hands:
        odds = calculate_win_odds(p, dealer_upcard, true_count)
        results.append((p, odds))
    return dealer_upcard, results


if __name__ == "__main__":
    print("♠ Blackjack Counter Simulator ♣")
    print("Using Hi-Lo Card Counting with Randomized Hands\n")

    # Initialize counter and shoe
    counter = CardCounter(decks=6)
    cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * (counter.decks * 4)
    random.shuffle(cards)

    # Deal random number of cards to simulate mid-shoe
    seen_cards = random.randint(20, 200)
    for _ in range(seen_cards):
        card = random.choice(cards)
        counter.count_card(card)
        cards.remove(card)

    # Random number of players (1–7 typical)
    num_players = random.randint(1, 7)

    dealer_upcard, results = simulate_table(num_players, counter)

    print(f"Cards seen so far: {seen_cards}")
    print(f"Running count: {counter.running_count}")
    print(f"True count: {counter.true_count()}")
    print(f"Dealer's upcard: {dealer_upcard}")
    print(f"Players at table: {num_players}\n")

    for i, (value, odds) in enumerate(results, start=1):
        print(f"Player {i} → Hand: {value}, Win Odds: {odds}%")

    print("\n(Counts and odds change each run — simulates a live shoe.)")

### There is no user interactability in this and runs the simulation automatically one time.
### The cards provided should be randomized, the player count and shoe count should be user defined.