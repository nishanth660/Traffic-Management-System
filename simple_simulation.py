import cv2
import numpy as np
import random

class SimpleTrafficSimulator:
    def __init__(self, output_path='simple_simulation.mp4', duration=10, fps=30):
        self.output_path = output_path
        self.duration = duration
        self.fps = fps
        self.frame_width = 800
        self.frame_height = 600
        self.cars = []
        
    def generate_simulation(self):
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (self.frame_width, self.frame_height))
        
        # Generate frames
        for frame_idx in range(self.duration * self.fps):
            # Create a frame with road
            frame = self.create_road_frame()
            
            # Add cars at fixed intervals (no random overlap)
            if frame_idx % 60 == 0 and len(self.cars) < 4:  # Add car every 2 seconds, max 4 cars
                self.add_car()
                
            # Update and draw cars
            self.update_cars()
            self.draw_cars(frame)
            
            # Add frame info
            cv2.putText(frame, f'Frame: {frame_idx}/{self.duration * self.fps}', (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(frame, f'Cars: {len(self.cars)}', (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Write frame to video
            out.write(frame)
            
            # Display progress
            if frame_idx % self.fps == 0:
                print(f"Generating simulation: {frame_idx//(self.fps)}/{self.duration} seconds")
        
        # Release resources
        out.release()
        print(f"Simulation video saved to {self.output_path}")
        
    def create_road_frame(self):
        # Create a blank frame
        frame = np.ones((self.frame_height, self.frame_width, 3), dtype=np.uint8) * 255
        
        # Draw road
        road_y = self.frame_height // 2
        road_height = 200
        cv2.rectangle(frame, (0, road_y - road_height//2), (self.frame_width, road_y + road_height//2), (100, 100, 100), -1)
        
        # Draw lane markings
        lane_y = road_y
        for x in range(0, self.frame_width, 50):
            cv2.line(frame, (x, lane_y), (x + 30, lane_y), (255, 255, 255), 5)
            
        return frame
        
    def add_car(self):
        # Fixed car properties
        car_width = 50
        car_height = 35
        car_x = -car_width
        car_speed = 8
        car_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        
        # Fixed lane positions - no random variation
        if len(self.cars) == 0:
            car_y = self.frame_height // 2 - 60  # Top lane
        elif len(self.cars) == 1:
            car_y = self.frame_height // 2 - 20  # Upper middle lane
        elif len(self.cars) == 2:
            car_y = self.frame_height // 2 + 20  # Lower middle lane
        elif len(self.cars) == 3:
            car_y = self.frame_height // 2 + 60  # Bottom lane
        else:
            return  # Max 4 cars
        
        # Add the car
        self.cars.append({
            'x': car_x,
            'y': car_y,
            'width': car_width,
            'height': car_height,
            'speed': car_speed,
            'color': car_color
        })
        
    def update_cars(self):
        # Update car positions and remove cars that have left the frame
        updated_cars = []
        for car in self.cars:
            car['x'] += car['speed']
            if car['x'] < self.frame_width:
                updated_cars.append(car)
        self.cars = updated_cars
        
    def draw_cars(self, frame):
        # Draw each car on the frame
        for i, car in enumerate(self.cars):
            x, y = int(car['x']), int(car['y'])
            w, h = car['width'], car['height']
            color = car['color']
            
            # Draw car body
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
            
            # Draw windows
            window_y = y + int(h * 0.2)
            window_height = int(h * 0.4)
            window_width = int(w * 0.7)
            window_x = x + int(w * 0.15)
            cv2.rectangle(frame, (window_x, window_y), (window_x + window_width, window_y + window_height), (200, 200, 255), -1)
            
            # Add car number
            cv2.putText(frame, f'Car {i+1}', (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

if __name__ == "__main__":
    simulator = SimpleTrafficSimulator()
    simulator.generate_simulation()
