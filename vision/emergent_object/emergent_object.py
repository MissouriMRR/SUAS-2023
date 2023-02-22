import torch
import pandas


# Function to create model
def emergent_object_model(path_to_weights):
    model = torch.hub.load(
        "ultralytics/yolov5", "custom", path=path_to_weights
    )  # path depends on location of the pretrained weights
    return model


# Function to do detection / classification
def emergent_object_detection(image_path, model):
    image = image_path
    results = model(image)
    output = results.pandas().xyxy[0]
    return output


if __name__ == "__main__":
    # Create model
    model = emergent_object_model()

    # Use model for detection / classification
    emergent_object_detection()
