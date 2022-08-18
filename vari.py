import cv2 as cv
import numpy as np

image = cv.imread("/tmp/2022-08-17_14-20-46.jpg")

red_channel = image[:,:,2]
blue_channel = image[:,:,0]
green_channel = image[:,:,1]

print((green_channel + red_channel) - blue_channel)

vari = np.divide( (green_channel - red_channel), ((green_channel + red_channel) - blue_channel) )

cv.imwrite("/tmp/vari_2022-08-17_14-20-46.jpg", vari)