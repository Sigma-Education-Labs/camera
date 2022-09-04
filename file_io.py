import subprocess
import os 

def downlink(transfer_dir):
    process = subprocess.run(["cp", "-fr", "fires.txt", transfer_dir])
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
    
    if valid_files:
        return max(valid_files, key=os.path.getmtime) 


def delete_image_file(img_path):
    process = subprocess.run(['rm', img_path])
    return process