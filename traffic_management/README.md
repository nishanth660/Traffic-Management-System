# Traffic Signal Management System

A simple traffic signal management system that uses computer vision to detect and count cars in traffic videos.

## Features

- Car detection using OpenCV and Haar Cascades
- Car counting functionality
- Traffic simulation generator for testing
- Visualization of car count history

## Requirements

- Python 3.7+
- OpenCV
- NumPy
- Matplotlib

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### Generate a Traffic Simulation Video

```
python main.py --generate --duration 20
```

This will create a `traffic_simulation.mp4` file with simulated traffic.

### Run Car Detection on a Video

```
python main.py --detect --video traffic_simulation.mp4
```

This will process the video, detect and count cars, and display the results.

### Run Both Simulation and Detection

```
python main.py
```

This will generate a simulation video and then run car detection on it.

## How It Works

1. **Traffic Simulation**: Creates a video with simulated cars moving on a road.
2. **Car Detection**: Uses Haar Cascade classifier to detect cars in each frame.
3. **Car Counting**: Counts the number of detected cars in each frame.
4. **Visualization**: Displays the car count on the video and plots a history graph.

## Customization

- Adjust the ROI (Region of Interest) in `car_detection.py` to focus on specific areas of the video
- Modify detection parameters in `detect_cars()` method to improve detection accuracy
- Change the simulation parameters in `simulation_generator.py` to create different traffic scenarios

## Notes

- This is a basic implementation and may not work perfectly in all scenarios
- For better accuracy, consider using more advanced object detection models like YOLO or SSD
- The system currently only counts cars and does not control traffic signals