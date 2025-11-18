import cv2
import numpy as np
import pyautogui
import os
# We updated the import to match the recommended filename change
from HiLoCounter import HiLoCounter 
# import StrategyGuide 

# --- CONFIGURATION ---
# The "Confidence Threshold".
# The detective needs to find at least this many matching "clues" 
# to confirm a card is present. 15-20 is usually a good starting point.
MIN_MATCH_COUNT = 15 

# --- ZONES (Your measured coordinates) ---
PLAYER_ZONE = (339, 430, 420, 183) 
DEALER_ZONE = (855, 376, 245, 296)

# --- SETUP ---
brain = HiLoCounter(decks=6)
TEMPLATE_FOLDER = "templates"

# Initialize the "Detective" (ORB)
orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# List of card ranks to load
card_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
known_cards = []

print("------------------------------------------------")
print("PRE-ANALYZING TEMPLATES (Finding Clues)...")
for rank in card_ranks:
    # We expect filenames like 'template_K.png' or 'template_2.png'
    filename = f"template_{rank}.png" 
    path = os.path.join(TEMPLATE_FOLDER, filename)
    
    img = cv2.imread(path, 0)
    
    if img is None:
        print(f"[ERROR] Could not load {filename}!")
    else:
        # Find the clues (Keypoints and Descriptors) for this card NOW.
        # We do this once at startup so the loop is fast.
        kp, des = orb.detectAndCompute(img, None)
        
        if des is None:
            print(f"[WARNING] No clues found in {filename}. Image too plain?")
        else:
            # Store everything we need to find this card later
            known_cards.append({
                "name": rank,
                "kp": kp,
                "des": des,
                "shape": img.shape # height, width
            })
            print(f"Learned {rank}: Found {len(kp)} clues.")

print(f"------------------------------------------------")
print(f"Bot Ready. Scanning for {len(known_cards)} card types.")
print("Controls: 'q' to Quit, 'r' to Reset Hand, 'n' to New Shoe")

cards_counted_this_hand = []

# --- HELPER FUNCTION: The Detective ---
def find_cards_orb(screenshot_bgr, known_cards_data):
    """
    Scans the screenshot for ALL known cards using Feature Matching.
    Returns a list of card names found (e.g., ['K', '5']).
    """
    found_names = []
    
    # 1. Convert screen to grayscale
    gray_screen = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2GRAY)
    
    # 2. Find clues on the SCREEN
    kp_screen, des_screen = orb.detectAndCompute(gray_screen, None)
    
    if des_screen is None:
        return [], screenshot_bgr # Screen is pitch black?

    # 3. Compare screen clues against every card we know
    for card in known_cards_data:
        
        # Match the descriptors
        matches = bf.match(card["des"], des_screen)
        
        # Sort them (best matches first)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Keep only the "Good" matches (distance < 50 is a common heuristic)
        good_matches = [m for m in matches if m.distance < 50]
        
        # 4. THE VERDICT
        if len(good_matches) > MIN_MATCH_COUNT:
            # We found enough clues! The card is likely here.
            found_names.append(card["name"])
            
            # -- Optional: Draw the Green Box (Homography) --
            # This math draws a box around the card even if it is rotated.
            try:
                src_pts = np.float32([ card["kp"][m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp_screen[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
                
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                if M is not None:
                    h, w = card["shape"]
                    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                    dst = cv2.perspectiveTransform(pts, M)
                    
                    # Draw the polygon on the screenshot
                    cv2.polylines(screenshot_bgr, [np.int32(dst)], True, (0,255,0), 3, cv2.LINE_AA)
                    
                    # Draw the label
                    label_x = int(dst[0][0][0])
                    label_y = int(dst[0][0][1])
                    cv2.putText(screenshot_bgr, card["name"], (label_x, label_y), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            except Exception:
                pass # If drawing fails (rare math error), just ignore it.

    return found_names, screenshot_bgr


# --- MAIN LOOP ---
while True:
    # 1. Capture Zones
    dealer_img = np.array(pyautogui.screenshot(region=DEALER_ZONE))
    player_img = np.array(pyautogui.screenshot(region=PLAYER_ZONE))
    
    dealer_img = cv2.cvtColor(dealer_img, cv2.COLOR_RGB2BGR)
    player_img = cv2.cvtColor(player_img, cv2.COLOR_RGB2BGR)

    # 2. Find Cards
    dealer_cards, dealer_debug = find_cards_orb(dealer_img, known_cards)
    player_cards, player_debug = find_cards_orb(player_img, known_cards)
    
    # 3. Update Brain (HiLo)
    all_cards = dealer_cards + player_cards
    for card in all_cards:
        if card not in cards_counted_this_hand:
            brain.count_card(card)
            cards_counted_this_hand.append(card)
            print(f"Counted: {card}") # Debug print

    # 4. Simple HUD
    hud = np.zeros((200, 400, 3), dtype="uint8")
    cv2.putText(hud, f"RC: {brain.running_count} | TC: {brain.true_count()}", (10, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(hud, f"Dealer: {dealer_cards}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    cv2.putText(hud, f"Player: {player_cards}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    # 5. Show Windows
    cv2.imshow("HUD", hud)
    cv2.imshow("Dealer View", dealer_debug)
    cv2.imshow("Player View", player_debug)
    
    key = cv2.waitKey(1)
    if key == ord('q'): break
    elif key == ord('r'): 
        cards_counted_this_hand = []
        print("Hand Reset")
    elif key == ord('n'): 
        brain.reset_shoe()
        cards_counted_this_hand = []

cv2.destroyAllWindows()