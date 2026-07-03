import cv2
import numpy as np
import random

class TrafficSimulatorWithSignals:
    def __init__(self, output_path='traffic_simulation_with_signals.mp4', duration=60, resolution=(800, 800)):
        self.output_path = output_path
        self.duration = duration  # seconds
        self.width, self.height = resolution
        self.fps = 30

        # Intersection center coordinates
        self.center_x, self.center_y = self.width // 2, self.height // 2

        # Road parameters
        self.road_width = 200
        self.lane_width = self.road_width // 2

        # Car parameters
        self.car_length = 40
        self.car_width = 20
        self.car_colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255)]
        self.cars = []

        # Traffic signals per lane: dict of {direction: 'red'/'green'}
        self.signals = {'N': 'red', 'S': 'red', 'E': 'green', 'W': 'green'}

        # Adaptive green signal timing system
        self.min_green_time = 10
        self.max_green_time = 40
        self.signal_cycle_time = 60  # total duration of 1 full cycle
        self.current_signal_time = 0
        self.active_green_group = 'EW'  # Either 'NS' or 'EW'

        self.frame_count = 0
        self.total_frames = self.duration * self.fps
        self.spawn_prob = 0.1

        # Lane setup for each direction
        self.lanes = {
            'N': {'start': (self.center_x - self.lane_width // 2, 0)},
            'S': {'start': (self.center_x + self.lane_width // 2, self.height)},
            'E': {'start': (self.width, self.center_y - self.lane_width // 2)},
            'W': {'start': (0, self.center_y + self.lane_width // 2)},
        }

        # Passed car counters
        self.passed_counts = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        self.junction_zone_size = 75  # Square zone near the center for overlap avoidance

    def create_background(self):
        bg = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        # Draw vertical road
        cv2.rectangle(
            bg,
            (self.center_x - self.road_width // 2, 0),
            (self.center_x + self.road_width // 2, self.height),
            (100, 100, 100), -1
        )
        # Draw horizontal road
        cv2.rectangle(
            bg,
            (0, self.center_y - self.road_width // 2),
            (self.width, self.center_y + self.road_width // 2),
            (100, 100, 100), -1
        )
        # Lane markings - vertical
        for y in range(0, self.height, 30):
            cv2.line(bg, (self.center_x, y), (self.center_x, y + 15), (255, 255, 255), 2)
        # Lane markings - horizontal
        for x in range(0, self.width, 30):
            cv2.line(bg, (x, self.center_y), (x + 15, self.center_y), (255, 255, 255), 2)
        return bg

    def draw_traffic_signal(self, frame, pos, color):
        colors_map = {'red': (0, 0, 255), 'green': (0, 255, 0), 'yellow': (0, 255, 255)}
        cv2.circle(frame, pos, 15, colors_map.get(color, (0, 0, 0)), -1)
        return frame

    def draw_cars(self, frame):
        for car in self.cars:
            x, y = int(car['pos'][0]), int(car['pos'][1])
            color = car['color']
            # Rectangle for car orientation
            if car['dir'] in ['N', 'S']:
                top_left = (x - self.car_width // 2, y - self.car_length // 2)
                bottom_right = (x + self.car_width // 2, y + self.car_length // 2)
            else:
                top_left = (x - self.car_length // 2, y - self.car_width // 2)
                bottom_right = (x + self.car_length // 2, y + self.car_width // 2)
            cv2.rectangle(frame, top_left, bottom_right, color, -1)
        return frame

    def spawn_cars(self):
        for direction, lane_info in self.lanes.items():
            if random.random() < self.spawn_prob:
                if direction in ['N', 'S']:
                    spawn_x = lane_info['start'][0] + self.lane_width // 4 * (random.choice([-1, 1]))
                    spawn_y = lane_info['start'][1]
                else:
                    spawn_x = lane_info['start'][0]
                    spawn_y = lane_info['start'][1] + self.lane_width // 4 * (random.choice([-1, 1]))
                speed = random.uniform(2, 4)
                car = {
                    'pos': (spawn_x, spawn_y),
                    'dir': direction,
                    'color': random.choice(self.car_colors),
                    'speed': speed,
                    'stopped': False,
                    'in_junction': False  # Used to prevent overlap in junction
                }
                self.cars.append(car)

    def move_cars(self):
        new_cars = []
        junction_occupied = {'N': False, 'S': False, 'E': False, 'W': False}
        for car in self.cars:
            x, y = car['pos']
            dir = car['dir']
            speed = car['speed']

            # Junction zone boundaries
            jx1 = self.center_x - self.junction_zone_size // 2
            jx2 = self.center_x + self.junction_zone_size // 2
            jy1 = self.center_y - self.junction_zone_size // 2
            jy2 = self.center_y + self.junction_zone_size // 2

            # Predict next step to check junction entry/exit
            new_x, new_y = x, y
            if dir == 'N': new_y = y + speed
            if dir == 'S': new_y = y - speed
            if dir == 'E': new_x = x - speed
            if dir == 'W': new_x = x + speed

            # Is the car inside the junction zone after the move?
            in_junction = (
                jx1 <= new_x <= jx2 and jy1 <= new_y <= jy2
            )

            # If at entry point and allowed, move into the junction if not already occupied by same direction
            if not car['in_junction'] and in_junction:
                if not junction_occupied[dir] and self.signals[dir] == 'green':
                    car['in_junction'] = True
                    junction_occupied[dir] = True
                    # Count this as a passed car
                    self.passed_counts[dir] += 1
                    # Move car further into junction
                    x, y = new_x, new_y
                else:
                    # Stop car at junction border if occupied
                    car['stopped'] = True
            else:
                # Standard signal stop logic before junction
                stop_line = None
                if dir == 'N':
                    stop_line = self.center_y - self.road_width//2 - self.car_length//2
                    if self.signals['N'] == 'red' and y + speed >= stop_line:
                        car['stopped'] = True
                    elif self.signals['N'] == 'green':
                        car['stopped'] = False
                    if not car['stopped'] and y < self.height:
                        y += speed
                elif dir == 'S':
                    stop_line = self.center_y + self.road_width//2 + self.car_length//2
                    if self.signals['S'] == 'red' and y - speed <= stop_line:
                        car['stopped'] = True
                    elif self.signals['S'] == 'green':
                        car['stopped'] = False
                    if not car['stopped'] and y > 0:
                        y -= speed
                elif dir == 'E':
                    stop_line = self.center_x + self.road_width//2 + self.car_length//2
                    if self.signals['E'] == 'red' and x - speed <= stop_line:
                        car['stopped'] = True
                    elif self.signals['E'] == 'green':
                        car['stopped'] = False
                    if not car['stopped'] and x > 0:
                        x -= speed
                elif dir == 'W':
                    stop_line = self.center_x - self.road_width//2 - self.car_length//2
                    if self.signals['W'] == 'red' and x + speed >= stop_line:
                        car['stopped'] = True
                    elif self.signals['W'] == 'green':
                        car['stopped'] = False
                    if not car['stopped'] and x < self.width:
                        x += speed

            car['pos'] = (x, y)
            # Remove car if it has gone beyond the frame
            if 0 <= x <= self.width and 0 <= y <= self.height:
                new_cars.append(car)
        self.cars = new_cars

    def count_waiting_cars_per_direction(self):
        count = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
        for car in self.cars:
            x, y = car['pos']
            dir = car['dir']
            if dir == 'N':
                stop_line = self.center_y - self.road_width//2 - self.car_length//2 + 5
                if self.signals['N'] == 'red' and y < stop_line + 15:
                    count['N'] += 1
            elif dir == 'S':
                stop_line = self.center_y + self.road_width//2 + self.car_length//2 - 5
                if self.signals['S'] == 'red' and y > stop_line - 15:
                    count['S'] += 1
            elif dir == 'E':
                stop_line = self.center_x + self.road_width//2 + self.car_length//2 - 5
                if self.signals['E'] == 'red' and x > stop_line - 15:
                    count['E'] += 1
            elif dir == 'W':
                stop_line = self.center_x - self.road_width//2 - self.car_length//2 + 5
                if self.signals['W'] == 'red' and x < stop_line + 15:
                    count['W'] += 1
        return count

    def update_signals(self):
        waiting_cars = self.count_waiting_cars_per_direction()
        NS_count = waiting_cars['N'] + waiting_cars['S']
        EW_count = waiting_cars['E'] + waiting_cars['W']

        self.current_signal_time += 1

        if self.active_green_group == 'EW':
            green_duration = int(np.clip(EW_count * 4 + self.min_green_time, self.min_green_time, self.max_green_time))
            if self.current_signal_time > green_duration * self.fps:
                self.signals = {'N': 'green', 'S': 'green', 'E': 'red', 'W': 'red'}
                self.active_green_group = 'NS'
                self.current_signal_time = 0
        else:
            green_duration = int(np.clip(NS_count * 4 + self.min_green_time, self.min_green_time, self.max_green_time))
            if self.current_signal_time > green_duration * self.fps:
                self.signals = {'N': 'red', 'S': 'red', 'E': 'green', 'W': 'green'}
                self.active_green_group = 'EW'
                self.current_signal_time = 0

    def draw_traffic_signals_on_frame(self, frame):
        offset = 50
        frame = self.draw_traffic_signal(frame, (self.center_x - offset, self.center_y - self.road_width//2 - offset), self.signals['N'])
        frame = self.draw_traffic_signal(frame, (self.center_x + offset, self.center_y + self.road_width//2 + offset), self.signals['S'])
        frame = self.draw_traffic_signal(frame, (self.center_x + self.road_width//2 + offset, self.center_y - offset), self.signals['E'])
        frame = self.draw_traffic_signal(frame, (self.center_x - self.road_width//2 - offset, self.center_y + offset), self.signals['W'])

        cv2.putText(frame, 'N', (self.center_x - offset - 10, self.center_y - self.road_width//2 - offset - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(frame, 'S', (self.center_x + offset - 10, self.center_y + self.road_width//2 + offset + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(frame, 'E', (self.center_x + self.road_width//2 + offset + 10, self.center_y - offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(frame, 'W', (self.center_x - self.road_width//2 - offset - 30, self.center_y + offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        return frame

    def draw_countdown(self, frame):
        if self.active_green_group == 'EW':
            green_duration = int(np.clip(sum([c for d, c in self.count_waiting_cars_per_direction().items() if d in ['E', 'W']]) * 4 + self.min_green_time, self.min_green_time, self.max_green_time))
            countdown_sec = max(0, green_duration - self.current_signal_time / self.fps)
            text = f'Green signal time LEFT (E-W): {int(countdown_sec)}s'
        else:
            green_duration = int(np.clip(sum([c for d, c in self.count_waiting_cars_per_direction().items() if d in ['N', 'S']]) * 4 + self.min_green_time, self.min_green_time, self.max_green_time))
            countdown_sec = max(0, green_duration - self.current_signal_time / self.fps)
            text = f'Green signal time LEFT (N-S): {int(countdown_sec)}s'

        cv2.putText(frame, text, (20, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 2)
        return frame

    def draw_counts(self, frame):
        # Show passed car counts for each direction
        cv2.putText(frame, f'Passed (N): {self.passed_counts["N"]}', (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f'Passed (S): {self.passed_counts["S"]}', (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f'Passed (E): {self.passed_counts["E"]}', (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f'Passed (W): {self.passed_counts["W"]}', (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        return frame

    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (self.width, self.height))

        for _ in range(self.total_frames):
            self.frame_count += 1
            frame = self.create_background()
            self.spawn_cars()
            self.update_signals()
            self.move_cars()
            frame = self.draw_cars(frame)
            frame = self.draw_traffic_signals_on_frame(frame)
            frame = self.draw_countdown(frame)
            frame = self.draw_counts(frame)
            out.write(frame)
        out.release()
        print(f"Simulation video with traffic signals saved to {self.output_path}")

if __name__ == "__main__":
    sim = TrafficSimulatorWithSignals(duration=60)
    sim.run()
