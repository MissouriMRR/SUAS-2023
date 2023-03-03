"""
Method for reading the text on the odlc standard objects.
"""

from typing import Any

import cv2
import numpy as np
import numpy.typing as npt
import pytesseract

from vision.common.bounding_box import ObjectType, BoundingBox
from vision.common.constants import Image


def text_detection_pre_processing(unprocessed_img: Image) -> Image:
    """
    This does the preprocessing effects on the passed image needed to make text detection easier.

    Parameters
    ----------
    unprocessed_img: Image
        The image that you want to do the preprocessing on.

    Returns
    -------
    final_img: Image
        The image after all of the preprocessing effects have been run.
    """

    # Contrast and brightness
    contrast_img: Image = cv2.convertScaleAbs(unprocessed_img, alpha=1.25, beta=-30)

    # Grayscale
    grayscale_img: Image = cv2.cvtColor(contrast_img, cv2.COLOR_RGB2GRAY)

    # Blur
    blured_img: Image = cv2.medianBlur(grayscale_img, ksize=3)

    # Erode and dilate
    kernel: Image = np.ones((5, 5), np.uint8)
    eroded_img: Image = cv2.erode(blured_img, kernel=kernel, iterations=1)
    final_img: Image = cv2.dilate(eroded_img, kernel=kernel, iterations=1)

    return final_img


def crop_image(uncropped_img: Image, bounds: BoundingBox) -> Image:
    """
    Crops the passed image according to the passed bounding box.

    Parameters
    ----------
    uncropped_img: Image
        The image to be cropped.
    bounds: BoundingBox
        The bounding box that has the cords to crop around.

    Returns
    -------
    cropped_img: Image
        The image after it has been cropped.
    """

    x_min: int
    x_max: int
    x_min, x_max = bounds.get_x_extremes()

    y_min: int
    y_max: int
    y_min, y_max = bounds.get_y_extremes()

    crop_img: Image = uncropped_img[y_min:y_max, x_min:x_max, :]

    return crop_img


def text_detection(base_img: Image) -> str:
    """
    Detects text on the passed image.

    Parameters
    ----------
    base_img: Image
        The image that you want to detect the text on.

    Returns
    -------
    found_text: str
        A single character string with the character detected in the image.
    """

    found_text: str  # Text to be returned, one character

    found_text_info: dict[str, list[Any]] = pytesseract.image_to_data(
        base_img, output_type=pytesseract.Output.DICT, config="--psm 10"
    )

    text: str
    character: str

    for text in found_text_info["text"]:
        for character in text:
            if (
                character.isalnum() and character.isupper()
            ):  # Text needs to be upercase and alphanumeric
                found_text = character

    return found_text


def get_odlc_text(starting_image: Image, text_bounds: BoundingBox) -> str:
    """
    Detects text in the passed image at the location specified by the passed bounding box.

    Parameters
    ----------
    starting_image: Image
        The image to detect the text on.
    text_bounds: BoundingBox
        The bounding box specifying were in the image to look for text.

    Returns
    -------
    detected_text: str
        A string containing the character that was detected.
    """

    cropped_img: Image = crop_image(starting_image, text_bounds)

    preprocessed_img: Image = text_detection_pre_processing(cropped_img)

    detected_text: str = text_detection(preprocessed_img)

    return detected_text


if __name__ == "__main__":
    import sys

    img: npt.NDArray[np.uint8] = cv2.imread(
        sys.argv[1]
    )  # Run with something like 'python3 odlc_text_detection.py image.jpg'

    # Testing coordinates
    test_bounds: BoundingBox = BoundingBox(
        ((740, 440), (820, 440), (820, 500), (740, 500)), ObjectType.STD_OBJECT
    )  # Coords for the A in the star of the 2022 image

    read_text: str = get_odlc_text(img, test_bounds)

    print("The following character was detected:")

    for i in enumerate(read_text):
        print(i[1])
