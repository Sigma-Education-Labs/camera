import fire_detection
import cv2
import time
from telemetry_main import unix_time_now, get_patch_coords
import subprocess
from datetime import datetime
import file_io
import os
from main import image_processing
from os.path import exists

test_dir = "test_images2/"
test_directory_enc = os.fsencode(test_dir)

def test_capture(tmp_dir):
    with open('error_log.txt', 'w') as f:    
        print(os.listdir(test_directory_enc))
        for file in os.listdir(test_directory_enc):
            filename = os.fsdecode(file)
            file_ext = os.path.splitext(filename)[1]
            print(test_dir + filename)
            if filename.endswith(".tif") or filename.endswith(".jpg"):
                process = subprocess.run(['cp', test_dir + filename, tmp_dir + "/ipxImage__" + datetime.now().strftime("%H%M%S") + file_ext], stdout=f, universal_newlines=True)
                print(filename)
                print(process)

                        
if __name__ == "__main__":
    start_time = time.time()
    tmp_dir = "/tmp"
    transfer_dir = "result"

    unix_time= unix_time_now()
    capture_error = test_capture(tmp_dir)
    print(capture_error)
    
    for file in os.listdir(tmp_dir):
        filename = os.fsdecode(file)
        if "ipxImage__" in filename:
            latest_img_path = tmp_dir + "/" + filename
            image_processing(latest_img_path, unix_time)
            file_io.downlink(transfer_dir)
            file_io.delete_image_file(latest_img_path)
        # process = subprocess.run(['rm', tmp_dir + "/ipxImage__*"])
        else:
            time.sleep(8) 
    print("--- %s seconds ---" % (time.time() - start_time))
