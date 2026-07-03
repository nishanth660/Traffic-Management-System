import argparse
import os
from simulation_generator import TrafficSimulator
from car_detection import TrafficSignalManagement

def main():
    parser = argparse.ArgumentParser(description='Traffic Signal Management System')
    parser.add_argument('--generate', action='store_true', help='Generate traffic simulation video')
    parser.add_argument('--detect', action='store_true', help='Detect cars in video')
    parser.add_argument('--video', type=str, default='simulation.mp4', help='Path to video file')
    parser.add_argument('--duration', type=int, default=10, help='Duration of simulation in seconds')
    parser.add_argument('--real-footage', action='store_true', help='Optimize for real-life footage')
    parser.add_argument('--realistic', action='store_true', help='Generate more realistic simulation')
    
    args = parser.parse_args()
    
    if args.generate:
        print("Generating traffic simulation video...")
        simulator = TrafficSimulator(output_path=args.video, duration=args.duration, realistic=args.realistic)
        simulator.generate_simulation()
        if args.realistic:
            print("Generated realistic traffic simulation video")
        
    if args.detect:
        print(f"Running car detection on {args.video}...")
        if not os.path.exists(args.video):
            print(f"Error: Video file {args.video} not found")
            return
            
        detector = TrafficSignalManagement(video_path=args.video, is_real_footage=args.real_footage)
        if args.real_footage:
            print("Using optimized settings for real-life footage")
        detector.process_video()
        
    if not args.generate and not args.detect:
        # Default behavior: generate and detect
        print("Generating traffic simulation video...")
        simulator = TrafficSimulator(output_path=args.video, duration=args.duration)
        simulator.generate_simulation()
        
        print(f"Running car detection on {args.video}...")
        detector = TrafficSignalManagement(video_path=args.video, is_real_footage=args.real_footage)
        if args.real_footage:
            print("Using optimized settings for real-life footage")
        detector.process_video()

if __name__ == "__main__":
    main()