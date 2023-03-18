import cv2
import numpy as np

from nptyping import NDArray, Shape, UInt8
from vision.common.constants import Image, Contour, Hierarchy

from vision.competition_inputs.bottle_reader import load_bottle_info, BottleData
from vision.standard_object.odlc_image_processing import preprocess_std_odlc
from vision.standard_object.odlc_classify_shape import process_shapes
from vision.standard_object.odlc_text_detection import get_odlc_text
from vision.standard_object.odlc_colors import find_colors
from vision.deskew.camera_distances import get_coordinates
from vision.common.bounding_box import BoundingBox
from vision.common.odlc_characteristics import ODLCColor

from typing import Any

def flyover_pipeline():
    # Load the data for each bottle
    bottle_info: list[BottleData] = load_bottle_info()
    
    # The list of lists where all sightings of each ODLC will be stored
    saved_odlcs: list[list[BoundingBox]] = [[], [], [], [], []]
    
    # The list of BoundingBoxes where all potential emergent objects will be stored
    saved_humanoids: list[BoundingBox] = []
    
    # List of filenames for images already completed to prevent repeating work
    completed_images: list[str] = []
    
    # -- All below will be done within a loop that goes through all images. --
    
    original_image: Image = np.zeros((720, 1080, 3))
    image_path = "example123.jpg"
    
    # These are made up, but shouldn't be *too* far off from realistic values
    camera_parameters: dict(str, Any) = {
        "focal_length": 10,
        "rotation_deg": [10, 20, 30],
        "drone_coordinates": [50.80085, 21.42069],
        "altitude": 100
    }
    
    processed_image: Image = preprocess_std_odlc(original_image)
    
    contours: tuple[Contour, ...]
    hierarchy: Hierarchy
    contours, hierarchy = cv2.findContours(processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    shapes: list[BoundingBox] = process_shapes(list(contours), hierarchy, processed_image.shape[:2])
    
    for shape in shapes:
        shape.set_attribute("image_path", image_path)
        
        text_bounding: BoundingBox = get_odlc_text(original_image, shape)
        
        shape.set_attribute("text", text_bounding.get_attribute("text"))
        
        shape_color : ODLCColor
        text_color : ODLCColor
        shape_color, text_color = find_colors(original_image, text_bounding)
        
        shape.set_attribute("shape_color", shape_color)
        shape.set_attribute("text_color", text_color)
        
        coordinates: tuple[float, float] = get_coordinates(
            shape.get_center_coord,
            processed_image.shape,
            camera_parameters["focal_length"],
            camera_parameters["rotation_deg"],
            camera_parameters["drone_coordinates"],
            camera_parameters["altitude"]
        )
        
        shape.set_attribute("latitude", coordinates[0])
        shape.set_attribute("longitude", coordinates[1])
        
        # For each of the given bottle shapes, find the number of characteristics the
        #   discovered ODLC shape has in common with it
        all_matches: NDArray[Shape[5], UInt8] = np.zeros((5), dtype=UInt8)
        for index, info in bottle_info:
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
            bottle_index: int = np.where(all_matches == all_matches.max())[0][0]
            
            # Save the shape bounding box in its proper place
            saved_odlcs[bottle_index].append(shape)
    
    
    