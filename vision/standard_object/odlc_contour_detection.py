"""Implements contour filtering to return contours that are likely to be shapes we expect to see."""

# pylint: disable=too-many-locals

import cv2
from nptyping import NDArray, Shape, UInt8
import numpy as np

from vision.common.constants import Contour, Hierarchy, Image, Mask, ScImage

# Contour restriction constants
MAX_CONTOUR_AREA: int = 10000
MIN_CONTOUR_AREA: int = 300
MAX_ASPECT_RATIO: float = 1.8
MIN_SOLIDITY: float = 0.85
MIN_PROPORTIONAL_AREA: float = 0.4

# Contour detection constants
KERNEL_SIZE: cv2.typing.Size = (5, 5)
DILATION_KERNEL: NDArray[Shape["3, 3"], UInt8] = np.ones([3, 3], np.uint8)
MIN_WHITE_VALUE: int = 195
MAX_BLACK_VALUE: int = 0
BRIGHTNESS_THRESH = 60
MIN_SATURATION_VALUE: int = 185
MIN_DARK_SATURATION_VALUE: int = 125
BLUR_IMG_WEIGHT: float = 0.7
NORMAL_IMG_WEIGHT: float = 0.3


def fetch_shape_contours(
    image: Image, draw_contours: bool = False, resulting_file_name: str = ""
) -> list[Contour]:
    """
    Detects the boundaries of potential shapes based on a pixel or region's
    brightness and saturation, finding only the darkest, brightest, and
    most saturated portions of an image, and filters out shapes that are
    guaranteed not to be the shapes we're expecting to see.

    Parameters
    ----------
    filename : str
        the name of the image to look for contours within
    draw_contours : bool
        True if we want to draw the contours and output the result
    resutling_file_name : str
        the name of the file to output the result to if draw_contours is True

    Returns
    -------
    contours : list[numpy.ndarray]
        a list of all contours that could potentially be shapes we expect
        contour : numpy.ndarray
            an array of all points that make up the contour
    """

    hls_img: Image = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)  # converts image to HLS color format

    # Blur is added to the image to reduce noise and to make the image/grass more uniform
    hls_blurred: Image = cv2.GaussianBlur(
        hls_img, KERNEL_SIZE, sigmaX=0, sigmaY=0
    )  # blurs HLS image

    blurred_brightness: ScImage
    blurred_saturation: ScImage

    blurred_brightness = np.array(hls_blurred[:, :, 1])  # reads lightness of image as 2D array
    blurred_saturation = np.array(hls_blurred[:, :, 2])  # reads saturation of image as 2D array

    # slightly blends blurred and unblurred images of same type, prioritizing blurred images
    blurred_brightness = cv2.addWeighted(
        hls_img[:, :, 1], NORMAL_IMG_WEIGHT, blurred_brightness, BLUR_IMG_WEIGHT, 0
    )
    blurred_saturation = cv2.addWeighted(
        hls_img[:, :, 2], NORMAL_IMG_WEIGHT, blurred_saturation, BLUR_IMG_WEIGHT, 0
    )

    avg_brt: float = float(np.average(blurred_brightness))  # gets average brightness

    # Use higher saturation value if image is bright, lower if dark
    saturation_value: int = (
        MIN_SATURATION_VALUE if avg_brt > BRIGHTNESS_THRESH else MIN_DARK_SATURATION_VALUE
    )

    # White threshold is used to find the brightest parts of the image
    # Black threshold is used to find the darkest parts of the image
    # Saturation threshold is used to find the most saturated parts of the image
    white_thresh: Mask
    black_thresh: Mask
    saturation_thresh: Mask

    _, white_thresh = cv2.threshold(blurred_brightness, MIN_WHITE_VALUE, 255, cv2.THRESH_BINARY)
    _, black_thresh = cv2.threshold(blurred_brightness, MAX_BLACK_VALUE, 255, cv2.THRESH_BINARY_INV)
    _, saturation_thresh = cv2.threshold(
        blurred_saturation, saturation_value, 255, cv2.THRESH_BINARY
    )

    # expands each threshold by 3 pixels in the x and y direction
    # to merge those in close proximity to one another
    white_thresh = cv2.dilate(white_thresh, DILATION_KERNEL)
    # black_thresh = cv2.dilate(black_thresh, DILATION_KERNEL)
    saturation_thresh = cv2.dilate(saturation_thresh, DILATION_KERNEL)

    contours: list[Contour]
    _hierarchy: Hierarchy

    # finds the contour outlines of the combined thresholds
    contours, _hierarchy = cv2.findContours(
        (white_thresh + saturation_thresh), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE
    )
    all_contours: list[Contour] = []

    contour: Contour
    for contour in contours:
        # gets rectangle bounding entire contour
        _x_pos: int
        _y_pos: int
        width: int
        height: int
        _x_pos, _y_pos, width, height = cv2.boundingRect(contour)
        area: float = float(cv2.contourArea(contour))

        # calculates area inside contour in proportion to the area of the bounding rectangle
        proportional_area: float = area / (width * height)
        aspect_ratio: float = max(float(width) / height, float(height) / width)

        # calculates solidity/rigidity of shape (shapes with rougher sides have lower solidity)
        solidity: float = area / (cv2.contourArea(cv2.convexHull(contour)))

        # saves the contour if the area is a reasonable size, reasonably close to a square,
        # is not extremely small compared to its bounding box, and does not have very rough edges.
        if (
            (MAX_CONTOUR_AREA >= cv2.contourArea(contour) >= MIN_CONTOUR_AREA)
            and (aspect_ratio <= MAX_ASPECT_RATIO)
            and (proportional_area >= MIN_PROPORTIONAL_AREA)
            and (solidity >= MIN_SOLIDITY)
        ):
            all_contours.append(contour)

    # draws contours and writes to output image file (but only if specified)
    if draw_contours:
        for contour in all_contours:
            cv2.drawContours(image, [contour], 0, (0, 0, 255), 2)
        cv2.imwrite(resulting_file_name, image)
        cv2.imwrite("thresh_white.jpg", white_thresh)
        cv2.imwrite("thresh_black.jpg", black_thresh)
        cv2.imwrite("thresh_saturation.jpg", saturation_thresh)
        cv2.imwrite("thresh_combined.jpg", white_thresh + black_thresh + saturation_thresh)

    # returns a filtered list of contours
    return all_contours
