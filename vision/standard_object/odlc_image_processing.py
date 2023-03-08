"""
Preprocesses images obtained during airdrop area flyover for
use in contour detection for the standard objects.
"""

import cv2
import numpy as np

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
    return


# unable to process tiny object
# Read the original image
img = cv2.imread("images001/DJI_0467.JPG")
# Display original image
cv2.imshow("Original", img)
cv2.waitKey(0)

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to graycsale

img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)  # Blur the image

# best one for images DJI_0434, 0435, 0448,0449
sobelx = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=5)
sobely = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=5)

# best one for images DJI_0453, 0467,0468,0469
sobelxy = cv2.Sobel(src=img_blur, ddepth=cv2.CV_64F, dx=2, dy=1, ksize=5)
sobelxyz = cv2.Sobel(src=img, ddepth=cv2.CV_64F, dx=2, dy=2, ksize=5)
cv2.imshow("Sobel X", sobelx)
cv2.waitKey(0)
cv2.imshow("Sobel Y", sobely)
cv2.waitKey(0)
cv2.imshow("Sobel X Y using Sobel() function", sobelxy)
cv2.waitKey(0)
cv2.imshow("Sobel X Y Z using Sobel() function", sobelxyz)
cv2.waitKey(0)

# images07
edges = cv2.Canny(image=img_blur, threshold1=15, threshold2=30)  # best one for image DJI_0470
# Display Canny Edge Detection Image
cv2.imshow("Canny", edges)
cv2.waitKey(0)

cv2.destroyAllWindows()
