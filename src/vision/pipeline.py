import cv2
import mediapipe as mp
import threading
import numpy as np

class VisionPipeline:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.mp_hands = mp.solutions.hands
        # Using ONE hand for OS control primarily
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
        self.latest_frame = None
        self.latest_landmarks = None

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        # Set some optimal properties for speed
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_index}")
        
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()
        self.hands.close()

    def _adaptive_luminance(self, frame):
        """
        Calculates brightness. If it is too dark, applies CLAHE (Contrast Limited Adaptive Histogram Equalization)
        or simple gain to improve landmark detection.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = cv2.mean(gray)[0]
        
        if mean_brightness < 80: # Threshold for 'dark'
            # Apply subtle alpha/beta correction to boost brightness
            # alpha (1.0-3.0) contrast, beta (0-100) brightness
            alpha = 1.2
            beta = 50
            frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
        return frame

    def _capture_loop(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                continue

            # Flip horizontally for selfie-view display
            frame = cv2.flip(frame, 1)

            # Adaptive Luminance
            processed_frame = self._adaptive_luminance(frame)

            # Convert BGR to RGB for Mediapipe
            frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False # Improve performance
            results = self.hands.process(frame_rgb)

            landmarks = None
            if results.multi_hand_landmarks:
                # We only take the first hand detected
                landmarks = results.multi_hand_landmarks[0]
                # Also get handedness (Left/Right) if needed later
                # handedness = results.multi_handedness[0]

            with self.lock:
                self.latest_frame = frame
                self.latest_landmarks = landmarks

    def get_latest_data(self):
        """Returns the latest BGR frame and HandLandmark protobuf"""
        with self.lock:
            if self.latest_frame is None:
                return None, None
            return self.latest_frame.copy(), self.latest_landmarks

    def draw_landmarks(self, frame, landmarks):
        """Helper to visualize landmarks on the frame"""
        self.mp_drawing.draw_landmarks(
            frame,
            landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style())
