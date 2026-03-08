import cv2
import time
import multiprocessing
import os
import sys
import psutil

# Add root directory to python path to resolve 'src' module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.pipeline import VisionPipeline
from src.vision.kalman import PredictiveTrajectory
from src.vision.biosignature import BioSignatureLock
from src.classifier.gestures import GestureClassifier, Gesture
from src.physics.engine import PhysicsEngine
from src.os_control.windows_api import WindowsController

def vision_process(data_queue):
    # Set high priority
    try:
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception as e:
        print(f"Could not set high priority: {e}")

    pipeline = VisionPipeline()
    pipeline.start()

    try:
        while True:
            frame, landmarks = pipeline.get_latest_data()
            if frame is not None:
                # We put the landmarks into the queue.
                # Since we can't easily pickle Mediapipe protobufs, we extract what we need
                # actually, we can pass basic dicts or process in the main thread
                pass
                
                if landmarks:
                    pipeline.draw_landmarks(frame, landmarks)
                
                # We will actually run the orchestrator in the main thread for simplicity 
                # OR we run the classifier here to pass simple enums to the orchestrator.
                # Let's do a unified loop for now for simplicity, with vision running in a thread.
                # The VisionPipeline class already handles threading internally!
                
                cv2.imshow("Neural OS - Vision", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


def run_orchestrator(camera_index=0):
    print("Starting Neural OS Controller...")
    
    # Priority
    try:
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
    except Exception as e:
         print(f"Priority error: {e}")

    pipeline = VisionPipeline(camera_index=camera_index)
    pipeline.start()
    
    classifier = GestureClassifier()
    physics = PhysicsEngine()
    os_ctrl = WindowsController()
    kalman = PredictiveTrajectory()
    bio_lock = BioSignatureLock()
    
    active_window = None
    window_last_pos = None
    
    cooldown_times = {
        Gesture.ORBITAL_ROTATION: 0,
        Gesture.EVENT_HORIZON: 0,
        Gesture.CENTRIFUGAL_EJECTION: 0
    }
    COOLDOWN_DUR = 1.0 # seconds
    
    print("Press 'C' to calibrate Bio-Signature. Press 'ESC' to exit.")
    
    try:
        while True:
            frame, landmarks = pipeline.get_latest_data()
            if frame is None:
                time.sleep(0.01)
                continue
                
            display_frame = frame.copy()
            current_time = time.time()
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == ord('c') or key == ord('C'):
                print("Starting Bio-Signature Calibration. Hold hand steady...")
                bio_lock.start_calibration()
                
            if landmarks:
                pipeline.draw_landmarks(display_frame, landmarks)
                
                # Bio-Signature update/check
                if bio_lock.calibrating:
                    if bio_lock.update_calibration(landmarks):
                        print("Calibration complete! Neural Lock engaged.")
                    cv2.putText(display_frame, "Calibrating...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)
                    cv2.imshow("Neural OS Controller", display_frame)
                    continue
                    
                if not bio_lock.is_authorized(landmarks):
                    cv2.putText(display_frame, "UNAUTHORIZED USER", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow("Neural OS Controller", display_frame)
                    continue

                # 1. Prediction & Trajectory
                wrist = landmarks.landmark[0]
                kalman.update(wrist.x, wrist.y)
                # Predict 5 frames ahead
                px, py = kalman.predict_frames(5)
                
                # 2. Classification
                gesture, state = classifier.classify(landmarks)
                cv2.putText(display_frame, f"Gesture: {gesture.name}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # 3. Action Execution
                if gesture == Gesture.MASS_CAPTURE:
                    if active_window is None:
                        active_window = os_ctrl.get_foreground_window()
                        window_last_pos = state.get('pinch_center')
                        
                    if active_window and window_last_pos:
                        curr_pinch = state.get('pinch_center')
                        dx = curr_pinch[0] - window_last_pos[0]
                        dy = curr_pinch[1] - window_last_pos[1]
                        
                        # Map dx, dy to screen pixels
                        sdx, sdy = physics.map_normalized_to_screen(dx, dy)
                        
                        wx, wy, ww, wh = os_ctrl.get_window_rect(active_window)
                        if ww > 0:
                            # Use predicted coordinates for smoother feel
                            pred_dx, pred_dy = physics.map_normalized_to_screen(px - wrist.x, py - wrist.y)
                            
                            new_x = wx + sdx + int(pred_dx * 0.1) # Mix some prediction in
                            new_y = wy + sdy + int(pred_dy * 0.1)
                            
                            # Z-Depth Mapping
                            bbox_width = abs(landmarks.landmark[17].x - landmarks.landmark[5].x) * 5 # Approx width
                            opacity = physics.get_z_depth_mapping(wrist.z, bbox_width)
                            
                            os_ctrl.move_window(active_window, new_x, new_y, ww, wh)
                            os_ctrl.set_window_opacity(active_window, opacity)
                            
                            # Save velocity for inertial smoothing
                            physics.active_window_velocity = (sdx, sdy)
                        
                        window_last_pos = curr_pinch
                else:
                    # Release Pinch
                    if active_window:
                        # Restore Opacity
                        os_ctrl.set_window_opacity(active_window, 1.0)
                        
                        # Apply physics (Inertial smoothing & Snapping)
                        vx, vy = physics.active_window_velocity
                        if abs(vx) > 2 or abs(vy) > 2:
                            # Apply a simplified momentum kick
                            wx, wy, ww, wh = os_ctrl.get_window_rect(active_window)
                            if ww > 0:
                                snap_rect = physics.check_gravitational_snap(wx + vx*10, wy + vy*10, ww, wh)
                                if snap_rect:
                                    os_ctrl.move_window(active_window, snap_rect[0], snap_rect[1], snap_rect[2], snap_rect[3])
                                else:
                                    # Simple translation kick
                                    os_ctrl.move_window(active_window, wx + vx*10, wy + vy*10, ww, wh)
                            
                        active_window = None
                        physics.active_window_velocity = (0, 0)

                # Flick
                if gesture == Gesture.CENTRIFUGAL_EJECTION and (current_time - cooldown_times[Gesture.CENTRIFUGAL_EJECTION] > COOLDOWN_DUR):
                    hwnd = os_ctrl.get_foreground_window()
                    os_ctrl.minimize_window(hwnd)
                    cooldown_times[Gesture.CENTRIFUGAL_EJECTION] = current_time

                # Fist
                if gesture == Gesture.EVENT_HORIZON and (current_time - cooldown_times[Gesture.EVENT_HORIZON] > COOLDOWN_DUR):
                    os_ctrl.execute_stealth_protocol()
                    cooldown_times[Gesture.EVENT_HORIZON] = current_time

                # Twist
                if gesture == Gesture.ORBITAL_ROTATION and (current_time - cooldown_times[Gesture.ORBITAL_ROTATION] > COOLDOWN_DUR):
                    delta = state.get('twist_delta', 0)
                    if delta > 15:
                        os_ctrl.switch_virtual_desktop("right")
                        cooldown_times[Gesture.ORBITAL_ROTATION] = current_time
                    elif delta < -15:
                        os_ctrl.switch_virtual_desktop("left")
                        cooldown_times[Gesture.ORBITAL_ROTATION] = current_time

            cv2.imshow("Neural OS Controller", display_frame)

    except KeyboardInterrupt:
        pass
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    cam_idx = 0
    if len(sys.argv) > 1:
        try:
            cam_idx = int(sys.argv[1])
        except ValueError:
            print(f"Invalid camera index: {sys.argv[1]}. Using default 0.")
    run_orchestrator(cam_idx)
