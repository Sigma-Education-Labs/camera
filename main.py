import fire_detection
import cv2
import time
from telemetry.telemetry_main import get_obc_telemetry, get_patch_coords
import subprocess
from datetime import datetime
import file_io

def image_processing(file_path, unix_time):
    test_image = cv2.imread(file_path)
    print(test_image.shape)
    print("Processing image {}".format(file_path))
    
    # Define the window size
    windowsize_r = 240
    windowsize_c = 180

    ''' Broad phase '''
    if (fire_detection.image_contains_fire(test_image)):
        ''' Narrow phase '''
        # Crop out a patch from the image and detect if there is fire in it
        for r in range(0,test_image.shape[0] - windowsize_r, windowsize_r):
            for c in range(0,test_image.shape[1] - windowsize_c, windowsize_c):
                window = test_image[r:r+windowsize_r,c:c+windowsize_c]
                if (fire_detection.image_contains_fire(window)):
                    lat, long = get_patch_coords(r,c,unix_time)
                    print("Detected fire image patch from image {} on patch {}:{} with lat {} and long {}".format(file_path, r, c, lat, long))
                    file_io.add_to_downlink_file(lat, long)

def image_capture():
    with open('error_log.txt', 'w') as f:
        if testing:
            process = subprocess.run(['cp','test_images/ipxImage__124219.tif', tmp_dir + "/ipxImage__" + datetime.now().strftime("%H%M%S") + ".tif"], stdout=f,universal_newlines=True)
            # process = subprocess.run(['cp','test_images/Fire2.jpg', "/tmp/ipxImage__" + datetime.now().strftime("%H%M%S") + ".jpg"], stdout=f,universal_newlines=True)
        else:
            process = subprocess.run(['es_rpiMgrClient','camera', '--capture', tmp_dir, '-t', 'jpg', '-p', '1'], stdout=f,universal_newlines=True)
        return process

                        
if __name__ == "__main__":
    start_time = time.time()
    testing = True
    tmp_dir = "/tmp"
    transfer_dir = "/work/transfer"

    while True:
        unix_time, opmode = get_obc_telemetry()
        if opmode == 4:
            #satellite is in payload mode so call payload functions
            capture_error = image_capture()
            print(capture_error)
            latest_img_path = file_io.get_latest_image_path(tmp_dir)
            if latest_img_path:
                image_processing(latest_img_path, unix_time)
                file_io.downlink(transfer_dir)
                file_io.delete_image_file(latest_img_path)
        else:
            time.sleep(30)
            break
    print("--- %s seconds ---" % (time.time() - start_time))