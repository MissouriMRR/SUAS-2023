import cv2
import numpy as np
import json

from nptyping import NDArray, Shape, UInt8
from typing import Callable
import vision.common.constants as consts

from vision.competition_inputs.bottle_reader import BottleData
from vision.common.bounding_box import BoundingBox
from vision.common.odlc_characteristics import ODLCColor

from vision.emergent_object.emergent_object import detect_emergent_object

from vision.standard_object.odlc_image_processing import preprocess_std_odlc
from vision.standard_object.odlc_classify_shape import process_shapes
from vision.standard_object.odlc_text_detection import get_odlc_text
from vision.standard_object.odlc_colors import find_colors

from vision.deskew.camera_distances import get_coordinates


def set_generic_attributes(
    object: BoundingBox,
    image_path: str,
    image_shape: tuple[int, int] | tuple[int, int, int],
    camera_parameters: consts.CameraParameters,
) -> None:
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


def create_odlc_dict(sorted_odlcs: list[list[BoundingBox]]) -> consts.ODLC_Dict:
    """
    
    
    """
    
    odlc_dict: consts.ODLC_Dict = {}
    
    for i, bottle in enumerate(sorted_odlcs):
        coords_list: list[tuple[int, int]] = []
        
        for shape in bottle:
            coords_list.append(
                (shape.get_attribute("latitude"), shape.get_attribute("longitude"))
            )
        
        coords_array = np.array(coords_list)
        
        average_coord = np.average(coords_array, axis=0)
                
        odlc_dict[i] = {"latitude": average_coord[0], "longitude": average_coord[1]}
    
    return odlc_dict