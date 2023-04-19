"""Runs vision code to find judges during an airdrop"""

from typing import Callable

import time
import cv2

import vision.common.constants as consts

from vision.common.bounding_box import BoundingBox
from vision.emergent_object.emergent_object import create_emergent_model
from vision.emergent_object.emergent_object_processing import calc_emerg_obj_min_dist

import vision.pipeline.emergent_pipeline as emg_obj
import vision.pipeline.pipeline_utils as pipe_utils

# The furthest a judge can move between images in feet
MAX_JUDGE_MOVEMENT_F: float = 15

def airdrop_pipeline(camera_data_path: str, state_path: str, output_path: str) -> None:
    """
    
    """
    
    # Load model
    emg_model: Callable[[consts.Image], str] = create_emergent_model()
    
    # List of filenames for images already completed to prevent repeating work
    completed_images: list[str] = []
    
    # Wait for and process unfinished images until no more images are being taken
    all_images_taken: bool = False
    while not all_images_taken:
        # Wait to check the files instead of spamming it
        time.sleep(0.1)

        # Check if all images have been taken
        all_images_taken = pipe_utils.flyover_finished(state_path)

        # Load in the json containing the camera data
        image_parameters: dict[str, consts.CameraParameters] = pipe_utils.read_parameter_json(
            camera_data_path
        )
        
        prev_data: list[BoundingBox]

        # Loop through all images in the json - if it hasn't been processed, process it
        for image_path in image_parameters.keys():
            if image_path not in completed_images:
                # Save the image path as completed so it isn't processed again
                completed_images.append(image_path)

                # Load the image to process
                image: consts.Image = cv2.imread(image_path)

                # Get the camera parameters from the loaded parameter file
                camera_parameters: consts.CameraParameters = image_parameters[image_path]

                # Find potential judges in the image
                current_data = emg_obj.find_humanoids(
                    image, emg_model, camera_parameters, image_path
                )
                
                judges: list[BoundingBox] = compare_data(prev_data, current_data)
                
                judge_dict: consts.ODLC_Dict = create_judge_dict(judges)
                
                pipe_utils.output_odlc_json(output_path, judge_dict)
                
                prev_data = current_data


def compare_data(prev_data: list[BoundingBox], current_data: list[BoundingBox]) -> list[BoundingBox]:
    judges: list[BoundingBox] = []
    
    for prev_detection in prev_data:
        min_distance = calc_emerg_obj_min_dist(current_data, prev_detection)
        
        if min_distance < MAX_JUDGE_MOVEMENT_F:
            judges.append(prev_detection)
    
    return judges


def create_judge_dict(judges: list[BoundingBox]) -> None:
    judge_dict: consts.ODLC_Dict
    for i, judge in enumerate(judges):
        judge_dict[str(i)] = {
            "latitude": judge.get_attribute("latitude"), 
            "longitude": judge.get_attribute("latitude")
        }
    
    return judge_dict