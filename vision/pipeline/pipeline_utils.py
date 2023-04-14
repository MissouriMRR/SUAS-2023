"""Pipeline functions not specific to either standard or emergent object"""

import json

import vision.common.constants as consts

from vision.common.bounding_box import BoundingBox

from vision.deskew.camera_distances import get_coordinates

from typing import TypeAlias

# Keys are image paths and values are the camera parameters for the image
FolderParameters: TypeAlias = dict[str, consts.CameraParameters]


def read_parameter_json(json_path: str) -> FolderParameters:
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
        data: FolderParameters = json.load(jfile)

    return data


def flyover_finished(state_path: str) -> bool:
    """
    Returns True if all photos have been taken and saved.
    The state_path file is a txt file containing only "True" if all images are taken

    Parameters
    ----------
    state_path: str
        The file holding a boolean

    Returns
    -------
    all_images_taken: bool
        True if all photos are saved
    """

    with open(state_path, encoding="UTF-8") as file:
        return str(file.read) == "True"


def set_generic_attributes(
    box: BoundingBox,
    image_path: str,
    image_shape: tuple[int, int] | tuple[int, int, int],
    camera_parameters: consts.CameraParameters,
) -> bool:
    """
    Sets BoundingBox attributes by reference. Attributes changed are image_path, latitude,
    and longitude.

    "Generic" because these attributes are important for any object

    Parameters
    ----------
    box: BoundingBox
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

    box.set_attribute("image_path", image_path)

    coordinates: tuple[float, float] | None = get_coordinates(
        box.get_center_coord(), image_shape, camera_parameters
    )

    if coordinates is None:
        return False

    box.set_attribute("latitude", coordinates[0])
    box.set_attribute("longitude", coordinates[1])

    return True


def output_odlc_json(output_path: str, odlc_dict: consts.ODLC_Dict) -> None:
    """
    Saves the ODLC_Dict to a file

    Parameters
    ----------
    output_path: str
        The json file name and path to save the data in
    odlc_dict: consts.ODLC_Dict
        The dictionary of ODLCs matched with bottles
    """

    with open(output_path, "w", encoding="UTF-8") as file:
        json.dump(odlc_dict, file, indent=4)
