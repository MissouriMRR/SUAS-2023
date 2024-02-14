"""
Preprocesses images obtained during airdrop area flyover for
use in contour detection for the standard objects.
"""

import cv2
import numpy as np
from nptyping import NDArray, Shape, UInt8

from vision.common.constants import Image, ScImage


def preprocess_std_odlc(image: Image, thresh_min: int = 50, thresh_max: int = 100) -> ScImage:
    """
    Preprocesses image for use in detecting the contours of standard objects.

    Parameters
    ----------
    image : Image
        image from airdrop area flyover before any processing has occured
    thresh_min: int
        The minimum threshold input for the Canny edge detection. Defaults to 10
    thresh_max: int
        The maximum threshold input for the Canny edge detection. Defaults to 100

    Returns
    -------
    edges : ScImage
        the single channel image after preprocessing for use in contour detection/processing
    """

    grayscaled: ScImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale

    blurred: ScImage = cv2.GaussianBlur(grayscaled, ksize=(3, 3), sigmaX=1.5)  # Blur the image

    edges: ScImage = cv2.Canny(image=blurred, threshold1=thresh_min, threshold2=thresh_max)

    # Create the kernel for the dilation
    kernel: NDArray[Shape["3, 3"], UInt8] = np.ones((3, 3), np.uint8)

    dilated: ScImage = cv2.dilate(edges, kernel, iterations=1)

    return dilated


# Runs preprocessing on specified image and displays results.
# duplicate code disabled for main
# pylint: disable=duplicate-code
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Error: Incorrect number of parameters. Please specify an image file path.")
        sys.exit()

    # read in image
    image_path: str = sys.argv[1]
    input_image: Image = cv2.imread(image_path)

    # show unprocessed image
    cv2.imshow("Image Before Preprocessing", input_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # run preprocessing
    processed_image: Image = preprocess_std_odlc(input_image, 15, 30)

    # show pre-processed image
    cv2.imshow("Preprocessed Image", processed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
