import cv2
import os

def capture_test_image():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    print("Press 'c' to capture an image or 'q' to quit")
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to grab frame")
            break
        
        # Display the frame
        cv2.imshow('Capture Test Image', frame)
        
        # Wait for key press
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c'):
            # Save the image
            cv2.imwrite('test_image.jpg', frame)
            print("Image saved as test_image.jpg")
            break
        elif key == ord('q'):
            break
    
    # Release everything
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    capture_test_image() 