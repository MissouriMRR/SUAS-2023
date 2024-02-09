"""Runs the necessary Vision code during the flyover stage of competition"""

from typing import Callable
from ctypes import c_bool
from multiprocessing.sharedctypes import SynchronizedBase  # pylint: disable=unused-import

import time
import cv2

import vision.common.constants as consts
from vision.common.crop import crop_image

from vision.competition_inputs.bottle_reader import load_bottle_info, BottleData
from vision.common.bounding_box import BoundingBox
from vision.emergent_object.emergent_object import create_emergent_model
from vision.emergent_object.emergent_object_processing import pick_emergent_object

import vision.pipeline.standard_pipeline as std_obj
import vision.pipeline.emergent_pipeline as emg_obj
import vision.pipeline.pipeline_utils as pipe_utils


def flyover_pipeline(
    camera_data_path: str, capture_status: "SynchronizedBase[c_bool]", output_path: str
) -> None:
    """
    Finds all standard objects in each image in the input folder

    Parameters
    ----------
    camera_data_path: str
        The path to the json file containing the CameraParameters entries
    capture_status: SynchronizedBase[c_bool]
        A text file containing True if all images have been taken and False otherwise
    output_path: str
        The json file name and path to save the data in
    """

    # Load the data for each bottle
    bottle_info: dict[str, BottleData] = load_bottle_info()

    # Load model
    emg_model: Callable[[consts.Image], str] = create_emergent_model()

    # List of filenames for images already completed to prevent repeating work
    completed_images: list[str] = []

    # The list where all sightings of ODLCs will be stored
    saved_odlcs: list[BoundingBox] = []

    # The list of BoundingBoxes where all potential emergent objects will be stored
    saved_humanoids: list[BoundingBox] = []

    # Wait for and process unfinished images until no more images are being taken
    all_images_taken: c_bool = c_bool(False)
    while not all_images_taken:
        # Wait to check the file instead of spamming it
        time.sleep(1)

        # Check if all images have been taken
        all_images_taken = capture_status.value  # type: ignore

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

                # Append all discovered standard objects to the list of saved odlcs
                saved_odlcs += std_obj.find_standard_objects(image, camera_parameters, image_path)

                # Append all discovered humanoids to the list of saved humanoids
                saved_humanoids += emg_obj.find_humanoids(
                    emg_model, image, camera_parameters, image_path
                )

    # Sort and output the locations of all ODLCs
    sorted_odlcs: list[list[BoundingBox]] = std_obj.sort_odlcs(bottle_info, saved_odlcs)
    odlc_dict: consts.ODLCDict = std_obj.create_odlc_dict(sorted_odlcs)
    pipe_utils.output_odlc_json(output_path, odlc_dict)

    # Pick the emergent object and save the image cropped in on the emergent object
    if len(saved_humanoids) > 0:
        emergent_object: BoundingBox = pick_emergent_object(saved_humanoids, odlc_dict)
        emergent_image: consts.Image = cv2.imread(emergent_object.get_attribute("image_path"))
        emergent_crop: consts.Image = crop_image(emergent_image, emergent_object)

        cv2.imwrite("emergent_object.jpg", emergent_crop)
