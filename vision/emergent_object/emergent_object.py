"""
Contains functions relating to the identification and
classification of the emergent object within an image.
"""

import torch

from typing import Callable, Any

from vision.common.constants import Image


EMG_MODEL_PATH = "vision/emergent_object/emergent_model.pt"


# Load the model from the file
def create_emergent_model(model_path: str = EMG_MODEL_PATH) -> Callable:
    """
    Loads the model used for emergent object detection/classification.

    Parameters
    ----------
    None

    Returns
    -------
    model : Callable ## TODO: Pretty sure the type isn't a Callable
        The model used for object detection/classification
    """
    model: Callable = torch.hub.load("ultralytics/yolov5", "custom", path=model_path)
    return model


def detect_emergent_object(image: Image, model: Callable) -> Any:
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
    object_locations : Any ## TODO: what's the type, idk
        A dataframe containing the xy coordinates of
        the detected object within the image
    """
    # Convert to RGB
    image: Image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run the model on the image
    model_prediction = model(image)

    # Retrieve the output from the model
    object_locations: Any = model_prediction.pandas().xyxy[0]

    return object_locations


if __name__ == "__main__":
    import cv2

    # Load the image ## TODO: add command line arg
    image_path = "vision/emergent_object/people.png"
    image = cv2.imread(image_path)

    # Load model
    model = create_emergent_model()

    # Use model for detection / classification
    output = detect_emergent_object(image, model)

    # Convert the Pandas Dataframe to a dictionary - this will be necessary and
    #   should eventually be done in `detect_emergent_object()` ## TODO
    output_dict = output.to_dict("index")

    # Draw the bounding boxes to the original image
    for row in output_dict.values():
        # Get the output ranges
        top_left = (int(row["xmin"]), int(row["ymin"]))
        bottom_right = (int(row["xmax"]), int(row["ymax"]))

        # Draw the bounding box
        cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 4)

    # Display the image
    cv2.imshow("Detected Emergent Objects", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
