# 🚦 Traffic Management System

An intelligent **Traffic Management System** that dynamically controls traffic signals using adaptive signal timing based on real-time vehicle density. The project simulates an intelligent traffic intersection using Python, image processing concepts, and computer vision techniques to reduce congestion, waiting time, and improve overall traffic flow.

---

## 📌 Features

- Adaptive traffic signal control
- Dynamic green signal allocation based on vehicle count
- Real-time traffic density analysis
- Vehicle movement simulation
- Collision-free junction management using zone control
- Performance logging and statistics
- Traffic throughput analysis
- Visualization of traffic movement
- Extensible for AI-based vehicle detection (YOLO)

---

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Libraries:**
  - NumPy
  - OpenCV
  - Matplotlib
- **Development Environment:**
  - Google Colab
  - Visual Studio Code / PyCharm
- **AI Extension:**
  - YOLO Object Detection (Future Integration)

---

## 📂 Project Structure

```
Traffic-Management-System/
│
├── main.py
├── simulation.py
├── traffic_signal.py
├── vehicle.py
├── utils.py
├── assets/
├── outputs/
├── logs/
├── requirements.txt
└── README.md
```

> *Project structure may vary depending on implementation.*

---

## ⚙️ Working

The system operates in the following stages:

1. Initialize the traffic intersection.
2. Generate vehicles randomly.
3. Detect vehicle density in each lane.
4. Calculate optimal green signal duration.
5. Update traffic signals dynamically.
6. Move vehicles safely through the intersection.
7. Record traffic statistics.
8. Display simulation results.

---

## 🧠 Algorithm

The adaptive traffic signal algorithm performs the following:

- Count waiting vehicles in each lane.
- Compute green signal time using:

```
Green Time = Minimum Green + (Vehicle Count × Scaling Factor)
```

- Restrict timing within predefined limits.
- Alternate between North-South and East-West phases.
- Prevent vehicle collisions using zone control.
- Store logs for performance evaluation.

---

## 📊 Performance Metrics

The system evaluates:

- Vehicle throughput
- Average waiting time
- Queue length
- Signal efficiency
- Traffic density
- Simulation stability

---

## ✅ Testing

The project was tested under multiple traffic conditions:

- Low traffic
- Medium traffic
- Heavy traffic
- Uneven lane distribution
- Random vehicle arrival rates

Testing verified:

- Correct adaptive signal switching
- Collision-free vehicle movement
- Improved traffic flow compared to fixed-time signals

---

## 📈 Results

The adaptive traffic management system provides:

- Reduced vehicle waiting time
- Improved intersection throughput
- Better traffic flow
- Efficient congestion handling
- Stable performance under varying traffic loads

---

## 🚀 Future Enhancements

- Live CCTV integration
- YOLOv8-based vehicle detection
- Multi-intersection traffic coordination
- IoT sensor integration
- Emergency vehicle prioritization
- Deep Reinforcement Learning (DRL)
- Cloud dashboard for real-time monitoring
- Traffic prediction using CNN-LSTM models

---

## 📚 References

- Intelligent Traffic Management using Deep Learning
- YOLO-based Vehicle Detection
- Deep Reinforcement Learning for Traffic Signal Control
- IoT-based Traffic Monitoring Systems
- CNN-LSTM Traffic Prediction Models
- Edge AI for Smart Traffic Management

---

## 👨‍💻 Team Members

- **Manish Ramu**
- **Mohammad Amaan**
- **Nishanth Reddy N**

**Guide:** Dr. Shubha Rao V

Department of Computer Science and Engineering

B.M.S. College of Engineering, Bengaluru

---

## 📄 License

This project was developed for academic purposes as part of the Mini Project requirement of the Bachelor of Engineering (Computer Science and Engineering) program at B.M.S. College of Engineering.

---

## ⭐ Acknowledgement

We sincerely thank **Dr. Shubha Rao V**, the Department of Computer Science and Engineering, and **B.M.S. College of Engineering** for their continuous guidance and support throughout the development of this project.
