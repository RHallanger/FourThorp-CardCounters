import cv2
import numpy as np
import pyautogui
import os
import time
from HiLoCounter import HiLoCounter # Imports the Brain
import StrategyGuide 

# --- CONFIGURATION ---
MIN_MATCH_COUNT = 40 # Required "clues" for detection (Fixes background noise)

# --- ZONES (Your final measured coordinates) ---
PLAYER_ZONE = (372, 393, 354, 320)
DEALER_ZONE = (855, 376, 245, 296)

# --- SETUP ---
brain = HiLoCounter(decks=6)
TEMPLATE_FOLDER = "templates"

# Initialize the "Detective" (ORB) and Matcher
orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# List of card ranks to load (13 total)
card_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
known_cards = []

print("------------------------------------------------")
print("PRE-ANALYZING TEMPLATES (Finding Clues)...")
for rank in card_ranks:
    # 1. LOAD THE STANDARD TEMPLATE (e.g., template_5.png)
    filename = f"template_{rank}.png" 
    path = os.path.join(TEMPLATE_FOLDER, filename)
    
    img = cv2.imread(path, 0) 
    
    if img is None:
        print(f"[ERROR] Missing template: {filename}")
    else:
        # Find the clues (Keypoints and Descriptors) ONCE at startup.
        kp, des = orb.detectAndCompute(img, None)
        
        if des is not None:
            # Store standard template data
            known_cards.append({
                "name": rank,
                "kp": kp,
                "des": des,
                "shape": img.shape 
            })
            print(f"Learned {rank}")

    # 2. LOAD THE HIDDEN TEMPLATE (Only for '5' and 'J') # <--- OCCLUSION FIX
    if rank == '5' or rank == 'J':
        hidden_file = f"template_{rank}_hidden.png"
        hidden_path = os.path.join(TEMPLATE_FOLDER, hidden_file)
        hidden_img = cv2.imread(hidden_path, 0)
        
        if hidden_img is not None:
             kp_h, des_h = orb.detectAndCompute(hidden_img, None)
             if des_h is not None:
                # Store the hidden template data with the same card name ('5' or 'J')
                known_cards.append({
                    "name": rank, 
                    "kp": kp_h, 
                    "des": des_h, 
                    "shape": hidden_img.shape
                })
                print(f"Learned {rank} (Hidden)")
        # Note: If the hidden file is missing, a warning isn't printed here 
        # to avoid confusing the user with too many warnings.

print(f"------------------------------------------------")
print(f"Bot Ready. Scanning for {len(known_cards)} total templates.")
cards_counted_this_hand = []

# --- HELPER FUNCTION: The Detective (ORB Logic) ---
def find_raw_detections(screenshot_bgr, known_cards_data):
    """
    Scans the screenshot for ALL known cards and returns a list of raw detections.
    """
    raw_detections = []
    
    gray_screen = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    kp_screen, des_screen = orb.detectAndCompute(gray_screen, None)
    
    if des_screen is None:
        return []

    for card in known_cards_data:
        
        matches = bf.match(card["des"], des_screen)
        matches = sorted(matches, key=lambda x: x.distance)
        good_matches = [m for m in matches if m.distance < 50]
        
        if len(good_matches) > MIN_MATCH_COUNT:
            try:
                src_pts = np.float32([ card["kp"][m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp_screen[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
                
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if M is not None:
                    h, w = card["shape"]
                    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                    dst = cv2.perspectiveTransform(pts, M)
                    
                    x, y, w, h = cv2.boundingRect(dst)
                    
                    raw_detections.append({
                        "box": [x, y, w, h],
                        "name": card["name"],
                        "source": screenshot_bgr
                    })
            except Exception:
                pass 

    return raw_detections

# --- HELPER FUNCTION: Calculate Hand Total (Unchanged) ---
def calculate_hand_total(cards):
    """Calculates the Blackjack value of a list of cards."""
    total = 0
    ace_count = 0
    
    card_values = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    
    for card in cards:
        total += card_values[card]
        if card == 'A':
            ace_count += 1
            
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
        
    return total


# --- MAIN LOOP ---
while True:
    # 1. Capture Zones
    dealer_img_raw = np.array(pyautogui.screenshot(region=DEALER_ZONE))
    player_img_raw = np.array(pyautogui.screenshot(region=PLAYER_ZONE))
    
    dealer_img = cv2.cvtColor(dealer_img_raw, cv2.COLOR_RGB2BGR)
    player_img = cv2.cvtColor(player_img_raw, cv2.COLOR_RGB2BGR)

    # 2. Find Cards (Using the ORB Detective)
    raw_dealer_detections = find_raw_detections(dealer_img, known_cards)
    raw_player_detections = find_raw_detections(player_img, known_cards)
    
    all_raw_detections = raw_dealer_detections + raw_player_detections
    
    # 3. GROUP OVERLAPPING BOXES (NMS - The Jitter Fix)
    all_boxes = [d['box'] for d in all_raw_detections]
    
    grouped_boxes, weights = cv2.groupRectangles(all_boxes * 2, 2, 0.2) 
    
    final_cards = []
    
    # 4. DRAW FINAL BOXES AND GET UNIQUE NAMES
    for (x, y, w, h) in grouped_boxes:
        
        # Find the original detection that best matches this new, merged box
        center_x = x + w // 2
        best_name = "UNKNOWN"
        best_distance = float('inf')
        
        for d in all_raw_detections:
            dx, dy, dw, dh = d['box']
            d_center_x = dx + dw // 2
            
            distance = abs(center_x - d_center_x) 
            
            if distance < best_distance:
                best_distance = distance
                best_name = d['name']
        
        # Draw the final, unique, merged box on the correct image source
        if best_name in [d['name'] for d in raw_dealer_detections]:
             cv2.rectangle(dealer_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
             cv2.putText(dealer_img, best_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        else:
             cv2.rectangle(player_img, (x, y), (x + w, y + h), (0, 255, 0), 3)
             cv2.putText(player_img, best_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        final_cards.append(best_name)

    # 5. UPDATE THE BRAIN (HiLoCounter)
    for card in final_cards:
        if card not in cards_counted_this_hand:
            brain.count_card(card)
            cards_counted_this_hand.append(card)

    # 6. CALCULATE STRATEGY (HUD Setup)
    dealer_hand = [c for c in final_cards if c in [d['name'] for d in raw_dealer_detections]]
    player_hand = [c for c in final_cards if c in [d['name'] for d in raw_player_detections]]

    player_total = calculate_hand_total(player_hand)
    dealer_up_card_total = calculate_hand_total(dealer_hand)
    action = "BUILDING..." 
    
    # 7. DRAW THE HUD
    hud = np.zeros((200, 400, 3), dtype="uint8")
    rc = brain.running_count
    tc = brain.true_count()
    
    cv2.putText(hud, f"RC: {rc} | TC: {tc}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(hud, f"Dealer: {dealer_hand} ({dealer_up_card_total})", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    cv2.putText(hud, f"Player: {player_hand} ({player_total})", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.putText(hud, f"Action: {action}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # 8. SHOW WINDOWS
    cv2.imshow("HUD", hud)
    cv2.imshow("Dealer View", dealer_img)
    cv2.imshow("Player View", player_img)
    
    key = cv2.waitKey(1)
    if key == ord('q'): break
    elif key == ord('r'): 
        cards_counted_this_hand = []
    elif key == ord('n'): 
        brain.reset_shoe()
        cards_counted_this_hand = []

cv2.destroyAllWindows()