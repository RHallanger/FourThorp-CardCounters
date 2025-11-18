# StrategyGuide.py
# This file is the "Book." It holds all the Blackjack
# Basic Strategy rules and the Hi-Lo deviations.
# It's a module, so it doesn't run on its own.

# A dictionary to hold the "hard values" of cards for calculating totals.
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def get_player_action(player_hand_cards, dealer_up_card, true_count):
    """
    Decides the best action (Hit, Stand, Double) based on the
    player's hand, dealer's card, and the true count.
    """
    
    # --- 1. Calculate Player's Total ---
    player_total = 0
    ace_count = 0
    for card in player_hand_cards:
        player_total += CARD_VALUES[card]
        if card == 'A':
            ace_count += 1
            
    # Adjust for "soft" aces (e.g., A+5=16, but if we hit and get a 10, it becomes 1+5+10=16)
    while player_total > 21 and ace_count > 0:
        player_total -= 10  # Change an 11-point Ace to a 1-point Ace
        ace_count -= 1
        
    # --- 2. Calculate Dealer's Up-Card Value ---
    # We assume the dealer only has one card visible
    if not dealer_up_card:
        return "Wait" # No dealer card visible
        
    dealer_val = CARD_VALUES[dealer_up_card[0]] # Get value of first (only) dealer card

    # --- 3. Run Strategy Rules ---
    # This is where we will build the "Basic Strategy Chart"
    
    # Example Rule: Hard 16 vs. Dealer 10
    if player_total == 16 and ace_count == 0 and dealer_val == 10:
        # Standard rule is Stand, but with Hi-Lo, we hit at TC >= 0
        if true_count >= 0:
            return "Hit"
        else:
            return "Stand"
            
    # Example Rule: Player has 11
    if player_total == 11:
        return "Double Down"
        
    # Example Rule: Player has 17 or more (hard)
    if player_total >= 17 and ace_count == 0:
        return "Stand"

    # Default if no specific rule matches
    return "Hit"