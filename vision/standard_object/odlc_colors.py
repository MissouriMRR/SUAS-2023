"""
Functions relating to finding the colors of the text and shape on the standard ODLC objects.
"""

import cv2
import numpy as np

from nptyping import NDArray, Shape, UInt8, Float32

from vision.common.bounding_box import BoundingBox
from vision.common.constants import Image
from vision.common.odlc_characteristics import ODLCColors, COLOR_RANGES


def find_colors(image: Image, text_bounds: BoundingBox) -> NDArray[Shape["2"], ODLCColors]:
    """
    Finds the colors of the shape and text based on the portion of the image bounded
    by the text bounds.

    Parameters
    ----------
    image : Image
        the image containing the standard odlc object
    text_bounds : BoundingBox
        the bounds of the text on the odlc object

    Returns
    -------
    colors : NDArray[Shape["2"], ODLCColors]
        the colors of the standard object
        shape_color : ODLCColors
            the color of the shape
        text_color : ODLCColors
            the color of the text on the object
    """
    # slice image around bounds of text
    cropped_img = crop_image(image, text_bounds)

    # kmeans clustering with k=2

    # get the 2 color values

    # determine which color is shape and which is text

    # match colors to closest color in ODLCColors

    # return the 2 colors
    pass


def crop_image(image: Image, bounds: BoundingBox) -> Image:
    """
    Crop an image around the given bounds. Will slice around
    the bound's extremes as an upright rectangle.

    Parameters
    ----------
    image : Image
        the image to slice
    bounds : BoundingBox
        the bounds to slice from the image

    Returns
    -------
    cropped_img : Image
        the image cropped around the given bounds
    """
    min_y: int
    max_y: int
    min_y, max_y = bounds.get_y_extremes()

    min_x: int
    max_x: int
    min_x, max_x = bounds.get_x_extremes()

    cropped_img: Image = image[min_y:max_y, min_x, max_x, :]
    return cropped_img


def run_kmeans(cropped_img: Image) -> Image:
    """
    Run kmeans clustering on the cropped image with K=2.

    Assumption: the bounds around the text will contain 2 primary colors,
    the text color and the shape color. Clustering with K=2 should result
    in these colors being chosen as the unique colors.

    NOTE: kmeans clustering performed on RGBXY data

    Parameters
    ----------
    cropped_img : Image
        the image cropped around the text

    Returns
    -------
    kmeans_img : Image
        the image after performing kmeans clustering with K=2,
        will contain 2 unique colors
    """
    # preprocess image to make text/shape bigger, reducing the likelihood
    # of kmeans choosing a ground color if bounds are loose
    blurred_img: Image = cv2.medianBlur(cropped_img, ksize=9)

    kernel: NDArray[Shape["5, 5"], UInt8]  # 5x5 kernal for use in dilation/erosion
    eroded_img: Image = cv2.erode(blurred_img, kernel=kernel, iterations=1)
    dilated_img: Image = cv2.dilate(eroded_img, kernel=kernel, iterations=1)

    # convert to RGBXY
    flattened: NDArray[Shape["*, 3"], UInt8] = dilated_img.reshape((-1, 3))
    idxs: NDArray[Shape["*, 2"], UInt8] = np.array(
        [idx for idx, _ in np.ndenumerate(np.mean(dilated_img, axis=2))]
    )
    vectorized: NDArray[Shape["*, 5"], UInt8] = np.hstack((flattened, idxs))  # RGBXY vector

    # run kmeans with K=2
    term_crit: tuple[int, int, float] = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        10,
        1.0,
    )
    k_val: int = 2

    label: NDArray[str]
    center: NDArray[Float32]
    _, label, center = cv2.kmeans(
        np.float32(vectorized), K=k_val, bestLabels=None, criteria=term_crit, attempts=10, flags=0
    )

    center_int: NDArray[UInt8] = center.astype(np.uint8)[:, :3]

    # Convert back to BGR
    kmeans_img: Image = center_int[label.flatten()]
    kmeans_img = kmeans_img.reshape((dilated_img.shape))

    return kmeans_img
