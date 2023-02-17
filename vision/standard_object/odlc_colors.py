"""
Functions relating to finding the colors of the text and shape on the standard ODLC objects.
"""

import numpy as np
from nptyping import NDArray, Shape, UInt8

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

    # kmeans clustering with k=2

    # get the 2 color values

    # determine which color is shape and which is text

    # match colors to closest color in ODLCColors

    # return the 2 colors
    pass
