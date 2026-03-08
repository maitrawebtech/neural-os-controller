import numpy as np
from filterpy.kalman import KalmanFilter

class PredictiveTrajectory:
    def __init__(self, fps=60):
        self.dt = 1.0 / fps
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        
        # State: [x, y, dx, dy]
        # Measurement: [x, y]
        
        # State Transition Matrix F
        self.kf.F = np.array([[1, 0, self.dt, 0],
                              [0, 1, 0, self.dt],
                              [0, 0, 1,       0],
                              [0, 0, 0,       1]])
        
        # Measurement Function H
        self.kf.H = np.array([[1, 0, 0, 0],
                              [0, 1, 0, 0]])
        
        # Measurement Noise Covariance R
        self.kf.R *= 10 # Adjust based on noise of mediapipe
        
        # Process Noise Covariance Q
        # Q_discrete_white_noise isn't strictly necessary for simple cases, we can use a basic array
        q = 0.1
        self.kf.Q = np.array([[q, 0, 0, 0],
                              [0, q, 0, 0],
                              [0, 0, q, 0],
                              [0, 0, 0, q]])
        
        # Initial State Covariance
        self.kf.P *= 1000
        
        self.initialized = False

    def update(self, x, y):
        # Handle normalization from mediapipe coords (0-1) to something larger (like screen coords 0-1920)
        # Assuming x, y come in as screen coordinates already scaled
        
        if not self.initialized:
            self.kf.x = np.array([[x], [y], [0.], [0.]])
            self.initialized = True
        
        self.kf.predict()
        self.kf.update(np.array([[x], [y]]))
        
    def predict_frames(self, frames=5):
        if not self.initialized:
            return None, None
            
        # To predict multiple frames ahead without updating:
        x_pred = self.kf.x.copy()
        
        # Project forward 'frames' times
        for _ in range(frames):
            x_pred = np.dot(self.kf.F, x_pred)
            
        return x_pred[0, 0], x_pred[1, 0]
    
    def get_velocity(self):
        """Returns dx, dy"""
        if not self.initialized:
            return 0, 0
        return self.kf.x[2, 0], self.kf.x[3, 0]
