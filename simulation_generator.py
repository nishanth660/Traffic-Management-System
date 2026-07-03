import cv2
import numpy as np
import random
import os

class TrafficSimulator:
    def __init__(self, output_path='simulation.mp4', duration=10, fps=30, realistic=False):
        self.output_path = output_path
        self.duration = duration
        self.fps = fps
        self.frame_width = 800
        self.frame_height = 600
        self.cars = []
        self.realistic = realistic  # Flag for more realistic simulation
        
    def generate_simulation(self):
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (self.frame_width, self.frame_height))
        
        # Generate frames
        for frame_idx in range(self.duration * self.fps):
            # Create a frame with road
            frame = self.create_road_frame()
            
            # Add new cars very rarely to prevent overlaps
            if random.random() < 0.005 and len(self.cars) < 3:  # 0.5% chance and max 3 cars
                self.add_car()
                
            # Update and draw cars
            self.update_cars()
            self.draw_cars(frame)
            
            # Add frame number and car count
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
        
        if self.realistic:
            # Create more realistic road with texture and noise
            road_y = self.frame_height // 2
            road_height = 200
            
            # Draw road with asphalt texture (dark gray with noise)
            road = np.random.randint(60, 80, (road_height, self.frame_width, 3), dtype=np.uint8)
            
            # Add some road texture/grain
            noise = np.random.randint(0, 15, (road_height, self.frame_width, 3), dtype=np.uint8)
            road = cv2.add(road, noise)
            
            # Place road on frame
            frame[road_y - road_height//2:road_y + road_height//2, 0:self.frame_width] = road
            
            # Draw lane markings (white dashed lines)
            lane_y = road_y
            for x in range(0, self.frame_width, 50):
                cv2.line(frame, (x, lane_y), (x + 30, lane_y), (255, 255, 255), 5)
                
            # Add some shadows and lighting variation
            shadow_pos = random.randint(0, self.frame_width)
            shadow_width = random.randint(100, 300)
            shadow = np.ones((road_height, shadow_width, 3), dtype=np.uint8) * 30
            
            # Place shadow on road if it fits
            if shadow_pos + shadow_width <= self.frame_width:
                road_region = frame[road_y - road_height//2:road_y + road_height//2, shadow_pos:shadow_pos + shadow_width]
                frame[road_y - road_height//2:road_y + road_height//2, shadow_pos:shadow_pos + shadow_width] = cv2.subtract(road_region, shadow)
        else:
            # Original simple road
            road_y = self.frame_height // 2
            road_height = 200
            cv2.rectangle(frame, (0, road_y - road_height//2), (self.frame_width, road_y + road_height//2), (100, 100, 100), -1)
            
            # Draw lane markings (white dashed lines)
            lane_y = road_y
            for x in range(0, self.frame_width, 50):
                cv2.line(frame, (x, lane_y), (x + 30, lane_y), (255, 255, 255), 5)
            
        return frame
        
    def add_car(self):
        # Only add car if we have very few cars
        if len(self.cars) >= 2:
            return
            
        # Car properties - fixed size to prevent issues
        car_width = 50
        car_height = 35
        car_x = -car_width  # Start from left side
        car_speed = random.randint(5, 15)
        car_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
        
        # Define ONLY 3 specific lanes with large gaps
        lanes = [
            self.frame_height // 2 - 80,  # Top lane
            self.frame_height // 2,       # Middle lane  
            self.frame_height // 2 + 80   # Bottom lane
        ]
        
        # Check which lanes are available
        available_lanes = []
        for lane_y in lanes:
            car_y = lane_y - car_height // 2
            if not self.check_car_overlap(car_x, car_y, car_width, car_height):
                available_lanes.append(lane_y)
        
        # If we have available lanes, pick one
        if available_lanes:
            lane_y = random.choice(available_lanes)
            car_y = lane_y - car_height // 2
            
            # Add the car
            self.cars.append({
                'x': car_x,
                'y': car_y,
                'width': car_width,
                'height': car_height,
                'speed': car_speed,
                'color': car_color
            })
    
    def check_car_overlap(self, x, y, width, height):
        """Check if a car at position (x, y) with given dimensions overlaps with existing cars"""
        for car in self.cars:
            # Very strict margin to prevent ANY overlap
            margin = 30  # 30 pixel safety margin
            if (x < car['x'] + car['width'] + margin and 
                x + width + margin > car['x'] and 
                y < car['y'] + car['height'] + margin and 
                y + height + margin > car['y']):
                return True  # Overlap detected (with large safety margin)
        return False  # No overlap
        
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
        for car in self.cars:
            if self.realistic:
                # Draw more realistic car with details
                x, y = car['x'], car['y']
                w, h = car['width'], car['height']
                color = car['color']
                
                # Car body
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
                
                # Windows (darker)
                window_color = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 50))
                window_h = int(h * 0.3)
                window_y = y + int(h * 0.2)
                cv2.rectangle(frame, (x + int(w * 0.2), window_y), 
                             (x + int(w * 0.8), window_y + window_h), window_color, -1)
                
                # Wheels
                wheel_radius = int(h * 0.2)
                wheel_y = y + h - wheel_radius
                cv2.circle(frame, (x + int(w * 0.25), wheel_y), wheel_radius, (30, 30, 30), -1)
                cv2.circle(frame, (x + int(w * 0.75), wheel_y), wheel_radius, (30, 30, 30), -1)
                
                # Headlights or taillights
                light_size = int(h * 0.15)
                if car['x'] > self.frame_width // 2:  # Cars on right side have headlights
                    cv2.rectangle(frame, (x, y + int(h * 0.3)), 
                                 (x + light_size, y + int(h * 0.5)), (255, 255, 200), -1)
                else:  # Cars on left side have taillights
                    cv2.rectangle(frame, (x + w - light_size, y + int(h * 0.3)), 
                                 (x + w, y + int(h * 0.5)), (200, 0, 0), -1)
            else:
                # Original simple car drawing
                cv2.rectangle(
                    frame,
                (int(car['x']), int(car['y'])),
                (int(car['x'] + car['width']), int(car['y'] + car['height'])),
                car['color'],
                -1
            )
            # Add windows to make it look more like a car
            window_y = int(car['y'] + car['height'] * 0.2)
            window_height = int(car['height'] * 0.4)
            window_width = int(car['width'] * 0.7)
            window_x = int(car['x'] + car['width'] * 0.15)
            cv2.rectangle(
                frame,
                (window_x, window_y),
                (window_x + window_width, window_y + window_height),
                (200, 200, 255),
                -1
            )