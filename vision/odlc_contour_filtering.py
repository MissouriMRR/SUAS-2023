"""
This file contains functions to filter contours to identify the odlc shapes from an already
processed image. The only function that should be needed is filter_contour(), the rest are helper
functions.
"""
import numpy as np
from nptyping import NDArray, Shape, UInt8, IntC, Float32
import cv2
import vision.common.constants as consts
import vision.common.bounding_box as bbox


def test_heirarchy(hierarchy: consts.Hierarchy, contour_index: int) -> bool:
    """
    Function to test whether the contour at the given index contains another contour in it

    Parameters
    ----------
    hierarchy : consts.Hierarchy
        The 2nd value returned from cv2.findContours(), describes how contours are inside of
        other contours
    contour_index : int
        The index of the contour to be examined (in the contours tuple and hierarchy array
        returned from cv2.findContours())

    Returns
    -------
    contains_contour : bool
        True if the given contour has a contour inside of it, False otherwise
    """
    if hierarchy[0, contour_index, 2] <= 0:
        return False
    return True


def test_min_area_box(contour: consts.Contour, max_box_ratio_range: float = 0.5) -> bool:
    """
    Will create a box around the given contour that has the smallest possible area
    (not necessarily upright) and check if the box's aspect ratio is within the given range

    Parameters
    ----------
    contour : consts.Contour
        The individual contour to be evaluated (as returned from cv2.findContours)
    max_box_ratio_range : float = 0.5
        The maximum acceptable range of aspect ratios (centered on a 1:1 ratio), so if 0.5 is the
        given parameter then the aspect ratio between the length and width must be between 0.5 and
        1.5 (1 - 0.5 and 1 + 0.5). The default would correspond to a 2:1 or 1:2 aspect ratio range
        the length/width vs. width/length does not matter

    Returns
    -------
    acceptable_ratio : bool
        Returns true if the aspect ratio of the min area box is inbetween the min and max
    """
    # NDArray[Shape["4, 2"], Float32] is the return type of cv2.boxPoints()
    min_area_box: NDArray[Shape["4, 2"], Float32] = cv2.boxPoints(cv2.minAreaRect(contour))
    # either length/width or width/length, does not matter
    aspect_ratio: float = (cv2.norm(min_area_box[0] - min_area_box[1])) / (
        cv2.norm(min_area_box[1] - min_area_box[2])
    )
    # pylint made me format the comparison like this
    return 1 - max_box_ratio_range < aspect_ratio < 1 + max_box_ratio_range


def test_bounding_box(
    contour: consts.Contour, dims: tuple[int, int], test_area_ratio: float = 10.0
) -> bool:
    """
    Calculates the area of an upright bounding box around the given contour
    and compares it to the rectangle (image) of the given dimensions

    Parameters
    ----------
    contour : consts.Contour
        The individual contour to be evaluated (as returned from cv2.findContours)
    dims : tuple[int, int]
        The dimensions of the image the contour is from
        dim_height : int
            The height of the image
        dim_width : int
            The width of the image
    test_area_ratio : float = 10.0
        The minimum acceptable ratio of image area to contour bounding box area

    Returns
    -------
    acceptable_area_ratio : bool
        Returns true if the bounding box area is less than the image area by a factor of
        test_area_ratio or more
    """
    bounding_box_retval: tuple[int, int, int, int] = cv2.boundingRect(contour)
    bounding_box: bbox.BoundingBox = bbox.BoundingBox(
        bbox.tlwh_to_vertices(
            bounding_box_retval[1],
            bounding_box_retval[0],
            bounding_box_retval[3] - bounding_box_retval[1],
            bounding_box_retval[2] - bounding_box_retval[0],
        ),
        bbox.ObjectType.STD_OBJECT,
    )

    box_area: float = bounding_box.get_height() * bounding_box.get_width()
    img_area: float = dims[0] * dims[1]

    return box_area * test_area_ratio <= img_area


def test_spikiness(contour: consts.Contour) -> bool:
    """
    Checks whether the contour has some points that are much farther away from the center of mass
    than the rest of the points
    basically real shapes will not have random points that are really far away from the rest
    but a weird patch of grass or something without well defined edges will have crazy points
    all over the place

    Parameters
    ----------
    contour : consts.Contour
        The individual contour to be evaluated (as returned from cv2.findContours)

    Returns
    -------
    lacks_spikes : bool
        True unless there is a statistical outlier point that is uniquely far away (or close ig)

    References
    -----
    This function uses a concept called the "Image moment" to calculate the center of a given
    contour. More information can be found here: https://en.wikipedia.org/wiki/Image_moment
    """
    moments: dict[str, float] = cv2.moments(contour)
    # com is Center of Mass, com = (y_coord, x_coord)
    # m01/m00 is the y coordinate of the center of the contour
    # m10/m00 is the x coordinate of the center of the contour
    com: NDArray[Shape["2"], Float32] = np.array(
        ((moments["m01"] / moments["m00"]), (moments["m10"] / moments["m00"])), dtype=np.float64
    )

    # numpy array that will hold the distance of each point in the contour to the center of the
    # contour
    dists_com: NDArray[Shape["*"], Float32] = np.ndarray(contour.shape[0], Float32)
    for i in range(contour.shape[0]):
        dists_com[i] = cv2.norm(contour[i] - com)

    # calculate the average distance from the center of the contour
    dists_mean: float = np.mean(dists_com)
    # calculate the statistical outlier range of the set of distances to the center of all of the
    # points in the contour, this is 3*standard deviation of the set of distances
    dists_outlier_range: float = 3.0 * np.std(dists_com)

    # if all of the points are within 3 standard deviations of the avg distance to the center of
    # the contour, then there are no statistical outliers
    # Also pylint made me format the comparison like this
    if np.all(dists_com < dists_mean + dists_outlier_range):
        return True
    return False


def min_common_bounding_box(contours: list[consts.Contour]) -> bbox.BoundingBox:
    """
    Takes a set of contours and returns the smallest bounding
    box that encloses all of them

    Parameters
    ----------
    contours : tuple[consts.Contour]
        Tuple of contours as formatted in cv2.findContour to find the minimum common bounding box

    Returns
    -------
    minimum_commom_bounding_box : bbox.BoundingBox
        The smallest bounding box that encompases all of the given contours
    """

    boxes: list[bbox.BoundingBox] = []
    for contour in contours:
        # tuple[int, int, int, int] is the return type of cv2.boundingRect()
        # the first two are the (y, x) of top left corner
        # the last two are the (y, x) of the bottom right corner
        contour_box: tuple[int, int, int, int] = cv2.boundingRect(contour)

        boxes.append(
            bbox.BoundingBox(
                bbox.tlwh_to_vertices(
                    contour_box[1],
                    contour_box[0],
                    contour_box[3] - contour_box[1],
                    contour_box[2] - contour_box[0],
                ),
                bbox.ObjectType.STD_OBJECT,
            )
        )

    min_x: int = np.min(np.array([box.get_x_extremes()[0] for box in boxes]))
    max_x: int = np.max(np.array([box.get_x_extremes()[1] for box in boxes]))
    min_y: int = np.min(np.array([box.get_y_extremes()[0] for box in boxes]))
    max_y: int = np.max(np.array([box.get_y_extremes()[1] for box in boxes]))
    min_box: bbox.BoundingBox = bbox.BoundingBox(
        ((min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)), bbox.ObjectType.STD_OBJECT
    )
    return min_box


def generate_mask(contour: consts.Contour, box: bbox.BoundingBox) -> consts.Mask:
    """
    Will create a mask with the dimensions of the given bounding box that is true for any point
    that is inside the contour.

    Parameters
    ----------
    contour : consts.Contour
        The individual contour to be evaluated (as returned from cv2.findContours)
    box : bbox.BoundingBox
        The bounding box that will be used to create the mask image, the mask will be the size of
        box and will offset the contour so that it is inside of the box

    Returns
    -------
    contour_mask : consts.Mask
        A MaskType that is the dimensions of the input bounding box and is true wherever is
        inside of the input contour
    """
    dims: tuple[int, int] = box.get_width_height()[::-1]
    shifted_cnt: consts.Contour = contour - np.array(box.vertices[0][::-1])

    mask: consts.Mask = np.zeros(dims)
    mask = cv2.drawContours(mask, [shifted_cnt], -1, True, cv2.FILLED)
    return mask


def test_roughness(
    contour: consts.Contour, approx: consts.Contour, test_percent_diff: float = 0.05
) -> bool:
    """
    Will check how rough the sides of a shape are. If the contour is an actual shape, then it will
    have relatively smooth sides, and the approximated contour will not have a lot of change. If
    the contour is not actually a shape (ie a patch of grass), then its sides will be less
    straight, and the polygon approximation will be very different from the original.

    Parameters
    ----------
    contour : consts.Contour
        The originally found contour to be evaluated (as returned from cv2.findContours)
    approx : consts.Contour
        The contour (same as contour param) but run through an approximation algoritm
        such as cv2.approxPolyDP(contour, 0.05*cv2.arcLength(contour, True), True)
                                          ^^^^can be tweaked
    test_percent_diff : float = 0.05
        The max percent difference in area allowed between the original and approximaed contour

    Returns
    -------
    lacks_roughness : bool
        Returns true if the non-overlapping area between the two contours is less than the
        specified percentage of the original contour's area, false otherwise
    """
    # finds one box that will fit both shapes
    box: bbox.BoundingBox = min_common_bounding_box([contour, approx])

    # generates masks (single channel binary images/matricies) for both shapes with white being
    # any point that is in the shape and black being everywhere else
    # the dimensions of the masks will be the same (both equal to the dimensions of the previously
    # found box)
    contour_mask: consts.Mask = generate_mask(contour, box)
    approx_mask: consts.Mask = generate_mask(approx, box)

    # makes a new mask where white is any point that was in one shape but not the other
    # aka a logical_xor between the two matricies of booleans
    non_overlap_mask: consts.Mask = np.logical_xor(contour_mask, approx_mask)

    # converts the boolean image to a single channel 8-bit image (still binarized with 0 and 255)
    non_overlap_img: consts.ScImage = non_overlap_mask.astype(UInt8)
    # detects all of the new shapes made by the xor operation
    non_overlap_cnts: tuple[consts.Contour]
    non_overlap_cnts, _ = cv2.findContours(non_overlap_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # sums the area of all of the non-overlapping portions of the shapes
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


def test_circleness(img: consts.ScImage) -> bool:
    """
    This function will test the cropped area around a given contour to see if it is a circle or if
    it is not a circle, it uses the cv2.HoughCircles() function to check for a circle

    Parameters
    ----------
    img : consts.ScImage
        Img should be grayscale cropped box around contour and PROCESSED ALREADY
        as in the image is binary with the contour filled in as white
        NOTE: sc_image_type denotes a single channel image

    Returns
    -------
    is_circular : bool
        Returns true if circle of appropriate size is found (to reduce chance of false positives)
    """
    padding: int = int(img.shape[0] * 0.05)
    modded: consts.ScImage = cv2.copyMakeBorder(
        img, padding, padding, padding, padding, cv2.BORDER_CONSTANT, None, 0
    )
    # 5 chosen arbitrarily as the kernel size and sigmaX params for the blur function
    # (kernel size and sigmaX are both parameters of cv2.GaussianBlur())
    # the number should not be very important because the input image is a binarized image
    modded = cv2.GaussianBlur(img, (5, 5), 5)
    # NDArray[Shape["1, *, 3"], Float32] is return type of cv2.HoughCircles()
    # format is [[[center_x_1, center_y_1, radius_1], [center_x_2, center_y_2, radius_2], ...]]
    circles: NDArray[Shape["1, *, 3"], Float32] | None = cv2.HoughCircles(
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

    # circles[0] is the actual array of circles because for some reason opencv puts this inside of
    # another list as the only element
    for circle in circles[0]:
        if int(max(img.shape[0], img.shape[1]) / 1.6) <= circle[2] and circle[2] <= int(
            min(img.shape[0], img.shape[1]) * 1.1
        ):
            return True

    return False


def filter_contour(
    contours: list[consts.Contour],
    hierarchy: consts.Hierarchy,
    index: int,
    image_dims: tuple[int, int],
    approx_contour: consts.Contour | None = None,
) -> bool:
    """
    Runs all created test functions and handles logic to determine if a given contour (from the
    tuple of contours) is an ODLC shape or not

    Parameters
    ----------
    contours : list[consts.Contour]
        The list of contours returned by the contour detection algorithm
        NOTE: cv2.findContours() returns as a tuple of arbitrary length, so first convert to list
    hierarchy : consts.Hierarchy
        The contour hierarchy list returned by the contour detection algorithm
        (the 2nd value returned by cv2.findContours())
    index : int
        The index corresponding to the contour in contours and hierarchy to be checked
        (must be in bounds of contours tuple and hierarchy array)
    image_dims : tuple[int, int]
        The dimensions of the original entire image
        (only height and width as gotten from image.shape[:2], not the color channels)
        image_dim_height : int
            The height dimension of the image
        image_dim_width : int
            The width dimension of the image
    approx_contour : consts.Contour | None = None
        Optional parameter to provide the approximated version (from cv2.approxPolyDP) of the
        contour to be checked to avoid recalculation
        This is None by default, it is only not None when the approximated contour is provided

    Returns
    -------
    is_odlc : bool
        True if the contour is (probably) an ODLC shape, False o.w.

    Notes
    -----
    Possibly in future could modifiy the filter_contour() function to return two booleans
    one to determine if there is a shape, another to determine if the detected shape was circular
    (or an integer could be used, ie: 0=no shape, 1=shape, 2=circular shape)
    """
    # test hierarchy, bounding_box, min_area_box, and spikiness
    if (
        (not test_heirarchy(hierarchy, index))
        or (not test_bounding_box(contours[index], image_dims))
        or (not test_min_area_box(contours[index]))
        or (not test_spikiness(contours[index]))
    ):
        return False
    # then calculate approxPolyDP if above all pass (maybe change depending on test results)
    if approx_contour is None:
        approx_contour = cv2.approxPolyDP(
            contours[index], cv2.arcLength(contours[index], True) * 0.05, True
        )

    # run polygon specific test
    if not test_roughness(contours[index], approx_contour):
        # if polygon test fails run circle test

        # tuple[int, int, int, int] is the return type of cv2.boundingRect()
        # the first two are the (y, x) of top left corner
        # the last two are the (y, x) of the bottom right corner
        cnt_bound_box_retval: tuple[int, int, int, int] = cv2.boundingRect(contours[index])
        cnt_bound_box: bbox.BoundingBox = bbox.BoundingBox(
            bbox.tlwh_to_vertices(
                cnt_bound_box_retval[1],
                cnt_bound_box_retval[0],
                cnt_bound_box_retval[3] - cnt_bound_box_retval[1],
                cnt_bound_box_retval[2] - cnt_bound_box_retval[0],
            ),
            bbox.ObjectType.STD_OBJECT,
        )
        # use _generate_mask to get a mask of the shape then cvt bool image to UInt8
        cnt_mask: consts.Mask = generate_mask(contours[index], cnt_bound_box)
        cnt_sc_img: consts.ScImage = np.where(cnt_mask, 255, 0).astype(np.uint8)

        if not test_circleness(cnt_sc_img):
            return False

    return True


# All of main is some basic testing code
if __name__ == "__main__":
    # create a blank image
    test_image1: consts.Image = np.zeros([5000, 5000, 3], dtype=UInt8)

    # define some points to make a polygon, there is some draw circle function to try circles also
    raw_pts: NDArray[Shape["*, 2"], IntC] = np.array(
        [[249, 0], [499, 249], [249, 499], [0, 249]], IntC
    )
    pts: consts.Contour = raw_pts.reshape((-1, 1, 2))
    # put the points on the image
    test_image1 = cv2.polylines(test_image1, [pts], True, (255, 255, 255))

    cv2.imshow("pic", test_image1)
    cv2.waitKey(0)
    # make single channel to do contour stuff
    test_image: consts.ScImage = cv2.cvtColor(test_image1, cv2.COLOR_BGR2GRAY)

    # a variable length tuple is not good practice, but that is what opencv does here
    # cnts_tmp: tuple(consts.Contour, ...) # also this gives a TypeError for some reason
    hier_tmp: consts.Hierarchy
    cnts_tmp, hier_tmp = cv2.findContours(test_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    print("contours1:", type(cnts_tmp), len(cnts_tmp), cnts_tmp)
    img2: consts.Image = np.dstack((test_image, test_image, test_image))

    # paint a filled in shape
    img2 = cv2.drawContours(img2, cnts_tmp, 0, (255, 255, 255), thickness=cv2.FILLED)
    cv2.imshow("cnts1-0", img2)
    cv2.waitKey(0)

    # find the contours for "real" my code doesnt do that, this is just to generate test contours
    # cnts: tuple(consts.Contour, ...)
    hier: consts.Hierarchy
    cnts, hier = cv2.findContours(test_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # for each contour run all of the tests on it
    ind: int
    cntr: consts.Contour
    for ind, cntr in enumerate(cnts):
        # the next 4 "lines" of code create a cropped ScImage around the contour to pass to
        # circle detection function
        cntr_bbox_retval: tuple[int, int, int, int] = cv2.boundingRect(cntr)
        cntr_bbox: bbox.BoundingBox = bbox.BoundingBox(
            bbox.tlwh_to_vertices(
                cntr_bbox_retval[1],
                cntr_bbox_retval[0],
                cntr_bbox_retval[3] - cntr_bbox_retval[1],
                cntr_bbox_retval[2] - cntr_bbox_retval[0],
            ),
            bbox.ObjectType.STD_OBJECT,
        )
        cntr_msk: consts.Mask = generate_mask(cntr, cntr_bbox)
        cntr_sc_img: consts.ScImage = np.where(cntr_msk, 255, 0).astype(np.uint8)
        print(type(cntr_sc_img), type(cntr_sc_img[0]), type(cntr_sc_img[0, 0]))
        # actually running each test individually and printing results for testing/debugging
        print("\nHierarchy Test:", test_heirarchy(hier, ind))
        print("Min Area Box Test:", test_min_area_box(cntr))
        print(
            "Bounding Box Test:",
            test_bounding_box(cntr, (test_image.shape[0], test_image.shape[1])),
        )
        print("Jaggedness Test:", test_spikiness(cntr))
        # generates an arbitrary polygon approximation of the contour (tries to remove redundant
        # points that do not make the contour much different)
        peri: float = cv2.arcLength(cntr, True)
        approximate: consts.Contour = cv2.approxPolyDP(cntr, 0.05 * peri, True)
        print("Polygonness Test:", test_roughness(cntr, approximate))
        print("Circleness Test:", test_circleness(img2[:, :, 0]))
