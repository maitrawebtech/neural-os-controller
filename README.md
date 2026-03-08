                                                                                          # Neural OS Controller

**Made by Ishan Maitra - Cloud & AI Developer of Google Cloud**

A futuristic, touchless operating system controller that translates 3D hand kinematics into precise system-level actions. By leveraging advanced Computer Vision and State Estimation algorithms, this project allows you to control your Windows PC using intuitive, "Jedi-like" gravitational gestures—no mouse or keyboard required.

## ✨ Features

*   **Touchless Window Management**: Grab, drag, and drop any active window on your screen using only your hand in mid-air.
*   **Inertial Physics Engine**: Windows glide and snap with built-in momentum when you release them during a drag, creating a natural, fluid feel.
*   **Instant Window Minimization**: Rapidly flick your hand to minimize the current window.
*   **Stealth Protocol**: Quickly clench a fist to instantly mute your system volume and hide all windows, showing the desktop.
*   **Virtual Desktop Navigation**: Twist your hand to seamlessly snap between your Windows Virtual Desktops.
*   **Ultra-Low Latency Tracking**: Uses Google MediaPipe and predictive Kalman Filters to ensure cursor movements are perfectly synced with physical motion.
*   **Universal Accessibility**: The system currently bypasses biocryptographic locks, allowing anyone to jump in and control the OS immediately.

## 🧠 Technologies Built-In

### Machine Learning & Computer Vision (CV)
This project heavily relies on real-time computer vision and mathematical modeling rather than traditional NLP:

*   **Google MediaPipe (Hand Landmark Detection)**: The core perception engine uses MediaPipe's deep neural networks to infer 21 distinct 3D landmarks of a hand from just a standard 2D webcam. This ML model operates in ultra-fast real-time, providing the foundation for all spatial calculations.
*   **Predictive Tracking (Kalman Filters)**: To ensure that grabbing and dragging windows feels completely smooth and weightless, the system utilizes a **Kalman Filter** (`filterpy`). This algorithm predicts the future trajectory of your hand to compensate for camera latency and perfectly sync on-screen physics with your physical movements.
*   **Biometric Cryptography (Bio-Signature)**: The system can calibrate a unique biological signature by extracting the geometric ratios of your specific hand structure (palm length, finger aspect ratios). *Note: Currently bypassed for universal access, but structurally implemented as a bio-lock.*
*   **Geometric Heuristics**: Custom mathematically-driven classifiers that calculate Euclidean distances and twist angles in 3D space to differentiate between complex kinematics like a "flick" vs. a "pinch".

### Natural Language Processing (NLP)
*   *Note: This specific iteration of the Neural OS Controller focuses entirely on **visual-spatial** intelligence and does not currently utilize Natural Language Processing or Speech-to-Text models. Audio integration is limited to system-level volume control (muting) via `pycaw`, triggered by physical gestures rather than voice commands.*

## ✋ Supported Gestures

1.  **Mass Capture (The Pinch)**: Pinch your thumb and index finger to grab the active window. Move your hand to drag the window across your screen with built-in momentum physics.
2.  **Centrifugal Ejection (The Flick)**: An open-handed rapid sweeping motion instantly minimizes the current window.
3.  **Event Horizon (The Fist)**: Clenching a tight fist triggers a "Stealth Protocol", instantly muting system audio and hiding all windows to show the desktop.
4.  **Orbital Rotation (Two-Finger Twist)**: Point your index and middle fingers and twist your wrist to quickly snap between Windows Virtual Desktops (Left/Right).

## 🌍 How This Helps People

The Neural OS Controller is more than just a sci-fi concept; it has practical, real-world benefits:

*   **Ultimate Accessibility**: Provides a robust alternative for individuals with motor disabilities or conditions like severe arthritis, who find grasping and clicking a traditional mouse painful or impossible.
*   **Sterile & Messy Environments**: Ideal for users who cannot touch their hardware. Whether you are a surgeon reviewing digital X-Rays in a sterile operating room, a mechanic with greasy hands checking a manual, or just cooking in the kitchen, you can control your PC without dirtying your peripherals.
*   **Ergonomics & RSI Prevention**: Prolonged use of standard mice leads to Repetitive Strain Injuries (RSI) like Carpal Tunnel Syndrome. Gestational control allows for macro-movements of the arm and shoulder, reducing micro-strain on wrist tendons.
*   **Enhanced Productivity**: With gestures like the "Orbital Rotation" to snap between virtual desktops or the "Event Horizon" to instantly clear the screen, power users can navigate their OS faster than using traditional keyboard shortcuts.

## 🚀 Getting Started

1.  Clone the repository and ensure you are on a Windows machine.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the orchestrator: `python src/main.py 1`
4.  Step back, raise your hand, and take control of your OS by your hand.


