"""
Contains functions relating to the identification and
classification of the emergent object within an image.

NOTE: Pytorch types are a bit of a pain, so not all types in here
are totally acurrate. Tried to make good approximations for types where
possible, or eliminate variables that couldn't be figured out.
"""

from typing import Any, Callable, TypedDict

import cv2
import torch

from vision.common.bounding_box import BoundingBox, ObjectType, Vertices, tlwh_to_vertices
from vision.common.constants import Image


EMG_MODEL_PATH = "vision/emergent_object/emergent_model.pt"


class DetectedEmgObj(TypedDict):
    """
    The output obtained from running the emergent object detection model.
    Represents the attributes of one detected emergent object

    Attributes
    ----------
    xmin: float
        minimum x value
    ymin: float
        minimum y value
    xmax: float
        maximum x value
    ymax: float
        maximum y value
    confidence: float
        confidence in the detection
    class: int
        class of object, can't be included because its a Python keyword,
        but we won't be using this attribute anyway
    name: str
        currently only human implemented
    """

    xmin: float
    ymin: float
    xmax: float
    ymax: float
    confidence: float
    name: str


def create_emergent_model(model_path: str = EMG_MODEL_PATH) -> Callable[[Image], Any]:
    """
    Loads the model used for emergent object detection/classification.

    Parameters
    ----------
    model_path : str, by default = EMG_MODEL_PATH
        the file path to the emergent object model weights file

    Returns
    -------
    model : Callable[[Image], Any]
        The model used for object detection/classification
        NOTE: model is not technically a Callable, but can be treated as such
        for our purposes.
    """
    model: Callable[[Image], Any] = torch.hub.load("ultralytics/yolov5", "custom", path=model_path)
    return model


def detect_emergent_object(image: Image, model: Callable[[Image], Any]) -> list[BoundingBox]:
    """
    Detects emergent object within an image using the selected model.

    NOTE: The pytorch model can be run on either an NDArray image, or
    on a file specified by a string path. To integrate better with the
    pipeline, we are utilizing a NDArray image.

    Parameters
    ----------
    image : Image
        the image being analyzed by the model
    model : Callable
        the model which is being used for object detection/classification

    Returns
    -------
    boxes : list[BoundingBox]
        bounding boxes of the detected emergent objects,
        with attributes confidence and name
    """
    # Convert to RGB
    rgb_image: Image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run the model on the image
    object_locations: dict[int, DetectedEmgObj] = model(rgb_image).pandas().xyxy[0].to_dict("index")

    # Create BoundingBoxes for the objects
    boxes: list[BoundingBox] = []

    obj: DetectedEmgObj
    for obj in object_locations.values():
        width: int = int(obj["xmax"] - obj["xmin"])
        height: int = int(obj["ymax"] - obj["ymin"])
        area: int = width * height

        verts: Vertices = tlwh_to_vertices(
            int(obj["xmin"]),
            int(obj["ymin"]),
            width,
            height,
        )

        box: BoundingBox = BoundingBox(verts, ObjectType.EMG_OBJECT)
        box.set_attribute("bounding_box_area", area)
        box.set_attribute("confidence", obj["confidence"])
        box.set_attribute("name", obj["name"])

        boxes.append(box)

    return boxes


# duplicate code disabled for main
# pylint: disable=duplicate-code
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Error: Incorrect number of parameters. Please specify an image file path.")
        sys.exit()

    # Load the image
    image_path: str = sys.argv[1]
    test_image: Image = cv2.imread(image_path)

    # Load model
    emg_model: Callable[[Image], str] = create_emergent_model()

    # Use model for detection / classification
    detected_emg_objs: list[BoundingBox] = detect_emergent_object(test_image, emg_model)

    # Draw the bounding boxes to the original image
    emg_obj: BoundingBox
    for emg_obj in detected_emg_objs:
        # Get the output ranges
        min_x: int
        max_x: int
        min_x, max_x = emg_obj.get_x_extremes()

        min_y: int
        max_y: int
        min_y, max_y = emg_obj.get_y_extremes()

        top_left: tuple[int, int] = (min_x, min_y)
        bottom_right: tuple[int, int] = (max_x, max_y)

        # Draw the bounding box
        cv2.rectangle(test_image, top_left, bottom_right, (255, 0, 0), 4)

    # Display the image
    cv2.imshow("Detected Emergent Objects", test_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
