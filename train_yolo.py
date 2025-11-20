from ultralytics import YOLO
from roboflow import Roboflow
import os

# 🛑 THIS LINE IS REQUIRED ON WINDOWS 🛑
if __name__ == '__main__':
    
    # --- 1. DOWNLOAD DATASET ---
    # (Paste your Roboflow snippet here if you haven't downloaded v2 yet)
    # rf = Roboflow(api_key="...")
    # ...
    
    # Since you already have the folder "247-Blackjack-Custom-2", we can point to it directly:
    dataset_folder = "247-Blackjack-Custom-2"


    # --- 2. LOAD THE PREVIOUS BRAIN ---
    path_to_old_brain = 'runs/detect/universal_blackjack_v13/weights/best.pt'

    print(f"Loading brain from: {path_to_old_brain}...")
    
    try:
        model = YOLO(path_to_old_brain)
    except Exception as e:
        print(f"Error loading brain: {e}")
        # Fallback to base model if path is wrong
        print("Falling back to yolov8n.pt")
        model = YOLO('yolov8n.pt')

    # --- 3. START TRAINING ---
    print("Starting Fine-Tuning...")
    
    # We use 'workers=8' which causes the crash if the 'if __name__' block is missing!
    results = model.train(
        data=f"{dataset_folder}/data.yaml", 
        epochs=50, 
        imgsz=640, 
        batch=16, 
        device=0, 
        workers=8, 
        name='final_fine_tuned_model'
    )