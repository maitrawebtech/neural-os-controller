import cv2

def test_cameras(max_cameras=5):
    print("Testing locally attached cameras...")
    valid_cams = []
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            print(f"Camera index {i}: NOT AVAILABLE")
        else:
            success, frame = cap.read()
            if success:
                print(f"Camera index {i}: WORKING")
                valid_cams.append(i)
                # Show frame briefly
                cv2.imshow(f"Camera {i} Test", frame)
                cv2.waitKey(2000) # Show for 2 seconds
                cv2.destroyWindow(f"Camera {i} Test")
            else:
                print(f"Camera index {i}: OPENED BUT NO FRAME")
            cap.release()
            
    cv2.destroyAllWindows()
    
    if valid_cams:
        print("\nValid camera indices found:", valid_cams)
        print("Run the main script with one of these indices, e.g.:")
        print(f"python src/main.py {valid_cams[0]}")
    else:
        print("\nNo working cameras found!")

if __name__ == "__main__":
    test_cameras()
