"""
Contains functions relating to the identification and
classification of the emergent object within an image.

NOTE: Pytorch types are a bit of a pain, so not all types in here
are totally acurrate. Tried to make good approximations for types where
possible, or elimnate variables that couldn't be figured out.
"""

## TODO REMOVE
import sys

sys.path.append("C:/Users/Cameron/Documents/GitHub/SUAS-2023")

import torch

from typing import Callable, Any, TypedDict

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
    None

    Returns
    -------
    model : Callable[[Image], Any]
        The model used for object detection/classification
        NOTE: model is not technically a Callable, but can be treated as such
        for our purposes.
    """
    model: Callable[[Image], Any] = torch.hub.load("ultralytics/yolov5", "custom", path=model_path)
    return model


def detect_emergent_object(
    image: Image, model: Callable[[Image], Any]
) -> dict[int, DetectedEmgObj]:
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
    object_locations : dict[int, DetectedEmgObj]
        contains the xy coordinates and attributes of
        the detected objects within the image
    """
    # Convert to RGB
    rgb_image: Image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run the model on the image
    object_locations: dict[int, DetectedEmgObj] = model(rgb_image).pandas().xyxy[0].to_dict("index")

    return object_locations


if __name__ == "__main__":
    import cv2

    # Load the image ## TODO: add command line arg
    image_path = "vision/emergent_object/people.jpg"
    test_image: Image = cv2.imread(image_path)

    # Load model
    model: Callable[[Image], str] = create_emergent_model()

    # Use model for detection / classification
    output: dict[int, DetectedEmgObj] = detect_emergent_object(test_image, model)

    # Draw the bounding boxes to the original image
    for row in output.values():
        # Get the output ranges
        top_left = (int(row["xmin"]), int(row["ymin"]))
        bottom_right = (int(row["xmax"]), int(row["ymax"]))

        # Draw the bounding box
        cv2.rectangle(test_image, top_left, bottom_right, (255, 0, 0), 4)

    # Display the image
    cv2.imshow("Detected Emergent Objects", test_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
