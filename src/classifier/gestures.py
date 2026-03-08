import math
import time
from enum import Enum

class Gesture(Enum):
    NONE = 0
    MASS_CAPTURE = 1
    CENTRIFUGAL_EJECTION = 2
    ORBITAL_ROTATION = 3
    EVENT_HORIZON = 4

class GestureClassifier:
    def __init__(self):
        self.last_wrist_pos = None
        self.last_wrist_time = 0
        self.base_pinch_threshold = 0.05
        self.fist_threshold = 0.1
        self.flick_velocity_threshold = 3.5 # normalized distance per second (increased to prevent accidental flicks)
        
        self.last_twist_angle = None
        
    def distance(self, p1, p2):
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

    def classify(self, landmarks, frame_width=640, frame_height=480):
        if not landmarks:
            return Gesture.NONE, {}

        # Landmarks structure based on Mediapipe Hand
        lm = landmarks.landmark
        
        wrist = lm[0]
        thumb_tip = lm[4]
        index_tip = lm[8]
        middle_tip = lm[12]
        ring_tip = lm[16]
        pinky_tip = lm[20]
        
        current_time = time.time()
        
        state = {}
        
        # 1. Mass Capture (The Pinch)
        dist_thumb_index = self.distance(thumb_tip, index_tip)
        is_pinching = dist_thumb_index < self.base_pinch_threshold
        
        state['is_pinching'] = is_pinching
        state['pinch_center'] = ((thumb_tip.x + index_tip.x) / 2, (thumb_tip.y + index_tip.y) / 2)
        
        # 2. Event Horizon (The Fist)
        dist_index_wrist = self.distance(index_tip, wrist)
        dist_middle_wrist = self.distance(middle_tip, wrist)
        dist_ring_wrist = self.distance(ring_tip, wrist)
        dist_pinky_wrist = self.distance(pinky_tip, wrist)
        
        is_fist = (dist_index_wrist < self.fist_threshold and 
                   dist_middle_wrist < self.fist_threshold and 
                   dist_ring_wrist < self.fist_threshold and 
                   dist_pinky_wrist < self.fist_threshold and
                   not is_pinching) # Disambiguate from tight pinch
                   
        # 3. Centrifugal Ejection (The Flick)
        is_flick = False
        is_new_frame = True
        if self.last_wrist_pos is not None:
            if wrist.x == self.last_wrist_pos.x and wrist.y == self.last_wrist_pos.y and wrist.z == self.last_wrist_pos.z:
                is_new_frame = False

        if self.last_wrist_pos is not None and is_new_frame:
            dt = current_time - self.last_wrist_time
            if dt > 0:
                dist_wrist = self.distance(wrist, self.last_wrist_pos)
                velocity = dist_wrist / dt
                
                # Check if hand is open (not fist, not pinching)
                is_open = not is_fist and not is_pinching
                
                # We expect a high velocity
                if velocity > self.flick_velocity_threshold and is_open:
                    is_flick = True
        
        if is_new_frame:
            self.last_wrist_pos = wrist
            self.last_wrist_time = current_time
        
        # 4. Orbital Rotation (Two-Finger Twist)
        is_twist = False
        twist_delta = 0
        if not is_fist:
            dy = middle_tip.y - index_tip.y
            dx = middle_tip.x - index_tip.x
            angle = math.degrees(math.atan2(dy, dx))
            
            if self.last_twist_angle is not None:
                twist_delta = angle - self.last_twist_angle
                # If absolute angle change is significant, class it as twist
                if abs(twist_delta) > 15: # 15 degrees change
                    is_twist = True
            
            self.last_twist_angle = angle
        else:
            self.last_twist_angle = None
            
        state['twist_delta'] = twist_delta


        # Priority resolution
        if is_fist:
            return Gesture.EVENT_HORIZON, state
        elif is_flick:
            return Gesture.CENTRIFUGAL_EJECTION, state
        elif is_pinching:
            return Gesture.MASS_CAPTURE, state
        elif is_twist:
            return Gesture.ORBITAL_ROTATION, state
            
        return Gesture.NONE, state
