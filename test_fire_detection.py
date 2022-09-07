from functools import cache
import numpy as np
import cv2
import matplotlib.pyplot as plt

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
    count_fire = cv2.countNonZero(mask_red) 
    height, width = hsv.shape[:2] 
    prob = 0.0
    hsum = 0.0
    ssum = 0.0
    vsum = 0.0
    if (count_fire > 0):
        for i in range(0, height):
            for j in range(0, width):
                h,s,v = hsv[i][j]
                if(h<=50 and s<=250 and v<=250 and h>=0 and s>= 120 and v>= 200):
                    h = h/50.0
                    s = s/250.0
                    v = s/250.0
                    hsum = hsum +h
                    ssum = ssum +s
                    vsum = vsum +v
        prob = 0.5 + (hsum+ssum+vsum)/(3*count_fire)
    return prob

img = cv2.imread("test_images/NoFire1.jpg")
probability = image_contains_fire(img)
print("probability of fire: ",probability)
    