# Vision

### Flyover Vision Pipeline

Run `flyover_pipeline()` from `vision/flyover_vision_pipeline.py`.

The pipeline will loop through any new images until it is given the signal to stop.

Takes three inputs:
- `camera_data_path`, which is the path to the json file with the necessary data for each image.
  - Keys are file paths to each image, and should be a path such that the image can be opened directly from the path in the pipeline.
  - Values are a dictionary matching `CameraParameters` in `vision/common/constants.py`
- `state_path` - A path to a txt file containing "True" or "False".
  - Set this to "True" when all images have been taken for the flyover, and "False" otherwise.
- `output_path` - The location for where the output json file will be once the pipeline is done.
  - Keys will be the bottle indices converted to strings
  - Values are the locations in dictionary form, matching the `Location` TypedDict in `vision/common/constants.py`
