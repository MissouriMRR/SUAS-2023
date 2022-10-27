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
from nptyping import NDArray, Shape, Int, UInt8, IntC, Float32, Bool
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

# type for return value of cv2.boxpoints()
min_area_box_type: TypeAlias = NDArray[Shape["4, 2"], Float32]
# type for return value of cv2.boundingRect()
bound_box_type: TypeAlias = Tuple[int, int, int, int]

image_type: TypeAlias = NDArray[Shape["*, *, 3"], UInt8]
single_channel_image_type: TypeAlias = NDArray[Shape["*, *"], UInt8]
mask_type: TypeAlias = NDArray[Shape["*, *"], Bool]


def test_heirarchy(hierarchy: hierarchy_type, contour_index: int) -> bool:
    """
    TODO: document code
    """
    if hierarchy[0, contour_index, 2] < 0:
        return False
    return True


def test_min_area_box(contour: contour_type, test_box_ratio: int = 3) -> bool:
    """
    TODO: document code
    """
    min_area_box: min_area_box_type = cv2.boxPoints(cv2.minAreaRect(contour))
    aspect_ratio: float = (cv2.norm(min_area_box[0] - min_area_box[1])) / (
        cv2.norm(min_area_box[1] - min_area_box[2])
    )
    if aspect_ratio > test_box_ratio or aspect_ratio < 1 / test_box_ratio:
        return False
    return True


def test_bounding_box(
    contour: contour_type, dims: Tuple[int, int], test_area_ratio: int = 10
) -> bool:
    """
    TODO: document code
    """
    bounding_box: bound_box_type = cv2.boundingRect(contour)

    box_area: float = abs(bounding_box[2] - bounding_box[0]) * abs(
        bounding_box[3] - bounding_box[1]
    )
    img_area: float = dims[0] * dims[1]

    return img_area / box_area >= test_area_ratio


def test_jaggedness(contour: contour_type) -> bool:
    """
    basically real shapes will not have random points that are really far away from the rest
    but a weird patch of grass or something without well defined edges will have crazy points
    all over the place
    TODO: document code
    """
    moments = cv2.moments(contour)
    # com is Center of Mass, com = (y_coord, x_coord)
    com: NDArray[Shape["2"], Float32] = np.array(
        ((moments["m01"] / moments["m00"]), (moments["m10"] / moments["m00"])), dtype=np.float64
    )

    dists_com: NDArray[Shape["*"], Float32] = np.ndarray(contour.shape[1], Float32)
    for i in range(contour.shape[1]):
        dists_com[i] = cv2.norm(contour[0, i] - com)

    dists_median: float = np.median(dists_com)
    dists_outlier_range: float = 1.5 * (np.quantile(dists_com, 0.75) - np.quantile(dists_com, 0.25))

    if np.all(dists_com < dists_median + dists_outlier_range):
        return True
    return False


def _min_common_bounding_box(contours: NDArray[Shape["*, 1, *, 2"], IntC]) -> bound_box_type:
    """
    takes a set of contours and returns the smallest bounding
    box that encloses all of them
    TODO: document code
    """
    
    boxes: Tuple[bound_box_type, ...] = ()
    for contour in contours:
        boxes.append(cv2.boundingRect(contour))
    
    min_box: bound_box_type = np.array([[[np.min(boxes[:, 0]),
                                          np.min(boxes[:, 1]),
                                          np.max(boxes[:, 2]),
                                          np.max(boxes[:, 3])]]])
    return min_box    


def _generate_mask(contour: contour_type, box: bound_box_type) -> mask_type:
    """
    returns
    TODO: document code
    """
    dims: Tuple[int, int] = (box[2]-box[0], box[3]-box[1])
    shifted_cnt: contour_type = contour - np.array((box[0], box[2]))

    mask: mask_type = np.zeros(dims, shifted_cnt)
    mask = cv2.drawContours(mask, [contour], -1, (True), cv2.FILLED)
    return mask


def test_polygonness(
    contour: contour_type, approx: contour_type, test_ratio: float = 0.75
) -> bool:
    """
    dims param should probably be bounding box dims not image dims
    TODO: document code
    """
    box: bound_box_type = _min_common_bounding_box(np.array([contour, approx]))

    contour_mask: mask_type = _generate_mask(contour, box)
    approx_mask: mask_type = _generate_mask(approx, box)

    non_overlap_mask: mask_type = np.where(contour_mask ^ approx_mask)
    # TODO: figure out how much non overlap is too much


def test_circleness(contour: contour_type):
    """
    TODO: document code
    TODO: actually write the code
    """


def filter_contour(
    contour: contour_type, hierarchy: hierarchy_type, contour_index: int, image: image_type
) -> bool:
    """
    TODO: document code
    NOTE:
    """
    # test hierarchy, bounding_box, and jaggedness
    # then calculate approxPolyDP if above all pass (maybe change depending on test results)

    # (vertical len, horizontal len)
    image_dims: Tuple[int, int] = image.shape[:2]


if __name__ == '__main__':
    img = np.zeros([500, 500, 3], dtype=UInt8)
    img = cv2.circle(img, (200, 250), 150, (255, 255, 255), -1)
    img = cv2.circle(img, (200, 250), 75, (0, 0, 255), -1)
    cv2.imshow("pic", img)
    cv2.waitKey(0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cnts, hier = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print(type(cnts[0]))
    print(cnts[0])
    rect = cv2.boxPoints(cv2.minAreaRect(cnts[0]))
    print(type(rect))
    print(type(rect[0, 0]))
    print(rect)
