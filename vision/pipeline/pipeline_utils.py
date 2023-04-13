"""Pipeline functions not specific to either standard or emergent object"""

import numpy as np
import json

import vision.common.constants as consts

from vision.common.bounding_box import BoundingBox

from vision.deskew.camera_distances import get_coordinates


def read_parameter_json(json_path: str) -> dict[str, consts.CameraParameters]:
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
        data: dict[str, consts.CameraParameters] = json.load(jfile)

    return data


def flyover_finished(state_path: str) -> bool:
    """
    Returns True if all photos have been taken and saved

    Parameters
    ----------
    state_path: str
        The file holding a boolean
    """

    with open(state_path) as file:
        return str(file.read) == "True"


def set_generic_attributes(
    object: BoundingBox,
    image_path: str,
    image_shape: tuple[int, int] | tuple[int, int, int],
    camera_parameters: consts.CameraParameters,
) -> bool:
    """
    Sets BoundingBox attributes by reference. Attributes changed are image_path, latitude, and longitude
    "Generic" because these attributes are important for any object

    Parameters
    ----------
    object: BoundingBox
        The bounding box of the object to which the attributes will be set
    image_path: str
        The path for the image the bounding box is from
    image_shape : tuple[int, int, int] | tuple[int, int]
        The shape of the image (returned by `image.shape` when image is a numpy image array)
    camera_parameters: CameraParameters
        The details of how and where the photo was taken

    Returns
    -------
    attributes_found: bool
        Returns true if all attributes were successfully found
    """

    object.set_attribute("image_path", image_path)

    coordinates: tuple[float, float] | None = get_coordinates(
        object.get_center_coord(), image_shape, camera_parameters
    )

    if coordinates is None:
        return False

    object.set_attribute("latitude", coordinates[0])
    object.set_attribute("longitude", coordinates[1])

    return True


def output_odlc_json(output_path: str, dict_data: consts.ODLC_Dict) -> None:
    """
    Saves the ODLC_Dict to a file
    """