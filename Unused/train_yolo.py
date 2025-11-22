from ultralytics import YOLO
from roboflow import Roboflow
import os

# 🛑 WINDOWS SAFETY GUARD: Everything must be indented under this line!
if __name__ == '__main__':

    # --- 1. DOWNLOAD THE DATASET ---
    # We moved this INSIDE the block so workers don't run it.
    
    # ⚠️ PASTE YOUR PRIVATE KEY HERE ⚠️
    api_key = "YzizvGDTGn3ycUp3BuOR" 
    
    # Your Project Details (I filled these in from your error message)
    workspace = "blackjack-p7elo"
    project_name = "blackjack-final-site-a-36w34"
    version_number = 3
    
    # Initialize Roboflow
    rf = Roboflow(api_key="YzizvGDTGn3ycUp3BuOR")
    project = rf.workspace("blackjack-p7elo").project("blackjack-final-site-a-36w34")
    version = project.version(1)
    dataset = version.download("yolov8")

    # -------------------------------------------------

    # --- 2. LOAD THE PREVIOUS BRAIN ---
    # Use your v13 brain as the starting point
    path_to_old_brain = 'runs/detect/universal_blackjack_v13/weights/best.pt'

    if os.path.exists(path_to_old_brain):
        print(f"✅ Loading previous brain: {path_to_old_brain}")
        model = YOLO(path_to_old_brain)
    else:
        print("⚠️ Old brain not found. Starting fresh with yolov8n.pt")
        model = YOLO('yolov8n.pt')

    # --- 3. START TRAINING ---
    print("Starting Training...")
    
    results = model.train(
        data=f"{dataset.location}/data.yaml", 
        epochs=50, 
        imgsz=640, 
        batch=16, 
        device=0,       # Use your 2070 Super
        workers=8,      # Fast loading
        name='final_fine_tuned_model'
    )