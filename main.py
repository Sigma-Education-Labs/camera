from fire_detection import image_contains_fire
import cv2

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


for i in test_image_paths:
    test_image = cv2.imread(i)
    print("Fire on image {}: {}".format(i, image_contains_fire(test_image)))