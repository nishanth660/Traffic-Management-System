import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import argparse

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our car detection module
from car_detection import TrafficSignalManagement

def main():
    # Create output directory if it doesn't exist
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Path to save the real traffic image
    image_path = 'real_traffic.jpg'
    
    # Check if the image exists
    if not os.path.exists(image_path):
        print(f"Please place your real traffic image at {image_path}")
        return
    
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to read image from {image_path}")
        return
    
    # Create a video from the image (repeat the image for 5 seconds at 30fps)
    video_path = 'real_traffic_video.mp4'
    height, width, _ = image.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 30, (width, height))
    
    # Write the same image multiple times to create a video
    for _ in range(150):  # 5 seconds at 30fps
        out.write(image)
    out.release()
    
    print(f"Created video from image: {video_path}")
    
    # Initialize car detection with real-footage optimization
    detector = TrafficSignalManagement(video_path, is_real_footage=True)
    
    # Process the video
    detector.process_video()
    
    # Display results
    print("Car detection completed. Results saved to car_count_history.png")
    
    # Save the processed frame with detections
    processed_frame = detector.get_last_processed_frame()
    if processed_frame is not None:
        cv2.imwrite('output/processed_real_traffic.jpg', processed_frame)
        print("Processed image saved to output/processed_real_traffic.jpg")

if __name__ == "__main__":
    main()