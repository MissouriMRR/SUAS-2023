"""Runs emergent object code for testing purposes"""

from typing import Callable, Final

import time
import numpy as np
import cv2

import vision.common.constants as consts

from vision.common.bounding_box import BoundingBox
from vision.emergent_object.emergent_object import create_emergent_model

import vision.pipeline.emergent_pipeline as emg_obj
import vision.pipeline.pipeline_utils as pipe_utils


# The location to pretend the emergent object is at for the test
# Located in the golf course
# https://www.google.com/maps/place/37%C2%B056'53.0%22N+91%C2%B047'02.9%22W/@37.9480567,-91.7847826,180m/data=!3m1!1e3!4m4!3m3!8m2!3d37.9480556!4d-91.7841389?entry=ttu
TEST_LATITUDE: Final[float] = +(37 + 56 / 60 + 53.00 / 60 / 60)
TEST_LONGITUDE: Final[float] = -(91 + 47 / 60 + 02.90 / 60 / 60)
# Circumference of Earth through poles is 40,007,863 m
TEST_AREA_SIZE: Final[float] = (
    100 / 3.28084 * (360 / 40_007_863)
)  # 100 feet north-south, smaller east-west
TEST_ALTITUDE: Final[float] = 100 / 3.28084  # 100 feet


# Disable duplicate code checking because the flyover pipeline is similar
# pylint: disable=duplicate-code
def emg_integration_pipeline(camera_data_path: str, state_path: str, output_path: str) -> None:
    """
    Runs the emergent object integration test - finds the emergent object in a set of images
    Saves a single coordinate in the json file output_path, with the key "0".

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

        detected_emergents: list[BoundingBox] = []

        image_path: str
        # Loop through all images in the json - if it hasn't been processed, process it
        for image_path in image_parameters.keys():
            if image_path not in completed_images:
                # Save the image path as completed so it isn't processed again
                completed_images.append(image_path)

                # Load the image to process
                image: consts.Image = cv2.imread(image_path)

                # Get the camera parameters from the loaded parameter file
                camera_parameters: consts.CameraParameters = image_parameters[image_path]

                # Find emergent objects in the image
                img_detections: list[BoundingBox] = emg_obj.find_humanoids(
                    emg_model, image, camera_parameters, image_path
                )

                detected_emergents += img_detections

        # Get an array of all locations of detections
        location_array = np.zeros((len(detected_emergents), 2), dtype=np.float64)
        detection: BoundingBox
        for i, detection in enumerate(detected_emergents):
            latitude: float = detection.get_attribute("latitude")
            longitude: float = detection.get_attribute("longitude")

            location = np.array([latitude, longitude], dtype=np.float64)

            location_array[i] = location

        # Average the locations together
        avg_location = np.mean(location_array, axis=0)

        # Create the dictionary which will be saved as a json
        output_dict: consts.ODLCDict = {
            "0": {"latitude": avg_location[0], "longitude": avg_location[1]},
        }

        pipe_utils.output_odlc_json(output_path, output_dict)
