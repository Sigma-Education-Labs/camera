import fire_detection
import cv2
import time
from telemetry_main import unix_time_now, get_patch_coords
import subprocess
from datetime import datetime
import file_io
from pathlib import Path
import os
import re
import json

def get_picture(camera_client, job_path):
    camera_exec = subprocess.Popen([camera_client, "camera", "--capture", job_path, "-t", "jpg", "-p", "1"], stdout=subprocess.PIPE)
    camera_response_str = camera_exec.communicate()[0].decode("utf-8")
    p = re.compile('{\'status\': .*')
    camera_response_jsons = p.findall(camera_response_str)
    if len(camera_response_jsons) == 0:
        print("Camera Error: " + camera_response_str)
        return
    q = re.compile('\'')
    camera_json_str = q.sub('"', camera_response_jsons[0])
    camera_json = json.loads(camera_json_str)
    print(camera_json)
    image_file = camera_json['value']
    try:
        if os.path.isfile(image_file):
            os.rename(image_file, job_path + "image.jpg" )
    except:
        pass

def image_processing(file_path, unix_time):
    test_image = cv2.imread(file_path)
    print(test_image.shape)
    print("Processing image {}".format(file_path))
    
    # Define the window size
    windowsize_r = 240
    windowsize_c = 180

    ''' Broad phase '''
    probability_in_img = fire_detection.image_contains_fire(test_image)
    if (probability_in_img>0.0):
        ''' Narrow phase '''
        # Crop out a patch from the image and detect if there is fire in it
        for r in range(0,test_image.shape[0] - windowsize_r, windowsize_r):
            for c in range(0,test_image.shape[1] - windowsize_c, windowsize_c):
                window = test_image[r:r+windowsize_r,c:c+windowsize_c]
                probability_in_window = fire_detection.image_contains_fire(window)
                if (probability_in_window > 0.5):
                    lat, long = get_patch_coords(r,c,unix_time)
                    print("Detected fire image patch from image {} on patch {}:{} with lat {} and long {} and prob {}".format(file_path, r, c, lat, long, probability_in_window))
                    file_io.add_to_downlink_file(lat, long, probability_in_window)
                    cv2.imwrite("result/fire_{}_{}_{}.jpg".format(r,c,unix_time),window)
        
if __name__ == "__main__":
    start_time = time.time()
    tmp_dir = "/tmp"
    transfer_dir = "result"


    # Create "result" dir if it doesn't exists
    isExist = os.path.exists(transfer_dir)
    if not isExist:
        os.makedirs(transfer_dir)

    # Create fires.txt file
    transfer_fle = Path(os.path.join(transfer_dir, "fires.txt"))
    transfer_fle.touch(exist_ok=True)

    # Create fires.txt file
    fle = Path(os.path.join("./", "fires.txt"))
    fle.touch(exist_ok=True)

    while True:
        unix_time = unix_time_now()
        get_picture("/usr/bin/es_rpiMgrClient", tmp_dir)
        latest_img_path = file_io.get_latest_image_path(tmp_dir)
        if latest_img_path:
            image_processing(latest_img_path, unix_time)
            file_io.downlink(transfer_dir)
            file_io.delete_image_file(latest_img_path)
        else:
            time.sleep(8)

    print("--- %s seconds ---" % (time.time() - start_time))