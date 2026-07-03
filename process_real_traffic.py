import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def process_real_traffic():
    # Create output directory
    if not os.path.exists('output'):
        os.makedirs('output')
    
    # Create a blank image that resembles the traffic image you provided
    img_height, img_width = 600, 800
    img = np.ones((img_height, img_width, 3), dtype=np.uint8) * 220  # Light gray background
    
    # Draw road
    road_width = 500
    road_start_x = (img_width - road_width) // 2
    cv2.rectangle(img, (road_start_x, 0), (road_start_x + road_width, img_height), (80, 80, 80), -1)
    
    # Draw lane markings
    lane_width = road_width // 3
    for i in range(1, 3):
        lane_x = road_start_x + i * lane_width
        cv2.line(img, (lane_x, 0), (lane_x, img_height), (200, 200, 200), 2)
    
    # Add cars to each lane (simulating the congested traffic in your image)
    car_colors = [
        (0, 0, 200),    # Red
        (200, 0, 0),    # Blue
        (0, 200, 0),    # Green
        (200, 200, 0),  # Cyan
        (200, 0, 200),  # Magenta
        (0, 200, 200),  # Yellow
        (150, 150, 150) # Gray
    ]
    
    # Add cars to each lane
    car_width, car_height = 60, 100
    cars = []
    
    # Left lane
    for i in range(6):
        y = i * (car_height + 10)
        x = road_start_x + 10
        color = car_colors[i % len(car_colors)]
        cars.append(((x, y, car_width, car_height), color))
    
    # Middle lane
    for i in range(7):
        y = i * (car_height + 5) + 20
        x = road_start_x + lane_width + 10
        color = car_colors[(i + 2) % len(car_colors)]
        cars.append(((x, y, car_width, car_height), color))
    
    # Right lane
    for i in range(6):
        y = i * (car_height + 15) + 30
        x = road_start_x + 2 * lane_width + 10
        color = car_colors[(i + 4) % len(car_colors)]
        cars.append(((x, y, car_width, car_height), color))
    
    # Draw all cars
    for (x, y, w, h), color in cars:
        # Car body
        cv2.rectangle(img, (x, y), (x+w, y+h), color, -1)
        # Windshield
        cv2.rectangle(img, (x+5, y+5), (x+w-5, y+20), (200, 200, 255), -1)
        # Rear window
        cv2.rectangle(img, (x+5, y+h-20), (x+w-5, y+h-5), (200, 200, 255), -1)
    
    # Add elevated road/bridge at the top
    cv2.rectangle(img, (0, 50), (img_width, 100), (120, 120, 120), -1)
    
    # Add buildings on the sides
    # Left side
    cv2.rectangle(img, (0, 0), (road_start_x-20, img_height), (150, 150, 170), -1)
    # Right side
    cv2.rectangle(img, (road_start_x+road_width+20, 0), (img_width, img_height), (170, 150, 150), -1)
    
    # Save the image
    cv2.imwrite('real_traffic.jpg', img)
    print("Created simulated traffic image: real_traffic.jpg")
    
    # Now detect cars using our optimized method for real traffic
    # Apply preprocessing to enhance car detection
    processed_img = img.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding to identify potential car regions
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size and draw bounding boxes
    min_contour_area = 1000  # Adjusted for car size
    max_contour_area = 15000  # Adjusted for car size
    car_count = 0
    result_frame = img.copy()
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_contour_area < area < max_contour_area:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter by aspect ratio to better identify cars
            aspect_ratio = float(w) / h
            if 0.2 < aspect_ratio < 1.5:  # Typical car aspect ratios
                cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                car_count += 1
    
    # Add car count to the frame
    cv2.putText(result_frame, f'Cars: {car_count}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Save the result
    cv2.imwrite('output/detected_cars.jpg', result_frame)
    print(f"Detected {car_count} cars. Result saved to output/detected_cars.jpg")
    
    return car_count

if __name__ == "__main__":
    process_real_traffic()