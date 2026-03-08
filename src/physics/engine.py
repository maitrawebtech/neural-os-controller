import time

class PhysicsEngine:
    def __init__(self, screen_width=1920, screen_height=1080):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.friction_mu = 0.95
        self.snap_threshold = 50 # pixels from edge
        
        self.active_window_velocity = (0, 0)
        
    def map_normalized_to_screen(self, norm_x, norm_y):
        """Maps Mediapipe 0-1 coordinates to screen coordinates"""
        return int(norm_x * self.screen_width), int(norm_y * self.screen_height)

    def apply_inertial_smoothing(self, current_v_x, current_v_y):
        """Returns the decayed velocity"""
        new_v_x = current_v_x * self.friction_mu
        new_v_y = current_v_y * self.friction_mu
        
        # Stop completely if velocity is very small
        if abs(new_v_x) < 1.0: new_v_x = 0
        if abs(new_v_y) < 1.0: new_v_y = 0
            
        return new_v_x, new_v_y
        
    def check_gravitational_snap(self, win_x, win_y, win_w, win_h):
        """
        Returns a new position/size if it should snap to an edge,
        or None if no snap.
        """
        snap_rect = None
        
        # Left edge snap (Split screen left)
        if win_x < self.snap_threshold:
            snap_rect = (0, 0, self.screen_width // 2, self.screen_height)
            
        # Right edge snap (Split screen right)
        elif (win_x + win_w) > (self.screen_width - self.snap_threshold):
            snap_rect = (self.screen_width // 2, 0, self.screen_width // 2, self.screen_height)
            
        # Top edge snap (Maximize)
        elif win_y < self.snap_threshold:
            snap_rect = (0, 0, self.screen_width, self.screen_height)
            
        return snap_rect

    def get_z_depth_mapping(self, wrist_z, bbox_width_ratio):
        """
        Map Z distance to opacity / scale multiplier.
        Using bounding box width or wrist Z is common.
        bbox_width_ratio represents the width of the hand bounding box relative to screen.
        Larger ratio -> closer to camera.
        """
        # Baseline bounding box width might be ~0.2 of frame when normal distance.
        # Opacity range 0.2 to 1.0
        
        # Clamping
        ratio = max(0.05, min(0.5, bbox_width_ratio))
        
        # Normalize between 0.0 an 1.0 based on that range
        normalized_dist = (ratio - 0.05) / (0.5 - 0.05)
        
        # Opacity Mapping (scale closer to 1 means closer to camera, more opaque)
        opacity = max(0.2, normalized_dist)
        
        return opacity
