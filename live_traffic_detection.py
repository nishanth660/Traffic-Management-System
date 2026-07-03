import cv2
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class LiveTrafficDetection:
    def __init__(self):
        # Create output directory
        if not os.path.exists('output'):
            os.makedirs('output')
        
        # Video parameters
        self.width = 800
        self.height = 600
        self.fps = 30
        self.duration = 30  # seconds
        
        # Car detection parameters
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=50)
        self.min_contour_area = 500
        self.max_contour_area = 10000
        
        # Traffic simulation parameters
        self.road_width = 500
        self.road_start_x = (self.width - self.road_width) // 2
        self.lane_width = self.road_width // 3
        
        # Car parameters
        self.car_width = 60
        self.car_height = 100
        self.cars = []
        self.car_speeds = []
        self.car_colors = [
            (0, 0, 200),    # Red
            (200, 0, 0),    # Blue
            (0, 200, 0),    # Green
            (200, 200, 0),  # Cyan
            (200, 0, 200),  # Magenta
            (0, 200, 200),  # Yellow
            (150, 150, 150) # Gray
        ]
        
        # Initialize cars
        self.initialize_cars()
        
        # Car count history
        self.car_count_history = []
        self.frame_count = 0
        
    def initialize_cars(self):
        # Initialize cars in each lane with different speeds
        # Left lane
        for i in range(6):
            y = i * (self.car_height + 10) - 300  # Start some cars off-screen
            x = self.road_start_x + 10
            color = self.car_colors[i % len(self.car_colors)]
            self.cars.append([x, y, self.car_width, self.car_height, color])
            self.car_speeds.append(np.random.randint(3, 7))
        
        # Middle lane
        for i in range(7):
            y = i * (self.car_height + 5) - 400  # Start some cars off-screen
            x = self.road_start_x + self.lane_width + 10
            color = self.car_colors[(i + 2) % len(self.car_colors)]
            self.cars.append([x, y, self.car_width, self.car_height, color])
            self.car_speeds.append(np.random.randint(5, 10))
        
        # Right lane
        for i in range(6):
            y = i * (self.car_height + 15) - 200  # Start some cars off-screen
            x = self.road_start_x + 2 * self.lane_width + 10
            color = self.car_colors[(i + 4) % len(self.car_colors)]
            self.cars.append([x, y, self.car_width, self.car_height, color])
            self.car_speeds.append(np.random.randint(2, 6))
    
    def create_frame(self):
        # Create a blank frame
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 220  # Light gray background
        
        # Draw road
        cv2.rectangle(frame, (self.road_start_x, 0), 
                     (self.road_start_x + self.road_width, self.height), 
                     (80, 80, 80), -1)
        
        # Draw lane markings
        for i in range(1, 3):
            lane_x = self.road_start_x + i * self.lane_width
            # Dashed lines
            for j in range(0, self.height, 30):
                cv2.line(frame, (lane_x, j), (lane_x, j + 20), (200, 200, 200), 2)
        
        # Add elevated road/bridge at the top
        cv2.rectangle(frame, (0, 50), (self.width, 100), (120, 120, 120), -1)
        
        # Add buildings on the sides
        # Left side
        cv2.rectangle(frame, (0, 0), (self.road_start_x-20, self.height), (150, 150, 170), -1)
        # Right side
        cv2.rectangle(frame, (self.road_start_x+self.road_width+20, 0), 
                     (self.width, self.height), (170, 150, 150), -1)
        
        # Update car positions
        for i, (x, y, w, h, color) in enumerate(self.cars):
            # Move car
            self.cars[i][1] += self.car_speeds[i]
            
            # If car goes off screen, reset to top
            if self.cars[i][1] > self.height:
                self.cars[i][1] = -self.car_height - np.random.randint(0, 100)
                # Randomize speed slightly
                self.car_speeds[i] = self.car_speeds[i] * 0.9 + np.random.randint(2, 6) * 0.1
        
        # Draw all cars
        for x, y, w, h, color in self.cars:
            if 0 <= y <= self.height:  # Only draw cars on screen
                # Car body
                cv2.rectangle(frame, (int(x), int(y)), (int(x+w), int(y+h)), color, -1)
                # Windshield
                cv2.rectangle(frame, (int(x+5), int(y+5)), (int(x+w-5), int(y+20)), (200, 200, 255), -1)
                # Rear window
                cv2.rectangle(frame, (int(x+5), int(y+h-20)), (int(x+w-5), int(y+h-5)), (200, 200, 255), -1)
        
        return frame
    
    def detect_cars(self, frame):
        # Create a copy for detection visualization
        result_frame = frame.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        opening = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and draw bounding boxes
        car_count = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_contour_area < area < self.max_contour_area:
                x, y, w, h = cv2.boundingRect(contour)
                # Filter by aspect ratio to better identify cars
                aspect_ratio = float(w) / h if h > 0 else 0
                if 0.2 < aspect_ratio < 1.5:  # Typical car aspect ratios
                    cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    car_count += 1
        
        # Add car count to the frame
        cv2.putText(result_frame, f'Cars: {car_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Add frame count
        self.frame_count += 1
        cv2.putText(result_frame, f'Frame: {self.frame_count}', (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Store car count for history
        self.car_count_history.append(car_count)
        
        return result_frame, car_count
    
    def run_live_detection(self):
        print("Starting live traffic detection simulation...")
        
        # Create a window
        cv2.namedWindow('Live Traffic Detection', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Live Traffic Detection', self.width, self.height)
        
        # Create a window for the car count graph
        plt.figure(figsize=(10, 4))
        
        start_time = time.time()
        try:
            while (time.time() - start_time) < self.duration:
                # Create a new frame
                frame = self.create_frame()
                
                # Detect cars
                result_frame, car_count = self.detect_cars(frame)
                
                # Display the frame
                cv2.imshow('Live Traffic Detection', result_frame)
                
                # Update car count graph every 10 frames
                if self.frame_count % 10 == 0:
                    plt.clf()
                    plt.plot(self.car_count_history[-100:] if len(self.car_count_history) > 100 else self.car_count_history)
                    plt.title('Car Count History')
                    plt.xlabel('Frame')
                    plt.ylabel('Number of Cars')
                    plt.grid(True)
                    plt.savefig('output/car_count_graph_live.png')
                
                # Break on ESC key
                if cv2.waitKey(int(1000/self.fps)) & 0xFF == 27:
                    break
                
        except KeyboardInterrupt:
            print("Simulation stopped by user")
        finally:
            # Clean up
            cv2.destroyAllWindows()
            
            # Save the final car count graph
            plt.figure(figsize=(10, 6))
            plt.plot(self.car_count_history)
            plt.title('Car Count History')
            plt.xlabel('Frame')
            plt.ylabel('Number of Cars')
            plt.grid(True)
            plt.savefig('output/car_count_history_final.png')
            
            print(f"Simulation completed. Processed {self.frame_count} frames.")
            print(f"Results saved to output folder.")

if __name__ == "__main__":
    detector = LiveTrafficDetection()
    detector.run_live_detection()