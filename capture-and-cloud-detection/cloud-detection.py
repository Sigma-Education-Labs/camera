import numpy as np
import matplotlib.pyplot as plt
import cv2

# load the image and perform pyramid mean shift filtering to aid the thresholding step
image = cv2.imread("data/00af77b.jpg")
w, h, bands = image.shape
shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)

# convert the mean shift image to grayscale, then apply
# Otsu's thresholding
gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

#cv2.imshow("Image", image)
'''
# compute the exact Euclidean distance from every binary
# pixel to the nearest zero pixel, then find peaks in this distance map
D = ndimage.distance_transform_edt(thresh)
localMax = peak_local_max(D, indices=False, min_distance=20,labels=thresh)
# perform a connected component analysis on the local peaks,
# using 8-connectivity, then appy the Watershed algorithm
markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
labels = watershed(-D, markers, mask=thresh)


# loop over the unique labels returned by the Watershed algorithm
#Pixels that have the same label value belong to the same object
for label in np.unique(labels):
	# if the label is zero, we are examining the 'background'so simply ignore it
	if label == 0:
		continue
	# otherwise, allocate memory for the label region and draw it on the mask
	mask = np.zeros(gray.shape, dtype="uint8")
	#sets pixels in foreground (hopefully clouds) to black
	mask[labels == label] = 255
	# detect contours in the mask and grab the largest one
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0]
	
	c = max(cnts, key=cv2.contourArea)
	
	# draw a circle enclosing the object
	((x, y), r) = cv2.minEnclosingCircle(c)
	cv2.circle(image, (int(x), int(y)), int(r), (0, 0, 0), -1)


'''
thresh = cv2.bitwise_not(thresh)
res = cv2.bitwise_and(image,image,mask = thresh)
cv2.imwrite('data/00af77b-cloud-detected.jpg')
#cv2.imshow("Resultant", res)
#cv2.waitKey(0)

