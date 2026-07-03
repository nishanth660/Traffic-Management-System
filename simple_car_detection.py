import cv2
import numpy as np

def detect_cars_in_video(video_path):
    """Simple car detection simulation"""
    print("=== CAR DETECTION SIMULATION ===")
    print(f"Processing video: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    # Get video info
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video Info: {width}x{height}, {fps} FPS, {total_frames} frames")
    print("Starting detection simulation...")
    print("-" * 50)
    
    frame_count = 0
    total_cars = 0
    
    # Background subtractor for motion detection
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply background subtraction
        fg_mask = bg_subtractor.apply(gray)
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Count cars based on contour area and aspect ratio
        car_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 15000:  # Filter by area
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                if 0.3 < aspect_ratio < 2.0:  # Filter by aspect ratio
                    car_count += 1
                    # Draw bounding box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        total_cars += car_count
        
        # Add text overlay
        cv2.putText(frame, f'Frame {frame_count}/{total_frames}', (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f'Cars Detected: {car_count}', (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Show frame
        cv2.imshow('Car Detection Simulation', frame)
        
        # Print frame info
        print(f"Frame {frame_count:2d}: Detected {car_count} cars")
        
        # Wait for key press or auto-advance
        if cv2.waitKey(500) & 0xFF == ord('q'):  # 500ms delay for better viewing
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    # Print summary
    print("-" * 50)
    print("=== SIMULATION COMPLETE ===")
    print(f"Total frames processed: {frame_count}")
    print(f"Total car detections: {total_cars}")
    print(f"Average cars per frame: {total_cars/frame_count:.2f}")
    print("Detection simulation finished!")

if __name__ == "__main__":
    detect_cars_in_video("real_traffic_video.mp4")
