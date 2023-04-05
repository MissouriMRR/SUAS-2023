import cv2
import numpy as np
import json

from nptyping import NDArray, Shape, UInt8
from typing import Callable
from vision.common.constants import Image, ScImage, Contour, Hierarchy, CameraParameters

from vision.competition_inputs.bottle_reader import BottleData
from vision.common.bounding_box import BoundingBox
from vision.common.odlc_characteristics import ODLCColor

from vision.emergent_object.emergent_object import detect_emergent_object

from vision.standard_object.odlc_image_processing import preprocess_std_odlc
from vision.standard_object.odlc_classify_shape import process_shapes
from vision.standard_object.odlc_text_detection import get_odlc_text
from vision.standard_object.odlc_colors import find_colors

from vision.deskew.camera_distances import get_coordinates


def read_image_parameters(json_path: str) -> dict[str, CameraParameters]:
    """
    Will read in the data from the given json file and return it as a python dict.

    Parameters
    ----------
    json_path : str
        The path of a valid json file, assumed to have data in the same format as return type.

    Returns
    -------
    data : dict[str, CameraParameters]
        The python dict version of the data from the given json file.
    """
    with open(json_path, encoding="utf-8") as jfile:
        data: dict[str, CameraParameters] = json.load(jfile)

    return data


def find_standard_objects(
    original_image: Image, camera_parameters: CameraParameters, image_path: str
) -> list[BoundingBox]:
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
    image_path: str,
) -> list[BoundingBox]:
    # The potential emergent objects found in the image
    found_humanoids: list[BoundingBox] = []

    detected_emergents: list[BoundingBox] = detect_emergent_object(original_image, emg_model)

    emergent: BoundingBox
    for emergent in detected_emergents:
        # Set the attributes by reference. If not successful, skip the current emergent
        if not set_generic_attributes(
            emergent, image_path, original_image.shape, camera_parameters
        ):
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
    shape: BoundingBox, image_path: str, original_image: Image, camera_parameters: CameraParameters
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
    camera_parameters: CameraParameters,
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
