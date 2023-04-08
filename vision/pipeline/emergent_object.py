from typing import Callable
import vision.common.constants as consts

from vision.common.bounding_box import BoundingBox

from vision.emergent_object.emergent_object import detect_emergent_object


from vision.pipeline.pipeline_utils import *

def find_humanoids(
    emg_model: Callable[[consts.Image], str],
    original_image: consts.Image,
    camera_parameters: consts.CameraParameters,
    image_path: str
) -> list[BoundingBox]:
    """
    Finds all candidate emergent objects in a given image
    
    Parameters
    ----------
    original_image: Image
        The image to run human detection on
    emg_model: Callable[[Image], str]
        The model which is being used for object detection/classification
    camera_parameters: CameraParameters
        The details of how and where the photo was taken
    image_path: str
        The path for the image the bounding box is from
    
    Returns
    -------
    found_humanoids: list[BoundingBox]
        The list of bounding boxes of detected humanoids
    """

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
