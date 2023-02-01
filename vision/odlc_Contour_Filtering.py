"""
This file contains code to filter contours to identify the odlc shapes from an already processed
image.

Assumed input: unmodified contours found from a well-processed image,
the processed image and the original image should be accessable,
the list of odlc shapes.

Output: will identify which contours are odlc shapes, and what types of odlc shapes it is.
"""
from typing import TypeAlias
import numpy as np
from nptyping import NDArray, Shape, UInt8, IntC, Float32, Bool
import cv2


# Brainstorming:
# Any ODLC shape will have a letter in it so the contour hierarchy will have stuff (needs heirarchy)
# bounding box will probably be close to a square and/or small (def will not be like whole image)
# wont have any crazy points that are really far from center of mass, can use:
# 	>>> moms = cv2.moments(single_contour)
# 	>>> center_x = (moms["m10"] / moms["m00"])
# 	>>> center_y = (moms["m01"] / moms["m00"])
# either will be circular or approxPolyDP will work well min area lost w/o erroneous area incl.


# return types for cv2.findContours() -> (Tuple[contours], hierarchy)
contour_type: TypeAlias = NDArray[Shape["*, 1, 2"], IntC]
hierarchy_type: TypeAlias = NDArray[Shape["1, *, 4"], IntC]

# type for return value of cv2.boxpoints()
min_area_box_type: TypeAlias = NDArray[Shape["4, 2"], Float32]
# type for return value of cv2.boundingRect()
bound_box_type: TypeAlias = tuple[int, int, int, int]
# type for return of cv2.HoughCircles() (center_x, center_y, radius)
circles_type: TypeAlias = NDArray[Shape["1, *, 3"], Float32]

image_type: TypeAlias = NDArray[Shape["*, *, 3"], UInt8]
# single channel image type
sc_image_type: TypeAlias = NDArray[Shape["*, *"], UInt8]
mask_type: TypeAlias = NDArray[Shape["*, *"], Bool]


def test_heirarchy(hierarchy: hierarchy_type, contour_index: int) -> bool:
    """
    Function to test whether the contour at the given index contains another contour in it

    parameters
    ----------
    hierarchy : hierarchy_type
        The 2nd value returned from cv2.findContours(), describes how contours are inside of
        other contours
    contour_index : int
        The index of the contour to be examined (in the contours tuple and hierarchy array
        returned from cv2.findContours())

    returns
    -------
    True if the given contour has a contour inside of it, False otherwise
    """
    if hierarchy[0, contour_index, 2] <= 0:
        return False
    return True


def test_min_area_box(
    contour: contour_type, min_box_ratio: float = 0.9, max_box_ratio: float = 1.1
) -> bool:
    """
    will create a box around the given contour that has the smallest possible area
    (not necessarily upright) and check if the box's aspect ratio is within the given range

    parameters
    ----------
    contour : contour_type
        The individual contour to be evaluated (as returned from cv2.findContours)
    min_box_ratio : float
        The lowest acceptable ratio of min area box length to width must be less than the max
    max_box_ratio : float
        The highest ratio of min area box length to width acceptable, more than min

    returns
    -------
    returns true if the aspect ratio of the min area box is inbetween the min and max
    """
    min_area_box: min_area_box_type = cv2.boxPoints(cv2.minAreaRect(contour))
    aspect_ratio: float = (cv2.norm(min_area_box[0] - min_area_box[1])) / (
        cv2.norm(min_area_box[1] - min_area_box[2])
    )

    return min_box_ratio < aspect_ratio < max_box_ratio


def test_bounding_box(
    contour: contour_type, dims: tuple[int, int], test_area_ratio: float = 10.0
) -> bool:
    """
    calculates the area of a upright bounding box around the given contour
    and compares it to the rectangle (image) of the given dimensions

    parameters
    ----------
    contour : contour_type
        The individual contour to be evaluated (as returned from cv2.findContours)
    dims : tuple[int, int]
        The dimensions of the image the contour is from
    test_area_ratio : float
        The minimum acceptable ratio of image area to contour bounding box area

    returns
    -------
    returns true if the bounding box area is less than the image area by a factor of
    test_area_ratio or more
    """
    bounding_box: bound_box_type = cv2.boundingRect(contour)

    box_area: float = abs(bounding_box[2] - bounding_box[0]) * abs(
        bounding_box[3] - bounding_box[1]
    )
    img_area: float = dims[0] * dims[1]

    return box_area * test_area_ratio <= img_area


def test_spikiness(contour: contour_type) -> bool:
    """
    Checks whether the contour has some points that are much farther away from the center of mass
    than the rest of the points
    basically real shapes will not have random points that are really far away from the rest
    but a weird patch of grass or something without well defined edges will have crazy points
    all over the place

    parameters
    ----------
    contour : contour_type
        The individual contour to be evaluated (as returned from cv2.findContours)

    returns
    -------
    True unless there is a statistical outlier point that is uniquely far away (or close ig)
    """
    moments: dict[str, float] = cv2.moments(contour)
    # com is Center of Mass, com = (y_coord, x_coord)
    com: NDArray[Shape["2"], Float32] = np.array(
        ((moments["m01"] / moments["m00"]), (moments["m10"] / moments["m00"])), dtype=np.float64
    )

    dists_com: NDArray[Shape["*"], Float32] = np.ndarray(contour.shape[0], Float32)
    for i in range(contour.shape[0]):
        dists_com[i] = cv2.norm(contour[i] - com)

    dists_median: float = np.median(dists_com)
    dists_outlier_range: float = 1.5 * (np.quantile(dists_com, 0.75) - np.quantile(dists_com, 0.25))

    if np.all(dists_com < dists_median + dists_outlier_range):
        return True
    return False


def _min_common_bounding_box(contours: tuple[contour_type, ...]) -> bound_box_type:
    """
    takes a set of contours and returns the smallest bounding
    box that encloses all of them

    parameters
    ----------
    contours : tuple[contour_type]
        Tuple of contours as formatted in cv2.findContour to find the minimum common bounding box

    returns
    -------
    the smallest bounding box that encompases all of the given contours
    """

    boxes: tuple[bound_box_type, ...] = ()
    for contour in contours:
        boxes += (cv2.boundingRect(contour),)

    min_box: bound_box_type = (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )
    return min_box


def _generate_mask(contour: contour_type, box: bound_box_type) -> mask_type:
    """
    will create a mask with the dimensions of the given bounding box that is true for any point
    that is inside the contour

    parameters
    ----------
    contour : contour_type
        The individual contour to be evaluated (as returned from cv2.findContours)
    box : bound_box_type
        The bounding box that will be used to create the mask image, the mask will be the size of
        box and will offset the contour so that it is inside of the box

    returns
    -------
    a mask_type that is the dimensions of the input bounding box and is true wherever is inside of
    the input contour
    """
    dims: tuple[int, int] = (box[2] - box[0], box[3] - box[1])
    shifted_cnt: contour_type = contour - np.array((box[0], box[2]))

    mask: mask_type = np.zeros(dims)
    mask = cv2.drawContours(mask, [contour], -1, True, cv2.FILLED)
    return mask


def test_roughness(
    contour: contour_type, approx: contour_type, test_percent_diff: float = 0.05
) -> bool:
    """
    will check how rough the sides of a shape are. If the contour is an actual shape, then it will
    have relatively smooth sides, and the approximated contour will not have a lot of change. If
    the contour is not actually a shape (ie a patch of grass), then its sides will be less
    straight, and the polygon approximation will be very different from the original.

    parameters
    ----------
    contour : contour_type
        The originally found contour to be evaluated (as returned from cv2.findContours)
    approx : contour_type
        The contour (same as contour param) but run through an approximation algoritm
        such as cv2.approxPolyDP(contour, 0.05*cv2.arcLength(contour, True), True)
                                          ^^^^can be tweaked
    test_percent_diff : float
        The max percent difference in area allowed between the original and approximaed contour

    returns
    -------
    returns true if the non-overlapping area between the two contours is less than the specified
    amount, false otherwise
    """
    # kinda need to figure out how much non overlap is too much
    box: bound_box_type = _min_common_bounding_box((contour, approx))

    contour_mask: mask_type = _generate_mask(contour, box)
    approx_mask: mask_type = _generate_mask(approx, box)

    non_overlap_mask: mask_type = np.logical_xor(contour_mask, approx_mask)

    non_overlap_cnts: tuple[contour_type]
    # non_overlap_hier: hierarchy_type
    non_overlap_img: sc_image_type = non_overlap_mask.astype(UInt8)
    non_overlap_cnts, _ = cv2.findContours(non_overlap_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    non_overlap_area_sum = 0
    for cnt in non_overlap_cnts:
        non_overlap_area_sum += cv2.contourArea(cnt)

    contour_area = cv2.contourArea(contour)
    if (
        len(non_overlap_cnts) == 0
        or non_overlap_area_sum == 0
        or 1 - test_percent_diff < contour_area / non_overlap_area_sum < 1 + test_percent_diff
    ):
        return True
    return False


def test_circleness(img: sc_image_type) -> bool:
    """
    this function will test the cropped area around a given contour to see if it is a circle or if
    it is not a circle, it uses the cv2.HoughCircles() function to check for a circle

    parameters
    ----------
    img : sc_image_type
        img should be grayscale cropped box around contour and PROCESSED ALREADY
        as in the image is binary with the contour filled in as white
        NOTE: sc_image_type denotes a single channel image

    returns
    -------
    returns true if a circle of appropriate size is found (to reduce chance of false positives)
    """
    padding: int = int(img.shape[0] * 0.05)
    modded: sc_image_type = cv2.copyMakeBorder(
        img, padding, padding, padding, padding, cv2.BORDER_CONSTANT, None, 0
    )
    modded = cv2.GaussianBlur(img, (5, 5), 5)
    circles: circles_type | None = cv2.HoughCircles(
        modded,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=int(max(img.shape[0], img.shape[1])),
        param1=50,
        param2=30,
        minRadius=4,
        maxRadius=int(min(img.shape[0], img.shape[1]) * 1.1),
    )

    if circles is None:
        return False
    else:
        for circle in circles[0]:
            if (
                int(max(img.shape[0], img.shape[1]) / 1.6)
                <= circle[2]
                <= int(min(img.shape[0], img.shape[1]) * 1.1)
            ):
                return True

    return False


def filter_contour(
    contours: tuple[contour_type], hierarchy: hierarchy_type, contour_index: int, image: image_type
) -> bool:
    """
    runs all created test functions and handles logic to determine if a given contour (from the
    tuple of contours) is an ODLC shape or not

    parameters
    ----------
    contours : tuple[contour_type]
        The list of contours returned by the contour detection algorithm
    hierarchy : hierarchy_type
        The contour hierarchy list returned by the contour detection algorithm
        (the 2nd value returned by cv2.findContours())
    contour_index : int
        The index corresponding to the contour in contours and hierarchy to be checked
    image : image_type
        a cropped bounding box arround the contour in question

    returns
    -------
    true if the contour is (probably) an ODLC shape
    """
    # test hierarchy, bounding_box, and jaggedness
    # then calculate approxPolyDP if above all pass (maybe change depending on test results)

    # (vertical len, horizontal len)
    image_dims: tuple[int, int] = image.shape[:2]
    return False


if __name__ == "__main__":
    img = np.zeros([500, 500, 3], dtype=UInt8)

    pts: contour_type = np.array([[249, 0], [499, 249], [249, 499], [0, 249]], IntC).reshape(
        -1, 1, 2
    )
    img = cv2.polylines(img, [pts], True, (255, 255, 255))

    cv2.imshow("pic", img)
    cv2.waitKey(0)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # print("grayscale image shape", img.shape)
    cnts_tmp, hier_tmp = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print("contours1:", type(cnts_tmp), len(cnts_tmp), cnts_tmp)
    img2 = np.dstack((img, img, img))

    img2 = cv2.drawContours(img2, cnts_tmp, 0, (255, 255, 255), thickness=cv2.FILLED)
    cv2.imshow("cnts1-0", img2)
    cv2.waitKey(0)

    cnts, hier = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for i, cnt in enumerate(cnts):
        print("\nHierarchy Test:", test_heirarchy(hier, i))
        print("Min Area Box Test:", test_min_area_box(cnt))
        print("Bounding Box Test:", test_bounding_box(cnt, (img.shape[0], img.shape[1])))
        print("Jaggedness Test:", test_spikiness(cnt))
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
        print("Polygonness Test:", test_roughness(cnt, approx))
        print("Circleness Test:", test_circleness(img2[:, :, 0]))
