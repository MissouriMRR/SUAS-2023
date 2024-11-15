"""This tests an image and sees what objects are detected and their attributes.
Also saves the cropped image of the object."""

from typing import Callable

import logging
import cv2

import vision.common.constants as consts
from vision.common.crop import crop_image

from vision.competition_inputs.bottle_reader import load_bottle_info, BottleData
from vision.common.bounding_box import BoundingBox
from vision.emergent_object.emergent_object import create_emergent_model

import vision.pipeline.standard_pipeline as std_obj
import vision.pipeline.emergent_pipeline as emg_obj
import vision.pipeline.pipeline_utils as pipe_utils


def flyover_pipeline(camera_data_path: str) -> None:
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

    # Load in the json containing the camera data
    image_parameters: dict[str, consts.CameraParameters] = pipe_utils.read_parameter_json(
        camera_data_path
    )
    print(image_parameters)
    # Loop through all images in the json - if it hasn't been processed, process it
    for image_path in image_parameters.keys():
        print(image_path)
        if image_path not in completed_images:
            # Save the image path as completed so it isn't processed again
            completed_images.append(image_path)

            # Load the image to process
            print("Loading image")
            image: consts.Image = cv2.imread(f"images/{image_path}")

            # Get the camera parameters from the loaded parameter file
            print("Loading camera parameters")
            camera_parameters: consts.CameraParameters = image_parameters[image_path]

            # Append all discovered standard objects to the list of saved odlcs
            print("Finding standard objects")
            saved_odlcs += std_obj.find_standard_objects(
                image, camera_parameters, f"images/{image_path}"
            )

            # Append all discovered humanoids to the list of saved humanoids
            print("Finding emergent objects")
            saved_humanoids += emg_obj.find_humanoids(
                emg_model, image, camera_parameters, f"images/{image_path}"
            )

    print("All images have been processed.")
    print(f"ODLC: {saved_odlcs}")
    print(f"Humanoids: {saved_humanoids}")
    # Sort and output the locations of all ODLCs
    sorted_odlcs: list[list[BoundingBox]] = std_obj.sort_odlcs(bottle_info, saved_odlcs)
    odlc_dict: consts.ODLCDict = std_obj.create_odlc_dict(sorted_odlcs)
    print(odlc_dict)

    j = 0
    for odlc in saved_odlcs:
        j += 1
        print(f"Text: {odlc.get_attribute('text_color')} {odlc.get_attribute('text')}")
        print(f"Shape: {odlc.get_attribute('shape_color')} {odlc.get_attribute('shape')}")
        odlc_image: consts.Image = cv2.imread(odlc.get_attribute("image_path"))
        odlc_crop: consts.Image = crop_image(odlc_image, odlc)

        cv2.imwrite(f"odlc_object{j}.jpg", odlc_crop)

    # Pick the emergent object and save the image cropped in on the emergent object
    if len(saved_humanoids) > 0:
        i = 0
        for humanoid in saved_humanoids:
            i += 1
            emergent_image: consts.Image = cv2.imread(humanoid.get_attribute("image_path"))
            emergent_crop: consts.Image = crop_image(emergent_image, humanoid)

            cv2.imwrite(f"emergent_object{i}.jpg", emergent_crop)


logging.basicConfig(filename="/dev/stdout", level=logging.INFO)
# flyover_pipeline("flight/data/camera.json")
flyover_pipeline("camera.json")
