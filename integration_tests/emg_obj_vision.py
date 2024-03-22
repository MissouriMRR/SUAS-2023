"""Contains the emergent object integration test pipeline."""

from ctypes import c_bool
from multiprocessing.sharedctypes import SynchronizedBase
import time
from typing import Callable

import cv2
from nptyping import NDArray, Shape
import numpy as np

import vision.common.constants as consts

from vision.common.bounding_box import BoundingBox
from vision.emergent_object.emergent_object import create_emergent_model

import vision.pipeline.emergent_pipeline as emg_obj
import vision.pipeline.pipeline_utils as pipe_utils


# Disable duplicate code checking because the flyover pipeline is similar
# pylint: disable=duplicate-code
def emg_integration_pipeline(
    camera_data_path: str, capture_status: "SynchronizedBase[c_bool]", output_path: str
) -> None:
    """
    Runs the emergent object integration test - finds the emergent object in a set of images
    Saves a single coordinate in the json file output_path, with the key "0".

    Parameters
    ----------
    camera_data_path: str
        The path to the json file containing the CameraParameters entries
    capture_status: SynchronizedBase[c_bool]
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
        all_images_taken = capture_status.value  # type: ignore

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

        # Gather the detections into a numpy array
        location_array: NDArray[Shape["*, 2"]] = np.zeros(
            (len(detected_emergents), 2), dtype=np.float64
        )
        detection: BoundingBox
        for i, detection in enumerate(detected_emergents):
            latitude: float = detection.get_attribute("latitude")
            longitude: float = detection.get_attribute("longitude")

            location: consts.Point = np.array([latitude, longitude], dtype=np.float64)

            location_array[i] = location

        # Average the locations together
        avg_location: consts.Point = np.mean(location_array, axis=0)

        # Create the dictionary which will be saved as a json
        output_dict: consts.ODLCDict = {
            "0": {"latitude": avg_location[0], "longitude": avg_location[1]},
        }

        pipe_utils.output_odlc_json(output_path, output_dict)
