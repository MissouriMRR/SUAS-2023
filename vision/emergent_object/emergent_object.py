import torch
from vision.common.constants import Image
from typing import Callable, Any

# You may have to install:
#   pandas
#   torchvision
#   tqdm
#   seaborn

MODEL_PATH = "vision/emergent_object/best.pt"


# Function to do detection / classification
def detect_emergent_object(image: Image, model: Callable):
    """
    Detects an emergent object within an image

    Parameters
    ----------
    image
        The image being analyzed by the model.

    model
        The model which is being used for object detection/classification

    Returns
    -------
    output
        A dataframe containing the xy coordinates of
        the detected object within the image
    """
    # Convert to RGB
    image: Image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run the model on the image. Both a file path and a numpy image work, but
    #   we want to use a numpy image
    model_prediction = model(image)

    # Retrieve the output from the model
    object_location: Any = model_prediction.pandas().xyxy[0]

    return object_location


# Load the model from the file
def create_emergent_model():
    """
    Creates the model used for object detection/classification

    Parameters
    ----------
    None

    Returns
    -------
    model : callable
        The model used for object detection/classification
    """
    model: Callable = torch.hub.load("ultralytics/yolov5", "custom", path=MODEL_PATH)
    return model


if __name__ == "__main__":
    import cv2

    image_path = "vision/emergent_object/people.png"

    image = cv2.imread(image_path)

    # Create model
    model = create_emergent_model()

    # Use model for detection / classification
    output = detect_emergent_object(image, model)

    # Convert the Pandas Dataframe to a dictionary - this will be necessary and
    #   should eventually be done in `detect_emergent_object()`
    output_dict = output.to_dict("index")

    # Draw the bounding boxes to the original image
    for row in output_dict.values():
        # Get the output ranges
        top_left = (int(row["xmin"]), int(row["ymin"]))
        bottom_right = (int(row["xmax"]), int(row["ymax"]))

        # Draw the bounding box
        cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 4)

    # Display the image
    cv2.imshow("", image)
    cv2.waitKey(0)
