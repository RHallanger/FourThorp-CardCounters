import cv2
import numpy as np
import pyautogui
import os

# --- CONFIGURATION ---
TEMPLATE_FILE = 'templates/template_9_BLACK.png'
GOOD_MATCH_THRESHOLD = 30 # How many "clues" we need to find (e.g., 30)

# --- 1. SETUP THE "DETECTIVE" (ORB) ---
# This creates the ORB object
orb = cv2.ORB_create(nfeatures=1000) # We'll look for 1000 clues

# --- 2. LOAD THE TEMPLATE AND FIND ITS CLUES ---
template = cv2.imread(TEMPLATE_FILE, 0)
if template is None:
    print(f"Error: Could not load {TEMPLATE_FILE}")
else:
    # Find the "clues" (keypoints) and "descriptions" of those clues
    kp1, des1 = orb.detectAndCompute(template, None)
    print(f"Loaded template, found {len(kp1)} keypoints.")

    # --- 3. GET THE SCREENSHOT ---
    print("Taking screenshot...")
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- 4. FIND CLUES ON THE SCREEN ---
    kp2, des2 = orb.detectAndCompute(frame_gray, None)
    print(f"Analyzed screen, found {len(kp2)} keypoints.")

    # --- 5. FIND MATCHES BETWEEN TEMPLATE AND SCREEN ---
    # BFMatcher = Brute Force Matcher. It compares every clue
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    if des1 is not None and des2 is not None:
        matches = bf.match(des1, des2)
        
        # Sort them by how good the match is (lower distance is better)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Keep only the "good" matches
        good_matches = [m for m in matches if m.distance < 50]
        
        print(f"Found {len(good_matches)} good matches.")

        # --- 6. CHECK IF WE FOUND THE CARD ---
        if len(good_matches) > GOOD_MATCH_THRESHOLD:
            print(f"CARD DETECTED! (Found {len(good_matches)} matches)")
            
            # Draw the box (This is more complex than before)
            # Get the coordinates of the match
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
            
            # Find the "homography" (the 4-corner perspective)
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            # Get the corners of the original template
            h,w = template.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            
            # Transform the template corners to their new "angled" position
            dst = cv2.perspectiveTransform(pts,M)
            
            # Draw the 4-sided polygon
            frame = cv2.polylines(frame,[np.int32(dst)],True,(0,255,0),3, cv2.LINE_AA)
        else:
            print("Card not detected.")

        # Draw the first 50 matches (for debugging)
        img_matches = cv2.drawMatches(template, kp1, frame, kp2, matches[:50], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        cv2.imshow("Matches", img_matches)
        cv2.waitKey(0)

    else:
        print("Could not find descriptors in one of the images.")

cv2.destroyAllWindows()