import cv2
import numpy as np
import pyautogui
import os
import time
from HiLoCounter import HiLoCounter 
# import StrategyGuide # (Still commented out)

# --- CONFIGURATION (Reverted to Pixel Matching) ---
# This threshold is the required score (0.0 to 1.0) for a pixel match.
# It's the most crucial setting for this version! 0.85 is a good start.
PIXEL_THRESHOLD = 0.85 

# --- ZONES (Your final measured coordinates) ---
PLAYER_ZONE = (372, 393, 354, 320)
DEALER_ZONE = (855, 376, 245, 296)

# --- SETUP: Initializing the Matcher ---
brain = HiLoCounter(decks=6)
TEMPLATE_FOLDER = "templates"

# List of card ranks and colors to load (26 total templates)
card_ranks_and_colors = [
    ('A', 'RED'), ('A', 'BLACK'), ('2', 'RED'), ('2', 'BLACK'),
    ('3', 'RED'), ('3', 'BLACK'), ('4', 'RED'), ('4', 'BLACK'),
    ('5', 'RED'), ('5', 'BLACK'), ('6', 'RED'), ('6', 'BLACK'),
    ('7', 'RED'), ('7', 'BLACK'), ('8', 'RED'), ('8', 'BLACK'),
    ('9', 'RED'), ('9', 'BLACK'), ('10', 'RED'), ('10', 'BLACK'),
    ('J', 'RED'), ('J', 'BLACK'), ('Q', 'RED'), ('Q', 'BLACK'),
    ('K', 'RED'), ('K', 'BLACK'),
]

known_templates = [] 

print("PRE-ANALYZING TEMPLATES...")
for rank, color in card_ranks_and_colors:
    # We look for the required 26 files (e.g., template_A_RED.png)
    filename = f"template_{rank}_{color}.png" 
    path = os.path.join(TEMPLATE_FOLDER, filename)
    
    img = cv2.imread(path, 0) # <-- IMPORTANT: Loads in grayscale (0) for shape/intensity comparison
    
    if img is None:
        print(f"[ERROR] Missing template: {filename}")
    else:
        # Store the necessary data
        h, w = img.shape
        known_templates.append({
            "name": rank,
            "img": img,
            "w": w, "h": h
        })

print(f"Bot Ready. Scanning for {len(known_templates)} templates.")
cards_counted_this_hand = [] 

# --- HELPER FUNCTION: Template Matching Logic ---
def find_raw_detections_tm(screenshot_bgr, known_templates_list):
    """
    Scans the screenshot using cv2.matchTemplate and returns a list of raw detections.
    """
    raw_detections = []
    
    # Converts the screenshot to grayscale (required for template matching comparison)
    gray_screen = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    
    for template_data in known_templates_list:
        w, h = template_data['w'], template_data['h']
        
        # 1. Run the template match (The Stencil)
        res = cv2.matchTemplate(gray_screen, template_data['img'], cv2.TM_CCOEFF_NORMED)
        
        # 2. Find all locations that pass the required score
        loc = np.where(res >= PIXEL_THRESHOLD) 
        
        for pt in zip(*loc[::-1]):
            # Store the match for grouping/counting
            raw_detections.append({
                "box": [pt[0], pt[1], w, h],
                "name": template_data['name'],
            })
            
    return raw_detections

# --- HELPER FUNCTION: Calculate Hand Total (Unchanged) ---
def calculate_hand_total(cards):
    """Calculates the Blackjack value of a list of cards, handling Aces (1 or 11)."""
    total = 0
    ace_count = 0
    card_values = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
    }
    for card in cards:
        total += card_values[card]
        if card == 'A': ace_count += 1
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
    return total


# --- MAIN LOOP (Template Matching Engine) ---
while True:
    # 1. CAPTURE SCREEN ZONES
    dealer_img_raw = np.array(pyautogui.screenshot(region=DEALER_ZONE))
    player_img_raw = np.array(pyautogui.screenshot(region=PLAYER_ZONE))
    
    dealer_img = cv2.cvtColor(dealer_img_raw, cv2.COLOR_RGB2BGR)
    player_img = cv2.cvtColor(player_img_raw, cv2.COLOR_RGB2BGR)

    # 2. FIND RAW DETECTIONS (Using Template Matching)
    raw_dealer_detections = find_raw_detections_tm(dealer_img, known_templates)
    raw_player_detections = find_raw_detections_tm(player_img, known_templates)
    
    all_raw_detections = raw_dealer_detections + raw_player_detections
    
    # 3. GROUP OVERLAPPING BOXES (NMS - The Jitter Fix)
    all_boxes = [d['box'] for d in all_raw_detections]
    
    # Group the boxes and then filter out duplicates/small groups
    grouped_boxes, weights = cv2.groupRectangles(all_boxes * 2, 2, 0.2) 
    
    final_cards = []
    
    # 4. DRAW FINAL BOXES AND GET UNIQUE NAMES
    for (x, y, w, h) in grouped_boxes:
        
        # Find the original detection that best matches this new, merged box (for naming)
        center_x = x + w // 2
        best_name = "UNKNOWN"
        best_distance = float('inf')
        
        for d in all_raw_detections:
            d_center_x = d['box'][0] + d['box'][2] // 2
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
    action = "TODO" 
    
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