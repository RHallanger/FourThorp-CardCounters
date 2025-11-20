import cv2
import numpy as np
import pyautogui
import os
import glob
import time
from ultralytics import YOLO
from HiLoCounter import HiLoCounter 
import StrategyGuide # <-- UNCOMMENT THIS LINE WHEN YOU ADD THE HIT/STAND LOGIC

# --- CONFIGURATION ---
CONFIDENCE_THRESHOLD = 0.10  
SCREEN_REGION = None        

# --- ZONES ---
PLAYER_ZONE = (372, 393, 354, 320) 
DEALER_ZONE = (855, 376, 245, 296) 

# --- SMART SETUP ---
print("\n" + "="*50)
print("   🃏 UNIVERSAL BLACKJACK AI COUNTER v1.0 🃏")
print("="*50)
print("🔍 Searching for trained AI model...")

possible_brains = glob.glob("runs/detect/*/weights/best.pt")

if not possible_brains:
    # Fallback check for local file
    if os.path.exists("blackjack_brain.pt"):
         model_path = "blackjack_brain.pt"
    else:
        print("❌ ERROR: Could not find any 'best.pt' files.")
        print("   Please run 'train_yolo.py' to build the brain first.")
        exit()
else:
    model_path = max(possible_brains, key=os.path.getmtime)

try:
    model = YOLO(model_path) 
    print(f"✅ AI Brain Loaded: {os.path.basename(model_path)}")
except Exception as e:
    print(f"❌ CRITICAL ERROR loading model: {e}")
    exit()

brain = HiLoCounter(decks=6)
cards_counted_this_hand = []

# --- PRINT INSTRUCTIONS ---
print("-" * 50)
print("🎮  CONTROLS (Click the Video Window first!):")
print("   [ q ]  : QUIT the program")
print("   [ r ]  : RESET HAND (Clears memory of current cards)")
print("   [ n ]  : NEW SHOE (Resets Count to 0)")
print("-" * 50)
print("📊  HUD LEGEND:")
print("   RC     : Running Count (Raw Hi-Lo Value)")
print("   TC     : True Count (RC divided by decks remaining)")
print("   Action : Basic Strategy Recommendation")
print("="*50 + "\n")

# --- HELPER FUNCTIONS ---

def get_card_ranks(results_list):
    """Parses YOLO output into a simple list of card rank names."""
    ranks = []
    RANK_MAP = {
        0: 'A', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7',
        7: '8', 8: '9', 9: '10', 10: 'J', 11: 'Q', 12: 'K'
    }
    
    if results_list and len(results_list) > 0:
        r = results_list[0] 
        for box in r.boxes:
            if box.conf.cpu().numpy()[0] > CONFIDENCE_THRESHOLD:
                cls_index = int(box.cls.cpu().numpy()[0])
                ranks.append(RANK_MAP.get(cls_index, 'Unknown'))
    return ranks

def calculate_hand_total(cards):
    """Calculates the Blackjack value of a list of cards."""
    total = 0
    ace_count = 0
    card_values = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    for card in cards:
        if card in card_values:
            total += card_values[card]
            if card == 'A':
                ace_count += 1
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
    return total


# --- MAIN LOOP ---
while True:
    # 1. CAPTURE & CROP
    full_frame = np.array(pyautogui.screenshot(region=SCREEN_REGION))
    full_frame_bgr = cv2.cvtColor(full_frame, cv2.COLOR_RGB2BGR)

    d_x, d_y, d_w, d_h = DEALER_ZONE
    p_x, p_y, p_w, p_h = PLAYER_ZONE
    
    dealer_img_crop = full_frame_bgr[d_y:d_y + d_h, d_x:d_x + d_w]
    player_img_crop = full_frame_bgr[p_y:p_y + p_h, p_x:p_x + p_w]

    # 2. RUN AI
    dealer_results = model.predict(dealer_img_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
    player_results = model.predict(player_img_crop, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    # 3. PARSE
    dealer_hand_ranks = get_card_ranks(dealer_results)
    player_hand_ranks = get_card_ranks(player_results)
    
    # 4. UPDATE BRAIN
    all_cards = dealer_hand_ranks + player_hand_ranks
    for card in all_cards:
        if card not in cards_counted_this_hand:
            brain.count_card(card)
            cards_counted_this_hand.append(card)
            print(f"--> Counted New Card: {card}") # Terminal feedback

    # 5. STRATEGY
    player_total = calculate_hand_total(player_hand_ranks)
    dealer_up_card_total = calculate_hand_total(dealer_hand_ranks)
    action = "READY"
    
    # 6. DRAW HUD
    hud = np.zeros((200, 400, 3), dtype="uint8")
    rc = brain.running_count
    tc = brain.true_count()
    
    cv2.putText(hud, f"RC: {rc} | TC: {tc}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(hud, f"Dealer: {dealer_hand_ranks} ({dealer_up_card_total})", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    cv2.putText(hud, f"Player: {player_hand_ranks} ({player_total})", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(hud, f"Action: {action}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # 7. VISUALIZE
    full_annotated = model.predict(full_frame_bgr, conf=CONFIDENCE_THRESHOLD, verbose=False)[0].plot()
    display_h, display_w = full_annotated.shape[:2]
    if display_h > 800:
        scale = 800 / display_h
        full_annotated = cv2.resize(full_annotated, None, fx=scale, fy=scale)

    cv2.imshow("Universal YOLO Scanner", full_annotated)
    cv2.imshow("HUD", hud)

    # 8. CONTROLS
    key = cv2.waitKey(1)
    if key == ord('q'): 
        print("Quitting...")
        break
    elif key == ord('r'): 
        cards_counted_this_hand = []
        print("\n--- 🖐️ HAND RESET ---")
    elif key == ord('n'): 
        brain.reset_shoe()
        cards_counted_this_hand = []
        print("\n--- 👟 NEW SHOE STARTED ---")

cv2.destroyAllWindows()