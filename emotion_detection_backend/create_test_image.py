import numpy as np
import cv2

def create_test_image():
    # Create a blank image
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Draw a simple face
    # Head
    cv2.circle(img, (150, 150), 100, (255, 255, 255), -1)
    
    # Eyes
    cv2.circle(img, (100, 120), 10, (0, 0, 0), -1)
    cv2.circle(img, (200, 120), 10, (0, 0, 0), -1)
    
    # Smile
    cv2.ellipse(img, (150, 150), (50, 30), 0, 0, 180, (0, 0, 0), 2)
    
    # Save the image
    cv2.imwrite('test_image.jpg', img)
    print("Test image created: test_image.jpg")

if __name__ == '__main__':
    create_test_image() 