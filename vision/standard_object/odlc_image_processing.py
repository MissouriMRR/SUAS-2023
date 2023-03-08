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
    edges : Image
        the image after preprocessing for use in contour detection/processing
    """
    grayscaled: Image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to graycsale

    blurred: Image = cv2.GaussianBlur(grayscaled, ksize=(3, 3), sigmaX=0)  # Blur the image

    edges: Image = cv2.Canny(image=blurred, threshold1=15, threshold2=30)

    return edges


# Runs preprocessing on specified image and displays results.
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
    processed_image: Image = preprocess_std_odlc(input_image)

    # show pre-processed image
    cv2.imshow("Preprocessed Image", processed_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
