import os
import argparse
from simulation_generator import TrafficSimulator
from car_detection import TrafficSignalManagement

def main():
    parser = argparse.ArgumentParser(description='Traffic Signal Management System')
    parser.add_argument('--generate', action='store_true', help='Generate simulation video')
    parser.add_argument('--detect', action='store_true', help='Run car detection on video')
    parser.add_argument('--video', type=str, default='traffic_simulation.mp4', help='Path to video file')
    parser.add_argument('--duration', type=int, default=20, help='Duration of simulation video in seconds')
    
    args = parser.parse_args()
    
    if args.generate:
        print("Generating traffic simulation video...")
        simulator = TrafficSimulator(output_path=args.video, duration=args.duration)
        simulator.generate_simulation()
        print(f"Simulation video saved to {args.video}")
    
    if args.detect:
        print(f"Running car detection on {args.video}...")
        if not os.path.exists(args.video):
            print(f"Error: Video file {args.video} not found.")
            if not args.generate:
                print("You can generate a simulation video using --generate")
            return
        
        traffic_system = TrafficSignalManagement(args.video)
        traffic_system.run()
    
    if not args.generate and not args.detect:
        # If no arguments provided, run both
        print("Generating traffic simulation video...")
        simulator = TrafficSimulator(output_path=args.video, duration=args.duration)
        simulator.generate_simulation()
        
        print(f"Running car detection on {args.video}...")
        traffic_system = TrafficSignalManagement(args.video)
        traffic_system.run()

if __name__ == "__main__":
    main()