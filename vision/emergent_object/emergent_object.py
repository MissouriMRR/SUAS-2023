import torch

# You may have to install:
#   pandas
#   torchvision
#   tqdm
#   seaborn

MODEL_PATH = "vision/emergent_object/best.pt"


# Function to do detection / classification
def emergent_object_detection(image, model):    
    # Convert to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Run the model on the image. Both a file path and a numpy image work, but
    #   we want to use a numpy image
    results = model(image)
    
    # Retrieve the output from the model
    output = results.pandas().xyxy[0]
    
    return output


# Load the model from the file
def emergent_object_model():
    model = torch.hub.load(
        "ultralytics/yolov5", "custom", path=MODEL_PATH
    )
    return model


if __name__ == "__main__":
    import cv2

    image_path = "vision/emergent_object/people.png"
    
    image = cv2.imread(image_path)
    
    # Create model
    model = emergent_object_model()
    
    # Use model for detection / classification
    output = emergent_object_detection(image, model)
    
    # Convert the Pandas Dataframe to a dictionary - this will be necessary and
    #   should eventually be done in `emergent_object_detection()`
    output_dict = output.to_dict("index")
    
    # Draw the bounding boxes to the original image
    for row in output_dict.values():
        # Get the output ranges
        top_left = (int(row["xmin"]), int(row["ymin"]))
        bottom_right = (int(row["xmax"]), int(row["ymax"]))
        
        # Draw the bounding box
        cv2.rectangle(image, top_left, bottom_right, (255,0,0), 4)
    
    # Display the image
    cv2.imshow("", image)
    cv2.waitKey(0)