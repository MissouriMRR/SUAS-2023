"""
This file contains code to filter contours to identify the odlc shapes from an already processed
image.

Assumed input: unmodified contours found from a well-processed image,
the processed image and the original image should be accessable,
the list of odlc shapes.

Output: will identify which contours are odlc shapes, and what types of odlc shapes it is.
"""
from typing import Tuple, TypeAlias
import numpy as np
from nptyping import NDArray, Shape, Int, UInt8, IntC
import cv2
"""
Brainstorming:
Any ODLC shape will have a letter in it so the contour hierarchy will have stuff (needs heirarchy)
bounding box will probably be close to a square and/or small (def will not be like whole image)
wont have any crazy points that are really far from center of mass, can use:
	>>> moms = cv2.moments(single_contour)
	>>> center_x = (moms["m10"] / moms["m00"])
	>>> center_y = (moms["m01"] / moms["m00"])
either will be circular or approxPolyDP will work well min area lost w/o erroneous area incl.

"""


contour_type: TypeAlias = NDArray[Shape["1, *, 2"], IntC]
hierarchy_type: TypeAlias = NDArray[Shape["1, *, 4"], IntC]


def test_heirarchy(contour: contour_type,
	hierarchy: hierarchy_type,
	contour_index: int
	) -> bool:
	"""
	TODO: document code
	"""
	if hierarchy[0, contour_index, 2] < 0:
		return False
	return True


def test_bounding_box(contour: contour_type,
	dims: Tuple[int, int],
	test_ratio: int = 3
	) -> bool:
	"""
	TODO: document code
	"""
	bounding_box: contour_type = cv2.boxPoints(cv2.minAreaRect(contour))
	aspect_ratio: float =	(cv2.norm(bounding_box[0, 0]-bounding_box[0, 1]))                        \
		                   /(cv2.norm(bounding_box[0, 2]-bounding_box[0, 3]))
	if aspect_ratio > test_ratio or aspect_ratio < 1 / test_ratio: return False
	


def filter_contour(contour: contour_type,
	hierarchy: hierarchy_type,
	contour_index: int
	) -> bool:
	"""
	TODO: document code
	"""
