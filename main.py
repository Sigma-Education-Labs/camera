from fire_detection import image_contains_fire
import cv2
import datetime
import time

start_time = time.time()

test_image_paths = [
    "test_images/clouds.jpg",
    "test_images/fire.jpg",
    "test_images/Fire1.jpg",
    "test_images/Fire2.jpg",
    "test_images/Fire3.jpeg",
    "test_images/flame.jpg",
    "test_images/hh.jpeg",
    "test_images/imh.jpeg",
    "test_images/NoFire1.jpg",
    "test_images/NoFire2.jpg",
    "test_images/watermelon.jpg",
    "test_images/blue-bird.png",
    "test_images/ipxImage__124219.tif",
    "test_images/2.tif",
]

def downlink(lat, long):
    print("Detected fire on Lat: {} and Long: {}".format(lat, long))

for i in test_image_paths:
    test_image = cv2.imread(i)
    print(test_image.shape)
    print("Processing image {}".format(i))
    
    # Define the window size
    windowsize_r = 240
    windowsize_c = 180

    # windowsize_r = 180
    # windowsize_c = 135

    ''' Broad phase '''
    if (image_contains_fire(test_image)):
        ''' Narrow phase '''

        # Crop out a patch from the image and detect if there is fire in it
        for r in range(0,test_image.shape[0] - windowsize_r, windowsize_r):
            for c in range(0,test_image.shape[1] - windowsize_c, windowsize_c):
                # print("Processing image patch {}:{}".format(r, c))
                window = test_image[r:r+windowsize_r,c:c+windowsize_c]
                if (image_contains_fire(window)):
                    lat = 0.0
                    long = 0.0
                    print("Detected fire image patch from image {} on patch {}:{} with lat {} and long {}".format(i, r, c, lat, long))
                    downlink(lat, long)

print("--- %s seconds ---" % (time.time() - start_time))