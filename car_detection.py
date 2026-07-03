import cv2
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class TrafficSignalManagement:
    def __init__(self, video_path=None, is_real_footage=False, display=True, output_path=None):
        self.video_path = video_path
        self.is_real_footage = is_real_footage
        self.display = display
        self.output_path = output_path
        
        # Use background subtraction with parameters optimized for real footage
        if is_real_footage:
            # More history frames and lower threshold for real footage
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25)
        else:
            # Default parameters for simulation
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)
            
        self.car_count = 0
        self.car_count_history = []
        self.timestamps = []
        
    def process_video(self):
        if self.video_path is None:
            print("No video path provided")
            return
        
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video at {self.video_path}")
            return
        
        # Prepare writer if headless output is requested
        writer = None
        if not self.display and self.output_path:
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # Try multiple codecs for better compatibility
            codec_candidates = []
            lower_path = self.output_path.lower()
            if lower_path.endswith('.mp4'):
                codec_candidates = ['mp4v', 'avc1']
            else:
                codec_candidates = ['XVID', 'MJPG', 'mp4v']
            for codec in codec_candidates:
                try:
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    temp_writer = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
                    if temp_writer.isOpened():
                        writer = temp_writer
                        break
                    else:
                        temp_writer.release()
                except Exception:
                    pass
        # Prepare frame dump directory if no writer is available in headless mode
        frame_dump_dir = None
        if not self.display and self.output_path and writer is None:
            import os
            frame_dump_dir = os.path.splitext(self.output_path)[0] + "_frames"
            os.makedirs(frame_dump_dir, exist_ok=True)
        
        frame_index = 0
            
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process the frame
            processed_frame = self.detect_cars(frame)
            
            if self.display:
                # Display the frame
                cv2.imshow('Traffic Management System', processed_frame)
                # Exit if 'q' is pressed
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            else:
                # Headless mode: write frames via writer or dump as images
                if writer is not None:
                    writer.write(processed_frame)
                elif frame_dump_dir is not None:
                    import os
                    cv2.imwrite(os.path.join(frame_dump_dir, f"frame_{frame_index:06d}.jpg"), processed_frame)
                frame_index += 1
                
        cap.release()
        if writer is not None:
            writer.release()
        if self.display:
            cv2.destroyAllWindows()
        
        # Plot the car count history
        self.plot_car_count()
        
    def detect_cars(self, frame):
        # Define region of interest (ROI) - bottom half of the frame
        height, width = frame.shape[:2]
        roi_vertices = np.array([[(0, height), (0, height//2), (width, height//2), (width, height)]], dtype=np.int32)
        
        # Create a mask for ROI
        mask = np.zeros((height, width), dtype=np.uint8)
        cv2.fillPoly(mask, roi_vertices, 255)
        
        # Pre-process frame for better detection in real footage
        if self.is_real_footage:
            # Apply Gaussian blur to reduce noise
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
            
            # Enhance contrast
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            enhanced_lab = cv2.merge((cl, a, b))
            frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Apply ROI mask to foreground mask
        masked_fg = cv2.bitwise_and(fg_mask, mask)
        
        # Apply morphological operations to reduce noise and fill gaps
        kernel = np.ones((5, 5), np.uint8)
        masked_fg = cv2.morphologyEx(masked_fg, cv2.MORPH_OPEN, kernel)
        masked_fg = cv2.morphologyEx(masked_fg, cv2.MORPH_CLOSE, kernel)
        
        # Apply threshold to reduce noise
        _, thresh = cv2.threshold(masked_fg, 200, 255, cv2.THRESH_BINARY)
        
        # Find contours of moving objects
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size to identify cars
        min_contour_area = 400 if self.is_real_footage else 500  # Lower threshold for real footage
        max_contour_area = 15000 if self.is_real_footage else 10000  # Upper threshold to filter out large noise
        car_contours = [cnt for cnt in contours if min_contour_area < cv2.contourArea(cnt) < max_contour_area]
        
        # Draw rectangles around detected cars
        for contour in car_contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Update car count
        current_car_count = len(car_contours)
        self.car_count = current_car_count
        self.car_count_history.append(current_car_count)
        self.timestamps.append(datetime.now())
        
        # Display car count
        cv2.putText(frame, f'Car Count: {current_car_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Draw ROI
        cv2.polylines(frame, roi_vertices, True, (255, 0, 0), 2)
        
        return frame
        
    def plot_car_count(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.timestamps, self.car_count_history, 'b-')
        plt.title('Car Count Over Time')
        plt.xlabel('Time')
        plt.ylabel('Number of Cars')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('car_count_history.png')
        if self.display:
            plt.show()
        else:
            plt.close()