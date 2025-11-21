# StrategyGuide.py
# This file is the "Book." It holds all the Blackjack
# Basic Strategy rules and the Hi-Lo deviations.

# Hard values for calculating hand totals
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

def get_player_action(player_hand_cards, dealer_hand_cards, true_count):
    """
    Decides the best action (Hit, Stand, Double) based on the 
    player's hand, dealer's card, and the True Count.
    """
    
    # --- 1. PRE-CALCULATE VALUES ---
    player_total = 0
    ace_count = 0
    for card in player_hand_cards:
        if card in CARD_VALUES:
            player_total += CARD_VALUES[card]
            if card == 'A':
                ace_count += 1
            
    # Adjust for soft aces
    while player_total > 21 and ace_count > 0:
        player_total -= 10
        ace_count -= 1
        
    # Get the value of the dealer's visible card (the first card in the list)
    dealer_val = 0
    if dealer_hand_cards and len(dealer_hand_cards) > 0:
        first_card = dealer_hand_cards[0]
        if first_card in CARD_VALUES:
            dealer_val = CARD_VALUES[first_card]
    
    # --- 2. RUN STRATEGY RULES ---
    
    # Rule 1: Always Stand on 17 or more (Hard)
    if player_total >= 17 and ace_count == 0:
        return "STAND"

    # Rule 2: Always Hit on 11 or less (Unless Doubling)
    if player_total <= 11 and player_total != 11:
        return "HIT"
    
    # Rule 3: The Hard 12 - 16 Decisions (The trickiest zone)
    if player_total >= 12 and player_total <= 16 and ace_count == 0:
        
        # Hi-Lo Deviation: Hard 16 vs Dealer 10 (Illustrious 18)
        if player_total == 16 and dealer_val == 10:
            if true_count >= 0:
                # Deviation: If the True Count is 0 or higher, HIT.
                return "HIT" 
            else:
                # Basic Strategy: Stand if TC is negative
                return "STAND" 

        # Basic Strategy: Stand if Dealer's Up-Card is low (2 through 6)
        if dealer_val >= 2 and dealer_val <= 6:
            return "STAND"
        else:
            # Basic Strategy: Hit if Dealer's Up-Card is 7 through Ace
            return "HIT" 
            
    # Rule 4: SOFT TOTALS (Hands with an Ace)
    if ace_count > 0:
        
        # Soft 19 or 20 (A-8 or A-9) always stands
        if player_total >= 19:
            return "STAND"
        
        # Soft 18 (A-7) decision: Stand vs low, Hit vs high
        if player_total == 18:
            if dealer_val >= 9 or dealer_val == 11: # 9, 10, A
                return "HIT"
            else:
                return "STAND"
                
    # --- 5. DEFAULT ACTION ---
    return "HIT"