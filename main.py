from fire_detection import image_contains_fire
import cv2
import time
from telemetry.telemetry_main import get_obc_telemetry, get_patch_coords
import subprocess
from datetime import datetime
import os

testing = True
tmp_dir = "/tmp"
transfer_dir = "/work/transfer"

def downlink():
    with open('error_log.txt', 'w') as f:
        process = subprocess.run(['mv','fires.txt', transfer_dir], stdout=f,universal_newlines=True)
    return process

def add_to_downlink_file(lat, long):
    print("Detected fire on Lat: {} and Long: {}".format(lat, long))
    f = open("fires.txt", "a")
    f.write("{} {}\n".format(lat, long))
    f.close()

def get_latest_image_path(dirpath, valid_extensions=("raw", "jpg", "bmp", "tif", "tiff")):
    """
    Get the latest image file in the given directory
    """

    # get filepaths of all files and dirs in the given dir
    valid_files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
    # filter out directories, no-extension, and wrong extension files
    valid_files = [f for f in valid_files if '.' in f and \
        f.rsplit('.',1)[-1] in valid_extensions and os.path.isfile(f)]

    if not valid_files:
        raise ValueError("No valid images in %s" % dirpath)

    return max(valid_files, key=os.path.getmtime) 

def image_processing(file_path, unix_time):
    test_image = cv2.imread(file_path)
    print(test_image.shape)
    print("Processing image {}".format(file_path))
    
    # Define the window size
    windowsize_r = 240
    windowsize_c = 180

    ''' Broad phase '''
    if (image_contains_fire(test_image)):
        ''' Narrow phase '''
        # Crop out a patch from the image and detect if there is fire in it
        for r in range(0,test_image.shape[0] - windowsize_r, windowsize_r):
            for c in range(0,test_image.shape[1] - windowsize_c, windowsize_c):
                window = test_image[r:r+windowsize_r,c:c+windowsize_c]
                if (image_contains_fire(window)):
                    lat, long = get_patch_coords(r,c,unix_time)
                    print("Detected fire image patch from image {} on patch {}:{} with lat {} and long {}".format(file_path, r, c, lat, long))
                    add_to_downlink_file(lat, long)

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

    while True:
        unix_time, opmode = get_obc_telemetry()
        if(opmode == 4):
            #satellite is in payload mode so call payload functions
            capture_error = image_capture()
            print(capture_error)
            latest_img_path = get_latest_image_path(tmp_dir)
            # time.sleep(8) #wait for image to be sent to dir
            image_processing(latest_img_path, unix_time)
            downlink()
        else:
            time.sleep(30)
            break
    print("--- %s seconds ---" % (time.time() - start_time))