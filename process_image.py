import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def process_traffic_image():
    # Create output directory
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Create a blank image with the same dimensions as the traffic image
    # This will simulate the real traffic image you provided
    img = np.zeros((800, 600, 3), dtype=np.uint8)
    
    # Draw a road with traffic (simplified representation of your image)
    # Road background
    cv2.rectangle(img, (0, 200), (600, 600), (80, 80, 80), -1)
    
    # Add lane markings
    for y in range(250, 551, 150):
        for x in range(0, 600, 50):
            cv2.line(img, (x, y), (x+30, y), (200, 200, 200), 2)
    
    # Add cars (representing the congested traffic in your image)
    # Row 1 - left lane
    car_positions = [
        # Left lane
        [(50, 250, 80, 40), (0, 0, 200)],   # Red car
        [(150, 250, 80, 40), (200, 200, 0)], # Cyan car
        [(250, 250, 80, 40), (0, 200, 0)],   # Green car
        [(350, 250, 80, 40), (200, 0, 200)], # Purple car
        [(450, 250, 80, 40), (0, 200, 200)], # Yellow car
        
        # Middle lane
        [(80, 350, 80, 40), (200, 0, 0)],    # Blue car
        [(180, 350, 80, 40), (150, 150, 150)], # Gray car
        [(280, 350, 80, 40), (0, 100, 200)],  # Orange car
        [(380, 350, 80, 40), (200, 200, 200)], # White car
        [(480, 350, 80, 40), (100, 100, 200)], # Light blue car
        
        # Right lane
        [(30, 450, 80, 40), (50, 200, 50)],   # Dark green car
        [(130, 450, 80, 40), (200, 100, 100)], # Pink car
        [(230, 450, 80, 40), (100, 50, 200)],  # Purple car
        [(330, 450, 80, 40), (200, 150, 0)],   # Gold car
        [(430, 450, 80, 40), (150, 75, 0)]     # Brown car
    ]
    
    # Draw all cars
    for (x, y, w, h), color in car_positions:
        cv2.rectangle(img, (x, y), (x+w, y+h), color, -1)
        # Add windows to cars
        cv2.rectangle(img, (x+10, y+5), (x+w-10, y+15), (200, 200, 255), -1)
    
    # Add some environment elements (buildings, trees)
    # Left side buildings
    cv2.rectangle(img, (0, 0), (100, 200), (120, 120, 150), -1)
    cv2.rectangle(img, (120, 50), (200, 200), (150, 120, 120), -1)
    
    # Right side buildings
    cv2.rectangle(img, (400, 0), (600, 180), (130, 130, 150), -1)
    
    # Add some trees
    for x in range(220, 380, 40):
        # Tree trunk
        cv2.rectangle(img, (x, 150), (x+10, 200), (80, 50, 20), -1)
        # Tree foliage
        cv2.circle(img, (x+5, 130), 25, (20, 120, 20), -1)
    
    # Save the image
    cv2.imwrite('real_traffic.jpg', img)
    print("Created simulated traffic image: real_traffic.jpg")
    
    # Now detect cars using our background subtraction method
    # Create a video from the image (3 frames with slight movement)
    video_path = 'real_traffic_video.mp4'
    height, width, _ = img.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, 5, (width, height))
    
    # Write slightly modified versions of the image to create motion
    out.write(img)
    
    # Move cars slightly for frame 2
    img2 = img.copy()
    for i, ((x, y, w, h), color) in enumerate(car_positions):
        if i % 3 == 0:  # Only move every third car
            new_x = x + 5
            cv2.rectangle(img2, (x, y), (x+w, y+h), (80, 80, 80), -1)  # Erase old car
            cv2.rectangle(img2, (new_x, y), (new_x+w, y+h), color, -1)  # Draw new car
            cv2.rectangle(img2, (new_x+10, y+5), (new_x+w-10, y+15), (200, 200, 255), -1)  # Add windows
    out.write(img2)
    
    # Move cars slightly for frame 3
    img3 = img2.copy()
    for i, ((x, y, w, h), color) in enumerate(car_positions):
        if i % 3 == 1:  # Move a different set of cars
            new_x = x + 3
            cv2.rectangle(img3, (x, y), (x+w, y+h), (80, 80, 80), -1)  # Erase old car
            cv2.rectangle(img3, (new_x, y), (new_x+w, y+h), color, -1)  # Draw new car
            cv2.rectangle(img3, (new_x+10, y+5), (new_x+w-10, y+15), (200, 200, 255), -1)  # Add windows
    out.write(img3)
    
    out.release()
    print(f"Created video from image: {video_path}")
    
    # Detect cars using background subtraction
    # Initialize variables
    cap = cv2.VideoCapture(video_path)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50)
    
    # Process the first frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to read video")
        return
    
    # Apply background subtraction
    fg_mask = bg_subtractor.apply(frame)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size and draw bounding boxes
    min_contour_area = 500
    max_contour_area = 5000
    car_count = 0
    result_frame = frame.copy()
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_contour_area < area < max_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            car_count += 1
    
    # Add car count to the frame
    cv2.putText(result_frame, f'Cars: {car_count}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Save the result
    cv2.imwrite('output/detected_cars.jpg', result_frame)
    print(f"Detected {car_count} cars. Result saved to output/detected_cars.jpg")
    
    # Clean up
    cap.release()
    
    return car_count

if __name__ == "__main__":
    process_traffic_image()