"""
Common functions related to the cropping or slicing of images.
"""

from vision.common.constants import Image
from vision.common.bounding_box import BoundingBox


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

    cropped_img: Image = image[min_y:max_y, min_x:max_x, :]
    return cropped_img
