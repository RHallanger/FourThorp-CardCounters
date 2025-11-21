import cv2
import numpy as np
import pyautogui
import os
import glob
import time
from ultralytics import YOLO
from HiLoCounter import HiLoCounter 
import StrategyGuide # <-- UNCOMMENTED: Now using the strategy logic

# --- CONFIGURATION ---
# Confidence: 0.5 is a good starting point for a fine-tuned model.
CONFIDENCE_THRESHOLD = 0.5  

# --- ZONES (Your measured coordinates) ---
# Player Zone: (x, y, w, h)
PLAYER_ZONE = (372, 393, 354, 320) 
# Dealer Zone: (x, y, w, h)
DEALER_ZONE = (855, 376, 245, 296) 

# --- SMART SETUP: Find the Brain ---
print("🔍 Searching for trained AI model...")

# Look for the newest 'best.pt' in the runs folder
# This will find your 'final_fine_tuned_model3' automatically
possible_brains = glob.glob("runs/detect/*/weights/best.pt")

if not possible_brains:
    # Fallback check for local file
    if os.path.exists("blackjack_brain.pt"):
         model_path = "blackjack_brain.pt"
    else:
        print("❌ ERROR: Could not find any 'best.pt' files.")
        print("   Make sure your training finished successfully.")
        exit()
else:
    # Pick the most recently modified file (Your model3)
    model_path = max(possible_brains, key=os.path.getmtime)

try:
    print(f"✅ Loading AI Brain: {model_path}")
    model = YOLO(model_path) 
except Exception as e:
    print(f"❌ CRITICAL ERROR loading model: {e}")
    exit()

brain = HiLoCounter(decks=6)
cards_counted_this_hand = []

# --- HELPER: Translate AI Output to Card Name ---
def get_card_ranks(results_list):
    """
    Translates YOLO class ID into Rank Name ('A', '2'...)
    """
    ranks = []
    
    # Standard Map (Backup)
    RANK_MAP = {
        0: '10', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 
        6: '7', 7: '8', 8: '9', 9: 'A', 10: 'J', 11: 'K', 12: 'Q'
    }
    
    if results_list and len(results_list) > 0:
        r = results_list[0] 
        for box in r.boxes:
            if box.conf.cpu().numpy()[0] > CONFIDENCE_THRESHOLD:
                cls_index = int(box.cls.cpu().numpy()[0])
                
                # Use the name from the model file itself
                if hasattr(model.names, 'get'):
                    name = model.names[cls_index]
                else:
                    name = RANK_MAP.get(cls_index, 'Unknown')
                
                ranks.append(name)
    return ranks

def calculate_hand_total(cards):
    total = 0
    ace_count = 0
    card_values = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11,
        'jack': 10, 'queen': 10, 'king': 10, 'ace': 11
    }
    for card in cards:
        # Clean up the name (make it uppercase, remove spaces)
        clean_card = str(card).upper().strip()
        if clean_card in card_values:
            total += card_values[clean_card]
            if clean_card == 'A' or clean_card == 'ACE':
                ace_count += 1
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
    return total


# --- MAIN LOOP ---
print("🟢 BOT RUNNING. Switch to game window.")
print("Controls: 'q' to Quit, 'r' to Reset Hand, 'n' to New Shoe")

while True:
    # 1. Capture Screen
    full_frame = np.array(pyautogui.screenshot())
    full_frame_bgr = cv2.cvtColor(full_frame, cv2.COLOR_RGB2BGR)

    d_x, d_y, d_w, d_h = DEALER_ZONE
    p_x, p_y, p_w, p_h = PLAYER_ZONE
    
    # Crop images for the AI
    dealer_img_crop = full_frame_bgr[d_y:d_y + d_h, d_x:d_x + d_w]
    player_img_crop = full_frame_bgr[p_y:p_y + p_h, p_x:p_x + p_w]

    # 2. Run AI
    dealer_results = model.predict(dealer_img_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
    player_results = model.predict(player_img_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    # 3. Get Card Names
    dealer_hand = get_card_ranks(dealer_results)
    player_hand = get_card_ranks(player_results)
    
    # 4. Update Count
    all_cards = dealer_hand + player_hand
    for card in all_cards:
        if card not in cards_counted_this_hand:
            brain.count_card(card)
            cards_counted_this_hand.append(card)
            print(f"--> Counted: {card}")

    # 5. Calculate Strategy
    player_total = calculate_hand_total(player_hand)
    dealer_total = calculate_hand_total(dealer_hand)
    
    # Get the Strategy Recommendation!
    action = StrategyGuide.get_player_action(player_hand, dealer_hand, brain.true_count())
    
    # 6. Draw HUD
    hud = np.zeros((200, 400, 3), dtype="uint8")
    rc = brain.running_count
    tc = brain.true_count()
    
    cv2.putText(hud, f"RC: {rc} | TC: {tc}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(hud, f"Dealer: {dealer_hand} ({dealer_total})", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    cv2.putText(hud, f"Player: {player_hand} ({player_total})", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    # Highlight the Action
    cv2.putText(hud, f"Action: {action}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # 7. Visualize
    dealer_plot = dealer_results[0].plot()
    player_plot = player_results[0].plot()

    cv2.imshow("HUD", hud)
    cv2.imshow("Dealer View", dealer_plot)
    cv2.imshow("Player View", player_plot)

    # 8. Controls
    key = cv2.waitKey(1)
    if key == ord('q'): break
    elif key == ord('r'): 
        cards_counted_this_hand = []
        print("--- Hand Reset ---")
    elif key == ord('n'): 
        brain.reset_shoe()
        cards_counted_this_hand = []
        print("--- New Shoe ---")

cv2.destroyAllWindows()