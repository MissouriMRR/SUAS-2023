import os
import cv2

def process_file(file_path):
    print("Processing file", file_path)
    image = cv2.imread(file_path)

# Path to the folder containing images
folder_path = "vision/unit_tests/test_images/standard_objects"

# List all files in the folder
all_files = os.listdir(folder_path)

for file_name in all_files:
    file_path = os.path.join(folder_path, file_name)
    process_file(file_path)
