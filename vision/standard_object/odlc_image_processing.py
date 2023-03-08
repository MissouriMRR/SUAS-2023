"""
Preprocesses images obtained during airdrop area flyover for
use in contour detection for the standard objects.
"""

import cv2

from vision.common.constants import Image


def preprocess_std_odlc(image: Image) -> Image:
    """
    Preprocesses image for use in detecting the contours of standard objects.

    Parameters
    ----------
    image : Image
        image from airdrop area flyover before any processing has occured

    Returns
    -------
    processed_image : Image
        the image after preprocessing for use in contour detection/processing
    """
    grayscaled: Image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to graycsale

    blurred: Image = cv2.GaussianBlur(grayscaled, ksize=(3, 3), sigmaX=0)  # Blur the image

    edges: Image = cv2.Canny(
        image=blurred, threshold1=15, threshold2=30
    )  # best one for image DJI_0470

    return edges
