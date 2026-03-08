import math
import cv2
import json
import os

class BioSignatureLock:
    def __init__(self, profile_path="user_profile.json"):
        self.profile_path = profile_path
        self.authorized_ratios = None
        self.tolerance = 0.35 # 35% tolerance to prevent strict lockouts
        self.calibrating = False
        self.calibration_frames = []
        self.required_frames = 30
        
        self.load_profile()

    def distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

    def extract_ratios(self, landmarks):
        if not landmarks:
            return None
            
        lm = landmarks.landmark
        
        # Base distances used for ratios
        palm_width = self.distance(lm[5], lm[17]) # Index knuckle to Pinky knuckle
        palm_length = self.distance(lm[0], lm[9]) # Wrist to Middle knuckle
        
        if palm_width == 0 or palm_length == 0:
            return None
            
        index_len = self.distance(lm[5], lm[8])
        middle_len = self.distance(lm[9], lm[12])
        ring_len = self.distance(lm[13], lm[16])
        pinky_len = self.distance(lm[17], lm[20])
        thumb_len = self.distance(lm[1], lm[4])
        
        ratios = {
            "palm_aspect": palm_length / palm_width,
            "index_rel": index_len / palm_length,
            "middle_rel": middle_len / palm_length,
            "ring_rel": ring_len / palm_length,
            "pinky_rel": pinky_len / palm_length,
            "thumb_rel": thumb_len / palm_length
        }
        
        return ratios

    def load_profile(self):
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r') as f:
                    self.authorized_ratios = json.load(f)
            except:
                self.authorized_ratios = None

    def save_profile(self, ratios):
        self.authorized_ratios = ratios
        with open(self.profile_path, 'w') as f:
            json.dump(ratios, f)

    def start_calibration(self):
        self.calibrating = True
        self.calibration_frames = []

    def update_calibration(self, landmarks):
        if not self.calibrating:
            return False
            
        ratios = self.extract_ratios(landmarks)
        if ratios:
            self.calibration_frames.append(ratios)
            
        if len(self.calibration_frames) >= self.required_frames:
            # Average the ratios
            avg_ratios = {}
            for key in self.calibration_frames[0].keys():
                avg_ratios[key] = sum(f[key] for f in self.calibration_frames) / self.required_frames
                
            self.save_profile(avg_ratios)
            self.calibrating = False
            return True # Calibration complete
            
        return False

    def is_authorized(self, landmarks):
        # Authorization check disabled as per user request
        # Anyone can now use the Neural OS Controller
        return True
