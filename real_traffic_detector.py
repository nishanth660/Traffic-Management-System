import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import time

class RealTrafficDetector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = None
        self.car_count = 0
        self.car_counts_history = []
        self.frame_count = 0
        
        # Background subtractor for motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, 
            varThreshold=50, 
            detectShadows=True
        )
        
        # Morphological kernel for noise reduction
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        
        # Car detection parameters
        self.min_contour_area = 800
        self.max_contour_area = 20000
        self.min_aspect_ratio = 0.3
        self.max_aspect_ratio = 2.0
        
    def start_video_capture(self):
        """Start video capture from file"""
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            return False
        
        # Get video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video loaded: {self.width}x{self.height}, {self.fps} FPS, {self.total_frames} frames")
        return True
    
    def preprocess_frame(self, frame):
        """Preprocess frame for better car detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply histogram equalization to improve contrast
        equalized = cv2.equalizeHist(blurred)
        
        return equalized
    
    def detect_cars_motion(self, frame):
        """Detect cars using motion detection"""
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)
        
        # Apply morphological operations to clean up the mask
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cars = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_contour_area < area < self.max_contour_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                # Filter by aspect ratio and size
                if (self.min_aspect_ratio < aspect_ratio < self.max_aspect_ratio and 
                    w > 30 and h > 30):
                    cars.append((x, y, w, h))
        
        return cars
    
    def detect_cars_contour(self, frame):
        """Detect cars using contour analysis"""
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cars = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_contour_area < area < self.max_contour_area:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                if (self.min_aspect_ratio < aspect_ratio < self.max_aspect_ratio and 
                    w > 30 and h > 30):
                    cars.append((x, y, w, h))
        
        return cars
    
    def process_frame(self, frame):
        """Process a single frame to detect cars"""
        self.frame_count += 1
        
        # Preprocess frame
        processed_frame = self.preprocess_frame(frame)
        
        # Try motion detection first
        cars_motion = self.detect_cars_motion(processed_frame)
        
        # Try contour detection as backup
        cars_contour = self.detect_cars_contour(processed_frame)
        
        # Use the method that detects more cars (or motion if similar)
        if len(cars_motion) >= len(cars_contour):
            cars = cars_motion
            method = "Motion"
        else:
            cars = cars_contour
            method = "Contour"
        
        # Update car count
        self.car_count = len(cars)
        self.car_counts_history.append(self.car_count)
        
        # Draw bounding boxes
        result_frame = frame.copy()
        for (x, y, w, h) in cars:
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add information overlay
        cv2.putText(result_frame, f'Cars: {self.car_count}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(result_frame, f'Method: {method}', (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(result_frame, f'Frame: {self.frame_count}/{self.total_frames}', (10, 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return result_frame
    
    def run_detection(self, show_video=True, save_frames=False):
        """Run car detection on the video"""
        if not self.start_video_capture():
            return
        
        # Create output directory if saving frames
        if save_frames:
            os.makedirs('output', exist_ok=True)
        
        print(f"Starting car detection simulation...")
        print(f"Video: {self.width}x{self.height}, {self.fps} FPS, {self.total_frames} frames")
        print("Press 'q' to quit during video playback")
        
        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("End of video stream")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Show video if requested
                if show_video:
                    cv2.imshow('Real Traffic Car Detection', processed_frame)
                    if cv2.waitKey(30) & 0xFF == ord('q'):  # Increased delay for better viewing
                        break
                
                # Save frame if requested
                if save_frames and self.frame_count % 10 == 0:  # Save every 10th frame
                    cv2.imwrite(f'output/frame_{self.frame_count:06d}.jpg', processed_frame)
                
                # Print progress for each frame
                print(f"Frame {self.frame_count}/{self.total_frames}: Detected {self.car_count} cars")
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
    
    def plot_car_count_history(self):
        """Plot car count history"""
        plt.figure(figsize=(12, 6))
        plt.plot(self.car_counts_history)
        plt.title('Car Count Over Time - Real Traffic Footage')
        plt.xlabel('Frame Number')
        plt.ylabel('Number of Cars Detected')
        plt.grid(True, alpha=0.3)
        
        # Add statistics
        avg_cars = np.mean(self.car_counts_history)
        max_cars = np.max(self.car_counts_history)
        plt.axhline(y=avg_cars, color='r', linestyle='--', alpha=0.7, label=f'Average: {avg_cars:.1f}')
        plt.axhline(y=max_cars, color='g', linestyle='--', alpha=0.7, label=f'Maximum: {max_cars}')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig('output/real_traffic_car_count.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\nCar Detection Statistics:")
        print(f"Average cars per frame: {avg_cars:.2f}")
        print(f"Maximum cars detected: {max_cars}")
        print(f"Total frames processed: {len(self.car_counts_history)}")
        print(f"Total unique car detections: {sum(self.car_counts_history)}")

def main():
    # Check if video file exists
    video_path = "real_traffic_video.mp4"
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} not found!")
        print("Please make sure the video file is in the current directory.")
        return
    
    # Create detector
    detector = RealTrafficDetector(video_path)
    
    # Run detection simulation
    detector.run_detection(show_video=True, save_frames=True)
    
    # Print final statistics
    if detector.car_counts_history:
        avg_cars = np.mean(detector.car_counts_history)
        max_cars = np.max(detector.car_counts_history)
        print(f"\n=== DETECTION SIMULATION COMPLETE ===")
        print(f"Average cars per frame: {avg_cars:.2f}")
        print(f"Maximum cars detected: {max_cars}")
        print(f"Total frames processed: {len(detector.car_counts_history)}")
        print(f"Total car detections: {sum(detector.car_counts_history)}")
        print("Check 'output' folder for saved frames.")

if __name__ == "__main__":
    main()
