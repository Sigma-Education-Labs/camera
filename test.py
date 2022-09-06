import fire_detection
import cv2
import time
from telemetry.telemetry_main import get_obc_telemetry, get_patch_coords
import subprocess
from datetime import datetime
import file_io
import os
from main import image_processing

test_dir = "test_images2/"
test_directory_enc = os.fsencode(test_dir)

def test_capture(tmp_dir):
    with open('error_log.txt', 'w') as f:    
        for file in os.listdir(test_directory_enc):
            filename = os.fsdecode(file)
            file_ext = os.path.splitext(filename)[1]
            process = subprocess.run(['cp', test_dir + filename, tmp_dir + "/ipxImage__" + datetime.now().strftime("%H%M%S") + file_ext], stdout=f, universal_newlines=True)
        return process

                        
if __name__ == "__main__":
    start_time = time.time()
    tmp_dir = "/tmp"
    transfer_dir = "/work/transfer"

    while True:
        unix_time, opmode = get_obc_telemetry()
        if opmode == 4:
            #satellite is in payload mode so call payload functions
            capture_error = test_capture(tmp_dir)
            print(capture_error)
            test_dir = "test_images/"
            test_directory_enc = os.fsencode("./test_images/")
    
            for file in os.listdir(tmp_dir):
                filename = os.fsdecode(file)

                if "ipxImage__" in filename:
                    latest_img_path = tmp_dir + "/" + filename
                    image_processing(latest_img_path, unix_time)
                    file_io.downlink(transfer_dir)
                    file_io.delete_image_file(latest_img_path)

            # process = subprocess.run(['rm', tmp_dir + "/ipxImage__*"])
            break    
        else:
            time.sleep(30)
            break
    print("--- %s seconds ---" % (time.time() - start_time))