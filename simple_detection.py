import cv2
import numpy as np

class SimpleCarDetector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = None
        self.car_count = 0
        self.car_counts_history = []
        
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
    
    def detect_cars(self, frame):
        """Simple car detection using color segmentation"""
        cars = []
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for colored objects (not white/gray road)
        lower_color = np.array([0, 50, 50])
        upper_color = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_color, np.array([180, 255, 255]))
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Car size range
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.8 < aspect_ratio < 2.0:  # Car aspect ratio
                    cars.append((x, y, w, h))
        
        return cars
    
    def process_frame(self, frame):
        """Process a single frame to detect and count cars"""
        # Detect cars
        cars = self.detect_cars(frame)
        
        # Update car count
        self.car_count = len(cars)
        self.car_counts_history.append(self.car_count)
        
        # Draw bounding boxes around detected cars
        for i, (x, y, w, h) in enumerate(cars):
            # Draw green bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            # Add car number label
            cv2.putText(frame, f"Car {i+1}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Display car count on frame
        cv2.putText(frame, f"Cars Detected: {self.car_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        
        return frame
    
    def run(self):
        """Run the car detection system"""
        if not self.start_video_capture():
            return
        
        print("Starting car detection...")
        print("Press 'q' to quit during video playback")
        
        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("End of video stream")
                    break
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Show video
                cv2.imshow('Simple Car Detection', processed_frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
        
        finally:
            self.cap.release()
            cv2.destroyAllWindows()
        
        # Print statistics
        if self.car_counts_history:
            avg_cars = sum(self.car_counts_history) / len(self.car_counts_history)
            max_cars = max(self.car_counts_history)
            print(f"\n=== DETECTION COMPLETE ===")
            print(f"Average cars per frame: {avg_cars:.2f}")
            print(f"Maximum cars detected: {max_cars}")
            print(f"Total frames processed: {len(self.car_counts_history)}")

def main():
    # Generate simulation first
    print("Generating simple simulation...")
    from simple_simulation import SimpleTrafficSimulator
    simulator = SimpleTrafficSimulator('simple_simulation.mp4', duration=30)  # 30 seconds
    simulator.generate_simulation()
    
    # Run detection
    print("\nRunning car detection...")
    detector = SimpleCarDetector('simple_simulation.mp4')
    detector.run()

if __name__ == "__main__":
    main()
