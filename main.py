from fire_detection import image_contains_fire
import cv2
import datetime
import time
from telemetry.telemetry_main import get_obc_telemetry, get_patch_coords
import subprocess
from sys import stdout

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
    f = open("fires.txt", "a")
    f.write("{} {}\n".format(lat, long))
    f.close()
    
def image_processing(unix_time):

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
                        lat, long = get_patch_coords(r,c,unix_time)
                        print("Detected fire image patch from image {} on patch {}:{} with lat {} and long {}".format(i, r, c, lat, long))
                        downlink(lat, long)

def image_capture():
    with open('error_log.txt', 'w') as f:
        process = subprocess.Popen(['es_rpiMgrClient','camera', '--capture', '/tmp', '-t', 'jpg', '-p', '1'], stdout=f,universal_newlines=True)
        return process

                        
if __name__ == "__main__":
    start_time = time.time()

    while True:
        unix_time, opmode = get_obc_telemetry()
        if(opmode == 4):
            #satellite is in payload mode so call payload functions
            capture_error = image_capture()
            print(capture_error)
            time.sleep(8) #wait for image to be sent to dir
            image_processing(unix_time)
        else:
            time.sleep(30)
            break
    print("--- %s seconds ---" % (time.time() - start_time))