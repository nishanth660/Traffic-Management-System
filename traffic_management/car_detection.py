import cv2
import numpy as np
import time

class TrafficSignalManagement:
    def __init__(self, video_path=None):
        # Initialize the video capture
        self.video_path = video_path
        self.cap = None
        
        # Car detection parameters - using fullbody cascade as alternative
        self.car_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        
        # Background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        
        # Car counting variables
        self.car_count = 0
        self.previous_car_count = 0
        self.car_counts_history = []
        
        # Frame processing parameters
        self.frame_count = 0
        self.process_every_n_frames = 5  # Process every 5th frame for performance
        
        # Region of interest parameters (can be adjusted based on camera view)
        self.roi_vertices = None
    
    def start_video_capture(self):
        """Start the video capture from file or camera"""
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
        else:
            # Use default camera (0) if no video path is provided
            self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Could not open video source")
            return False
        
        # Get video dimensions
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Set default ROI as the bottom half of the frame
        self.roi_vertices = np.array([
            [0, height],
            [0, height//2],
            [width, height//2],
            [width, height]
        ], dtype=np.int32)
        
        return True
    
    def set_roi(self, vertices):
        """Set custom region of interest"""
        self.roi_vertices = np.array(vertices, dtype=np.int32)
    
    def apply_roi_mask(self, frame):
        """Apply region of interest mask to the frame"""
        mask = np.zeros_like(frame)
        cv2.fillPoly(mask, [self.roi_vertices], (255, 255, 255))
        masked_frame = cv2.bitwise_and(frame, mask)
        return masked_frame
    
    def detect_cars(self, frame):
        """Detect cars in the frame using improved hybrid approach"""
        # Convert frame to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply ROI mask
        masked_frame = self.apply_roi_mask(gray)
        
        # Use color-based detection for better accuracy
        cars = self.color_based_detection(frame)
        
        # If we don't detect enough cars, use motion detection
        if len(cars) < 5:
            motion_cars = self.motion_based_detection(masked_frame)
            cars.extend(motion_cars)
        
        # Remove overlapping detections
        cars = self.remove_overlapping_detections(cars)
        
        return cars
    
    def color_based_detection(self, frame):
        """Detect cars based on color segmentation"""
        cars = []
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define color ranges for different car colors
        color_ranges = [
            # Red cars
            ([0, 50, 50], [10, 255, 255]),
            ([170, 50, 50], [180, 255, 255]),
            # Blue cars
            ([100, 50, 50], [130, 255, 255]),
            # Green cars
            ([40, 50, 50], [80, 255, 255]),
            # Yellow cars
            ([20, 50, 50], [40, 255, 255]),
            # White/Light cars
            ([0, 0, 200], [180, 30, 255]),
            # Dark cars
            ([0, 0, 0], [180, 255, 50])
        ]
        
        for lower, upper in color_ranges:
            # Create mask for this color range
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            # Apply morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 15000:  # Car size range
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.4 < aspect_ratio < 3.0:  # Car aspect ratio
                        cars.append((x, y, w, h))
        
        return cars
    
    def motion_based_detection(self, masked_frame):
        """Enhanced motion-based detection"""
        cars = []
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(masked_frame)
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and aspect ratio
        for contour in contours:
            area = cv2.contourArea(contour)
            if 200 < area < 15000:  # Adjusted area threshold
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.4 < aspect_ratio < 3.0:  # Car aspect ratio
                    cars.append((x, y, w, h))
        
        return cars
    
    def template_matching_detection(self, gray_frame):
        """Use template matching to detect cars"""
        cars = []
        
        # Create a simple car template (rectangular shape)
        template = np.ones((40, 60), dtype=np.uint8) * 128
        template[5:35, 10:50] = 200  # Car body
        template[10:20, 15:45] = 255  # Windshield
        
        # Apply template matching
        result = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= 0.3)  # Lower threshold for more detections
        
        for pt in zip(*locations[::-1]):
            x, y = pt
            w, h = 60, 40
            cars.append((x, y, w, h))
        
        return cars
    
    def remove_overlapping_detections(self, cars):
        """Remove overlapping car detections using improved Non-Maximum Suppression"""
        if len(cars) <= 1:
            return cars
        
        # Convert to numpy array for easier processing
        cars_array = np.array(cars)
        
        # Calculate areas
        areas = cars_array[:, 2] * cars_array[:, 3]
        
        # Sort by area (largest first)
        indices = np.argsort(areas)[::-1]
        
        # Improved Non-Maximum Suppression
        keep = []
        while len(indices) > 0:
            # Take the largest remaining detection
            current = indices[0]
            keep.append(current)
            
            # Calculate IoU with remaining detections
            current_box = cars_array[current]
            remaining_boxes = cars_array[indices[1:]]
            
            # Calculate intersection over union
            ious = self.calculate_iou(current_box, remaining_boxes)
            
            # Remove detections with high overlap (stricter threshold)
            indices = indices[1:][ious < 0.2]  # Lower IoU threshold for better separation
        
        # Additional check: ensure minimum distance between car centers
        final_cars = []
        for i in keep:
            current_car = cars_array[i]
            x1, y1, w1, h1 = current_car
            center1 = (x1 + w1//2, y1 + h1//2)
            
            # Check if this car is too close to already selected cars
            too_close = False
            for final_car in final_cars:
                x2, y2, w2, h2 = final_car
                center2 = (x2 + w2//2, y2 + h2//2)
                
                # Calculate distance between centers
                distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
                
                # If too close, skip this car
                if distance < 50:  # Minimum distance threshold
                    too_close = True
                    break
            
            if not too_close:
                final_cars.append(current_car)
        
        return [tuple(car) for car in final_cars]
    
    def calculate_iou(self, box1, boxes2):
        """Calculate Intersection over Union between one box and multiple boxes"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = boxes2[:, 0], boxes2[:, 1], boxes2[:, 2], boxes2[:, 3]
        
        # Calculate intersection coordinates
        x_left = np.maximum(x1, x2)
        y_top = np.maximum(y1, y2)
        x_right = np.minimum(x1 + w1, x2 + w2)
        y_bottom = np.minimum(y1 + h1, y2 + h2)
        
        # Calculate intersection area
        intersection = np.maximum(0, x_right - x_left) * np.maximum(0, y_bottom - y_top)
        
        # Calculate union area
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        # Calculate IoU
        iou = intersection / (union + 1e-6)  # Add small epsilon to avoid division by zero
        
        return iou
    
    def process_frame(self, frame):
        """Process a single frame to detect and count cars"""
        # Increment frame counter
        self.frame_count += 1
        
        # Process every frame for better detection
        # Detect cars
        cars = self.detect_cars(frame)
        
        # Update car count
        self.previous_car_count = self.car_count
        self.car_count = len(cars)
        self.car_counts_history.append(self.car_count)
        
        # Draw bounding boxes around detected cars with thicker lines
        for i, (x, y, w, h) in enumerate(cars):
            # Draw green bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
            
            # Add car number label
            cv2.putText(
                frame,
                f"Car {i+1}",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        # Display car count on frame with better visibility
        cv2.putText(
            frame,
            f"Cars Detected: {self.car_count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )
        
        # Add frame counter
        cv2.putText(
            frame,
            f"Frame: {self.frame_count}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        # Draw ROI on frame
        cv2.polylines(frame, [self.roi_vertices], True, (255, 0, 0), 2)
        
        return frame
    
    def run(self):
        """Run the traffic management system"""
        if not self.start_video_capture():
            return
        
        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                
                if not ret:
                    print("End of video stream")
                    break
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                # Display the processed frame
                cv2.imshow('Traffic Management System', processed_frame)
                
                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Simulate real-time processing
                time.sleep(0.01)
        
        finally:
            # Release resources
            self.cap.release()
            cv2.destroyAllWindows()
    


if __name__ == "__main__":
    # Example usage with a video file
    # Replace 'traffic_video.mp4' with your video file or remove the parameter to use webcam
    traffic_system = TrafficSignalManagement('traffic_simulation.mp4')
    traffic_system.run()