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
    Finds all judges in the images in the camera_data_path json file.

    Unlike with the Flyover Vision Pipeline, the output_path json will be updated continuously.

    Parameters
    ----------
    camera_data_path: str
        The path to the json file containing the CameraParameters entries
    state_path: str
        A text file containing True if all images have been taken and False otherwise
    output_path: str
        The json file name and path to save the data in
    """

    # Load model
    emg_model: Callable[[consts.Image], str] = create_emergent_model()

    # List of filenames for images already completed to prevent repeating work
    completed_images: list[str] = []


    prev_data: list[BoundingBox] = []
    first_detection: bool = True
    
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
                
                if not first_detection:
                    judges: list[BoundingBox] = compare_data(prev_data, current_data)

                    judge_dict: consts.ODLC_Dict = create_judge_dict(judges)

                    pipe_utils.output_odlc_json(output_path, judge_dict)

                prev_data = current_data
                
                first_detection = False


def compare_data(
    prev_data: list[BoundingBox], current_data: list[BoundingBox]
) -> list[BoundingBox]:
    """ "
    Compares humanoid detections between two images to filter out false positive detections

    Parameters
    ----------
    prev_data: list[BoundingBox]
        The detected humanoids from the previous image being considered
    current_data: list[BoundingBox]
        The detected humanoids from the current image

    Returns
    -------
    judges: list[BoundingBox]
        The subset of current_data that is likely to be judges
    """

    judges: list[BoundingBox] = []

    for current_detection in current_data:
        min_distance = calc_emerg_obj_min_dist(prev_data, current_detection)

        # Ensures that a detection in the current image that was not in the previous image
        #   will be ignored
        if min_distance < MAX_JUDGE_MOVEMENT_F:
            judges.append(current_detection)

    return judges


def create_judge_dict(judges: list[BoundingBox]) -> consts.ODLC_Dict:
    """
    Creates an ODLC_Dict object that represents where the judges probably are

    Parameters
    ----------
    judges: list[BoundingBox]
        The list of bounding boxes of judges

    Returns
    -------
    judge_dict: ODLC_Dict
        The dictionary of locations of judges.
        The keys are indices in string form and are meaningless.
    """

    judge_dict: consts.ODLC_Dict = {}
    for i, judge in enumerate(judges):
        judge_dict[str(i)] = {
            "latitude": judge.get_attribute("latitude"),
            "longitude": judge.get_attribute("latitude"),
        }

    return judge_dict
