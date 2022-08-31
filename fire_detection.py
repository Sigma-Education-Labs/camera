import numpy as np
import cv2

def image_contains_fire(image):
    blur = cv2.blur(image,(5,5))
    blur0=cv2.medianBlur(blur,5)
    blur1= cv2.GaussianBlur(blur0,(5,5),0)
    blur2= cv2.bilateralFilter(blur1,9,75,75)

    hsv = cv2.cvtColor(blur2, cv2.COLOR_BGR2HSV)

    ## RED
    lower_red = np.array([0, 120, 200])
    upper_red = np.array([50, 250, 250])

    # Threshold with inRange() get only specific colors
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(hsv, hsv, mask= mask_red)    
    
    if (len(np.nonzero(res)[0]) > 0 and len(np.nonzero(res)[1]) > 0):
        return True
    else:
        return False