"""
Method for reading the text on the odlc standard objects.
"""

from typing import Any

import cv2
import numpy as np
import pytesseract

from vision.common.bounding_box import ObjectType, BoundingBox, tlwh_to_vertices
from vision.common.constants import Image
from vision.common.crop import crop_image


def get_odlc_text(starting_image: Image, odlc_bounds: BoundingBox) -> BoundingBox:
    """
    Detects text in the passed image at the location specified by the passed bounding box.

    Parameters
    ----------
    starting_image: Image
        The image to detect the text on.
    text_bounds: BoundingBox
        The bounding box specifying where in the image to look for text.

    Returns
    -------
    detected_text: BoundingBox
        A BoundingBox object containing the detected character as an attribute and its bounds.
        If no text is detected, the character will be a blank string and
        the bounds will all be zeros.
    """

    cropped_img: Image = crop_image(starting_image, odlc_bounds)

    preprocessed_img: Image = text_detection_pre_processing(cropped_img)

    detected_text: BoundingBox = text_detection(preprocessed_img)

    return detected_text


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
    blurred_img: Image = cv2.medianBlur(grayscale_img, ksize=3)

    # Erode and dilate
    kernel: Image = np.ones((5, 5), np.uint8)
    eroded_img: Image = cv2.erode(blurred_img, kernel=kernel, iterations=1)
    final_img: Image = cv2.dilate(eroded_img, kernel=kernel, iterations=1)

    return final_img


def text_detection(base_img: Image) -> BoundingBox:
    """
    Detects text on the passed image.

    Parameters
    ----------
    base_img: Image
        The image that you want to detect the text on.

    Returns
    -------
    found_text: BoundingBox
        A BoundingBox object containing the detected character as an attribute and its bounds.
        If no text is detected, the character will be a blank string and
        the bounds will all be zeros.
    """

    found_text: str = ""  # Text to be returned, one character

    found_text_info: dict[str, list[Any]] = pytesseract.image_to_data(
        base_img, output_type=pytesseract.Output.DICT, config="--psm 10"
    )

    text_x: int = 0
    text_y: int = 0
    text_width: int = 0
    text_height: int = 0

    i: int
    text: str
    for i, text in enumerate(found_text_info["text"]):
        character: str
        for character in text:
            if (
                character.isalnum() and character.isupper()
            ):  # Text needs to be upercase and alphanumeric
                found_text = character

                # Bounding box of text in cropped image
                text_x = found_text_info["left"][i]
                text_y = found_text_info["top"][i]
                text_width = found_text_info["width"][i]
                text_height = found_text_info["height"][i]

    text_bounds: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]] = (
        tlwh_to_vertices(text_x, text_y, text_width, text_height)
    )

    text_attributes: dict[str, str] = {"text": found_text}
    text_with_bounds: BoundingBox = BoundingBox(
        vertices=text_bounds, attributes=text_attributes, obj_type=ObjectType.TEXT
    )

    return text_with_bounds


if __name__ == "__main__":
    import sys

    img: Image = cv2.imread(
        sys.argv[1]
    )  # Run with something like 'python3 odlc_text_detection.py image.jpg'

    # Testing coordinates
    test_bounds: BoundingBox = BoundingBox(
        ((740, 440), (820, 440), (820, 500), (740, 500)), ObjectType.STD_OBJECT
    )  # Coords for the A in the star of the 2022 image

    read_text: BoundingBox = get_odlc_text(img, test_bounds)

    print("The following character was detected: " + read_text.get_attribute("text"))
    print("Text bounds are: " + str(read_text.vertices))
