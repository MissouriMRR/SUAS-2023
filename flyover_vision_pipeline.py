"""Runs the necessary Vision code during the flyover stage of competition"""

import cv2
import numpy as np

from nptyping import NDArray, Shape, UInt8
from typing import Callable
from vision.common.constants import Image, ScImage, Contour, Hierarchy, CameraParameters

from vision.competition_inputs.bottle_reader import load_bottle_info, BottleData
from vision.standard_object.odlc_image_processing import preprocess_std_odlc
from vision.standard_object.odlc_classify_shape import process_shapes
from vision.standard_object.odlc_text_detection import get_odlc_text
from vision.standard_object.odlc_colors import find_colors
from vision.deskew.camera_distances import get_coordinates
from vision.common.bounding_box import BoundingBox
from vision.common.odlc_characteristics import ODLCColor
from vision.emergent_object.emergent_object import create_emergent_model, detect_emergent_object

FLYOVER_IMAGES_PATH: str = ""
JSON_PATH: str = ""


def read_image_parameters(path: str) -> CameraParameters:
    raise NotImplementedError

def get_image_paths() -> list[str]:
    raise NotImplementedError


def flyover_pipeline() -> None:
    """
    Finds all standard objects in each image in the input folder
    """

    # Load the data for each bottle
    bottle_info: list[BottleData] = load_bottle_info()

    # Load model
    emg_model: Callable[[Image], str] = create_emergent_model()
    
    # List of filenames for images already completed to prevent repeating work
    completed_images: list[str] = []
    
    # The list where all sightings of ODLCs will be stored
    saved_odlcs: list[BoundingBox] = []

    # The list of BoundingBoxes where all potential emergent objects will be stored
    saved_humanoids: list[BoundingBox] = []

    # -- All below will be done within a loop that goes through all images. --
    # While not done:
        # Check for new images; for each new image:
            # Get camera parameters
            # Get standard and emergent objects
            # Save standard and emergent objects
    
    while True:
        for image_path in get_image_paths():
            if image_path not in completed_images:
                image: Image = cv2.imread(image_path)
                
                camera_parameters: CameraParameters = read_image_parameters(image_path)
                
                saved_odlcs += find_standard_objects(image, camera_parameters, image_path)
                
                saved_humanoids += find_emergent_objects(image, emg_model, camera_parameters, image_path)
                
                
        


    original_image: Image = np.zeros((720, 1080, 3))
    image_path = "example_name.jpg"

    # These are made up, but shouldn't be *too* far off from realistic values
    camera_parameters: CameraParameters = {
        "focal_length": 10,
        "rotation_deg": [10, 20, 30],
        "drone_coordinates": [50.80085, 21.42069],
        "altitude_f": 100,
    }

    # bottle_index: int = get_bottle_index(shape, bottle_info)

    #     if bottle_index is not -1:
    #         # Save the shape bounding box in its proper place



def find_standard_objects(
    original_image: Image,
    camera_parameters: CameraParameters,
    image_path: str
):
       
    found_odlcs: list[BoundingBox] = []

    # Run the image preprocessing
    processed_image: ScImage = preprocess_std_odlc(original_image)
    
    # Get the contours in the image
    contours: tuple[Contour, ...]
    hierarchy: Hierarchy
    contours, hierarchy = cv2.findContours(processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    shapes: list[BoundingBox] = process_shapes(list(contours), hierarchy, processed_image.shape[:2])

    for shape in shapes:
        # Set the shape attributes by reference. If successful, keep the shape
        if not set_shape_attributes(shape, image_path, original_image, camera_parameters):
            continue  # Skip the current shape and move on to the next
               
        found_odlcs.append(shape)
    
    return found_odlcs


def find_emergent_objects(
    original_image: Image,
    emg_model: Callable[[Image], str],
    camera_parameters: CameraParameters,
    image_path: str
):
    # The potential emergent objects found in the image
    found_humanoids: list[BoundingBox] = []

    detected_emergents: list[BoundingBox] = detect_emergent_object(original_image, emg_model)
    
    emergent: BoundingBox
    for emergent in detected_emergents:
        # Set the attributes by reference. If not successful, skip the current emergent
        if not set_generic_attributes(emergent, image_path, original_image.shape, camera_parameters):
            continue  # Skip the current emergent object and move on to the next
        
        found_humanoids.append(emergent)
    
    return found_humanoids
    


def get_bottle_index(shape: BoundingBox, bottle_info: list[BottleData]):
    """
    For the input ODLC BoundingBox, find the index of the bottle that it best matches.
    Returns -1 if no good match is found
    
    Parameters
    ----------
    shape: BoundingBox
        The bounding box of the shape. Attributes "text", "shape", "shape_color", and
        "text_color" must be set
    bottle_info: list[BottleData]
        The input info from bottle.json
    
    Returns
    -------
    bottle_index: int
        The index of the bottle from bottle.json that best matches the given ODLC
        Returns -1 if no good match is found
    """
    
    # For each of the given bottle shapes, find the number of characteristics the
    #   discovered ODLC shape has in common with it
    all_matches: NDArray[Shape[5], UInt8] = np.zeros((5), dtype=UInt8)
    index: int
    info: BottleData
    for index, info in enumerate(bottle_info):
        matches: int = 0
        if shape.get_attribute("text") == info["Letter"]:
            matches += 1

        if shape.get_attribute("shape") == info["Shape"]:
            matches += 1

        if shape.get_attribute("shape_color") == info["Shape_Color"]:
            matches += 1

        if shape.get_attribute("letter_color") == info["Letter_Color"]:
            matches += 1

        all_matches[int(index)] = matches

    # This if statement ensures that bad matches are ignored, and standards
    #    can be lowered
    if all_matches.max() > 2:
        # Gets the index of the first bottle with the most matches.
        # First [0] takes the first dimension, second [0] takes the first element
        return np.where(all_matches == all_matches.max())[0][0]
    else:
        return -1



def set_shape_attributes(
        shape: BoundingBox,
        image_path: str,
        original_image: Image,
        camera_parameters: CameraParameters
    ) -> bool:
    """
    Gets the attributes of a shape returned from process_shapes()
    Modifies `shape` in place
    
    Parameters
    ----------
    shape: BoundingBox
        The bounding box of the shape. Attribute "shape" must be set
    image_path: str
        The path for the image the bounding box is from
    camera_parameters: CameraParameters
        The details of how and where the photo was taken
    
    Returns
    -------
    attributes_found: bool
        Returns true if all attributes were successfully found
    """
    if shape.get_attribute("shape") is None:
        return False
    
    text_bounding: BoundingBox = get_odlc_text(original_image, shape)

    # If no text is found, we can't do find_colors()
    if not text_bounding.get_attribute("text"):
        return False

    shape.set_attribute("text", text_bounding.get_attribute("text"))

    shape_color: ODLCColor
    text_color: ODLCColor
    shape_color, text_color = find_colors(original_image, text_bounding)

    shape.set_attribute("shape_color", shape_color)
    shape.set_attribute("text_color", text_color)
    
    # Modifies by reference
    if not set_generic_attributes(shape, image_path, original_image.shape, camera_parameters):
        return False
    
    return True

def set_generic_attributes(
        object: BoundingBox,
        image_path: str,
        image_shape: tuple[int, int] | tuple[int, int, int],
        camera_parameters: CameraParameters
    ) -> None:
    
    object.set_attribute("image_path", image_path)

    coordinates: tuple[float, float] | None = get_coordinates(
        object.get_center_coord(), image_shape, camera_parameters
    )
    
    object.set_attribute("latitude", coordinates[0])
    object.set_attribute("longitude", coordinates[1])
    
    if coordinates is None:
        return False
    
    return True