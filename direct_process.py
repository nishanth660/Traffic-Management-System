import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import base64
from PIL import Image
import io

def process_real_traffic_image():
    # Create output directory
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Load the image directly using OpenCV
    img = cv2.imread('real_traffic.jpg')
    if img is None:
        # If image doesn't exist, create a placeholder
        print("Creating placeholder traffic image...")
        img = np.zeros((600, 800, 3), dtype=np.uint8)
        # Draw a road with traffic
        cv2.rectangle(img, (200, 0), (600, 600), (80, 80, 80), -1)
        # Add cars
        for i in range(10):
            x = 250 + (i % 3) * 100
            y = 100 + (i // 3) * 120
            cv2.rectangle(img, (x, y), (x+80, y+40), (0, 0, 255), -1)
        cv2.imwrite('real_traffic.jpg', img)
    
    # Apply optimized detection for real traffic footage
    print("Processing traffic image...")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(blurred)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Apply morphological operations
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size and draw bounding boxes
    min_contour_area = 500
    max_contour_area = 10000
    car_count = 0
    result_frame = img.copy()
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_contour_area < area < max_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter by aspect ratio to better identify cars
            aspect_ratio = float(w) / h
            if 0.3 < aspect_ratio < 2.5:  # Typical car aspect ratios
                cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                car_count += 1
    
    # Add car count to the frame
    cv2.putText(result_frame, f'Cars: {car_count}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Save the result
    cv2.imwrite('output/detected_cars.jpg', result_frame)
    print(f"Detected {car_count} cars. Result saved to output/detected_cars.jpg")
    
    # Create a simple graph showing car count
    plt.figure(figsize=(10, 6))
    plt.bar(['Detected Cars'], [car_count], color='green')
    plt.title('Traffic Analysis Results')
    plt.ylabel('Number of Cars')
    plt.savefig('output/car_count_graph.png')
    print("Created car count graph: output/car_count_graph.png")
    
    return car_count

if __name__ == "__main__":
    process_real_traffic_image()