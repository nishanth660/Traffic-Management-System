import cv2
import numpy as np
import random
import os

class TrafficSimulator:
    def __init__(self, output_path='traffic_simulation.mp4', duration=30, resolution=(640, 480)):
        self.output_path = output_path
        self.duration = duration  # in seconds
        self.width, self.height = resolution
        self.fps = 30
        
        # Car images (we'll use simple rectangles for this simulation)
        self.car_width = 40
        self.car_height = 20
        self.car_colors = [
            (0, 0, 255),    # Red
            (0, 255, 0),    # Green
            (255, 0, 0),    # Blue
            (0, 255, 255),  # Yellow
            (255, 0, 255),  # Magenta
        ]
        
        # Road parameters
        self.road_y = self.height // 2
        self.road_height = 100
        
        # Cars data structure: [x, y, speed, color_index]
        self.cars = []
        
        # Video writer
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = None
    
    def create_background(self):
        """Create a background with a road"""
        bg = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255  # White background
        
        # Draw road (gray)
        cv2.rectangle(
            bg,
            (0, self.road_y - self.road_height//2),
            (self.width, self.road_y + self.road_height//2),
            (100, 100, 100),
            -1
        )
        
        # Draw road markings (white dashed line)
        for x in range(0, self.width, 30):
            cv2.line(
                bg,
                (x, self.road_y),
                (x + 20, self.road_y),
                (255, 255, 255),
                2
            )
        
        return bg
    
    def add_random_car(self):
        """Add a new car at random position on the left side"""
        if random.random() < 0.1:  # 10% chance to add a car each frame
            car = [
                0,  # x position (start from left)
                self.road_y - self.road_height//4 + random.randint(-10, 10),  # y position with slight variation
                random.randint(2, 5),  # speed
                random.randint(0, len(self.car_colors) - 1)  # color index
            ]
            self.cars.append(car)
    
    def update_cars(self):
        """Update positions of all cars"""
        # Move cars
        for car in self.cars:
            car[0] += car[2]  # Update x position based on speed
        
        # Remove cars that have gone off-screen
        self.cars = [car for car in self.cars if car[0] < self.width]
    
    def draw_cars(self, frame):
        """Draw all cars on the frame"""
        for car in self.cars:
            x, y, _, color_idx = car
            color = self.car_colors[color_idx]
            
            # Draw car as a rectangle
            cv2.rectangle(
                frame,
                (int(x), int(y - self.car_height//2)),
                (int(x + self.car_width), int(y + self.car_height//2)),
                color,
                -1
            )
            
            # Draw windows (black)
            cv2.rectangle(
                frame,
                (int(x + 5), int(y - self.car_height//2 + 3)),
                (int(x + self.car_width - 5), int(y + self.car_height//2 - 3)),
                (0, 0, 0),
                1
            )
        
        # Display car count
        cv2.putText(
            frame,
            f"Cars: {len(self.cars)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2
        )
        
        return frame
    
    def generate_simulation(self):
        """Generate the traffic simulation video"""
        # Initialize video writer
        self.out = cv2.VideoWriter(
            self.output_path,
            self.fourcc,
            self.fps,
            (self.width, self.height)
        )
        
        # Generate frames
        total_frames = self.duration * self.fps
        
        for _ in range(total_frames):
            # Create background
            frame = self.create_background()
            
            # Add random cars
            self.add_random_car()
            
            # Update car positions
            self.update_cars()
            
            # Draw cars on frame
            frame = self.draw_cars(frame)
            
            # Write frame to video
            self.out.write(frame)
        
        # Release resources
        self.out.release()
        print(f"Simulation video saved to {self.output_path}")


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath('traffic_simulation.mp4'))
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate simulation
    simulator = TrafficSimulator(duration=20)
    simulator.generate_simulation()