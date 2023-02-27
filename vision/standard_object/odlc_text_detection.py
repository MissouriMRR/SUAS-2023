"""
Method for reading the text on the odlc standard objects.
"""

from typing import Any, Dict, List

import sys
import cv2
import numpy as np
import numpy.typing as npt
import pytesseract

from vision.common.bounding_box import ObjectType, BoundingBox

# from bounding_box import ObjectType, BoundingBox  # A local file is required when testing


def text_detection_pre_processing(unprocessed_img: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
    """
    This does the preprocessing effects on the passed image needed to make text detection easier.

    Parameters
    ----------
    img: npt.NDArray[np.uint8]
        The image that you want to do the preprocessing on.

    Returns
    ----------
    final_img: pt.NDArray[np.uint8]
        The image after all of the preprocessing effects have been run.
    """

    # Contrast and brightness
    contrast_img: npt.NDArray[np.uint8] = cv2.convertScaleAbs(unprocessed_img, alpha=1.25, beta=-30)

    # Grayscale
    grayscale_img: npt.NDArray[np.uint8] = cv2.cvtColor(contrast_img, cv2.COLOR_RGB2GRAY)

    # Blur
    blured_img: npt.NDArray[np.uint8] = cv2.medianBlur(grayscale_img, ksize=3)

    # Erode and dilate
    kernel: npt.NDArray[np.uint8] = np.ones((5, 5), np.uint8)
    eroded_img: npt.NDArray[np.uint8] = cv2.erode(blured_img, kernel=kernel, iterations=1)
    final_img: npt.NDArray[np.uint8] = cv2.dilate(eroded_img, kernel=kernel, iterations=1)

    return final_img


def text_detection(base_img: npt.NDArray[np.uint8]) -> List[str]:
    """
    Detects text on the passed image.

    Parameters
    ----------
    img: npt.NDArray[np.uint8]
        The image that you want to detect the text on.

    Returns
    ----------
    detected_text: List[str]
        A list containing each of the individual detected characters in the passed image as strings.

    """

    found_text: List[str] = []

    found_text_info: Dict[str, List[Any]] = pytesseract.image_to_data(
        base_img, output_type=pytesseract.Output.DICT, config="--psm 10"
    )

    for _, text in enumerate(found_text_info["text"]):
        found_text += text

    return found_text


def crop_image(uncropped_img: npt.NDArray[np.uint8], bounds: BoundingBox) -> npt.NDArray[np.uint8]:
    """
    Crops the passed image according to the passed bounding box.

    Parameters
    ----------
    img: pt.NDArray[np.uint8]
        The image to be cropped.

    bounds: BoundingBox
        The bounding box that has the cords to crop around.

    Returns
    ----------
    cropped_img: pt.NDArray[np.uint8]
        The image after it has been cropped.
    """

    x_min: int
    x_max: int
    x_min, x_max = bounds.get_x_extremes()

    y_min: int
    y_max: int
    y_min, y_max = bounds.get_y_extremes()

    crop_img: npt.NDArray[np.uint8] = uncropped_img[y_min:y_max, x_min:x_max, :]

    return crop_img


if __name__ == "__main__":
    img: npt.NDArray[np.uint8] = cv2.imread(
        sys.argv[1]
    )  # Run with something like 'python3 odlc_text_detection.py image.jpg'

    # Testing coordinates
    test_bounds: BoundingBox = BoundingBox(
        ((740, 440), (820, 440), (820, 500), (740, 500)), ObjectType.STD_OBJECT
    )  # Coords for the A in the star

    # test_bounds: BoundingBox = BoundingBox(
    # ((570, 440), (630, 440), (570, 520), (630, 520)), ObjectType.STD_OBJECT
    # )  # Coords for the T in the rectangle

    cropped_img: npt.NDArray[np.uint8] = crop_image(img, test_bounds)

    preprocessed_img: npt.NDArray[np.uint8] = text_detection_pre_processing(cropped_img)

    deteceted_text: List[str] = text_detection(preprocessed_img)

    print("The following text was detected:")

    for i in enumerate(deteceted_text):
        print(i[1])
