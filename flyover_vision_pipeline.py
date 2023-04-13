"""Runs the necessary Vision code during the flyover stage of competition"""

from typing import Callable

import cv2

import vision.common.constants as consts
from vision.common.crop import crop_image

from vision.competition_inputs.bottle_reader import load_bottle_info, BottleData
from vision.common.bounding_box import BoundingBox
from vision.emergent_object.emergent_object import create_emergent_model
from vision.emergent_object.emergent_object_processing import pick_emergent_object

import vision.pipeline.standard_object as std
import vision.pipeline.emergent_object as emg
import vision.pipeline.pipeline_utils as utils


def flyover_pipeline(camera_data_path: str, state_path: str, output_path: str) -> None:
    """
    Finds all standard objects in each image in the input folder

    Parameters
    ----------
    camera_data_path: str
        The path to the json file containing the CameraParameters entries
    state_path: str
        A text file containing True if all images have been taken and False otherwise
    output_path: str
        The json file name and path to save the data in
    """

    # Load the data for each bottle
    bottle_info: list[BottleData] = load_bottle_info()

    # Load model
    emg_model: Callable[[consts.Image], str] = create_emergent_model()

    # List of filenames for images already completed to prevent repeating work
    completed_images: list[str] = []

    # The list where all sightings of ODLCs will be stored
    saved_odlcs: list[BoundingBox] = []

    # The list of BoundingBoxes where all potential emergent objects will be stored
    saved_humanoids: list[BoundingBox] = []

    all_images_taken: bool = False
    while not all_images_taken:
        image_parameters: dict[str, consts.CameraParameters] = utils.read_parameter_json(
            camera_data_path
        )

        for image_path in image_parameters.keys():
            if image_path not in completed_images:
                completed_images.append(image_path)

                image: consts.Image = cv2.imread(image_path)

                camera_parameters: consts.CameraParameters = image_parameters[image_path]

                saved_odlcs += std.find_standard_objects(image, camera_parameters, image_path)

                saved_humanoids += emg.find_humanoids(
                    image, emg_model, camera_parameters, image_path
                )

        all_images_taken = utils.flyover_finished(state_path)

    # Sort and output the locations of all ODLCs
    sorted_odlcs: list[list[BoundingBox]] = std.sort_odlcs(bottle_info, saved_odlcs)
    odlc_dict: consts.ODLC_Dict = std.create_odlc_dict(sorted_odlcs)
    utils.output_odlc_json(output_path, odlc_dict)

    # Find the emergent object and save the image
    emergent_object: BoundingBox = pick_emergent_object(saved_humanoids, odlc_dict)
    emergent_image: consts.Image = cv2.imread(emergent_object.get_attribute("image_path"))
    emergent_crop: consts.Image = crop_image(emergent_image, emergent_object)

    cv2.imwrite("emergent_object.jpg", emergent_crop)
