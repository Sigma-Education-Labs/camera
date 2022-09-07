import fire_detection
import cv2
import time
from telemetry.telemetry_main import unix_time_now, get_patch_coords
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
        process = subprocess.run(['es_rpiMgrClient','camera', '--capture', tmp_dir, '-t', 'jpg', '-p', '1'], stdout=f,universal_newlines=True)
        return process

                        
if __name__ == "__main__":
    start_time = time.time()
    tmp_dir = "/tmp"
    transfer_dir = "/work/transfer"

    while True:
        unix_time = unix_time_now()
        capture_error = image_capture()
        print(capture_error)
        latest_img_path = file_io.get_latest_image_path(tmp_dir)
        if latest_img_path:
            image_processing(latest_img_path, unix_time)
            file_io.downlink(transfer_dir)
            file_io.delete_image_file(latest_img_path)
        else:
            time.sleep(8)

    print("--- %s seconds ---" % (time.time() - start_time))