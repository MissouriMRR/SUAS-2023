"""
Takes the contour of an ODLC shape and determine which shape it is
"""

import numpy as np
import nptyping as npt
import cv2
import vision.common.constants as consts
import vision.common.odlc_characteristics as chars
import vision.standard_object.odlc_contour_filtering as filtering
import vision.common.bounding_box as bbox


# constants
MAX_CHILD_AMT: int = 2
# The max number of (direct) child contours that a contour can have and be considered

RIGHT_ANG_THRESH: float = 5.0
# When checking if quadrilateral has right angles the max range of angles allowed (ex 85 to 95)

SIDE_LEN_EQ_THRESH: float = 0.05
# when comparing the side lengths of a shape for equality, the max difference allowed

SHAPE_ASPECT_RATIO_RANGE: float = 0.15
# some shapes are expected to not be oblong (oblong shapes being rectangle, trapezoid, semicircle,
# etc) this value is the max that the shape can be wider than long (calculated with a rotated,
# not upright bounding box)

APPROX_CNT_EPSILON: float = 5.0
# Value used for epsilon parameter for polygon contour approximation in cv2.approxPolyDP()
# epsilon is the max distance between the approximation's and the original's curves

QUARTER_CIRCLE_RATIO: float = 0.280
# 0.280 is ratio of radius to total perimeter of quarter circle = r / (r + r + pi*r/2)

SEMICIRCLE_RATIO: float = 0.389
# 0.389 is ratio of diameter to total perimeter of semi circle = 2r / (2r + pi*r)

CIRCULAR_RATIO_RANGE: float = 0.054
# The max amount that the calculated ratio in classify_circular() may differ from the exact value
# NOTE: do not set to above 0.054, this will result in overlap between two ratio ranges


def process_shapes(
    contours: list[consts.Contour], hierarchy: consts.Hierarchy, image_dims: tuple[int, int]
) -> list[bbox.BoundingBox]:
    """
    Takes all of the contours of an image and will return BoundingBox list w/ shape attributes

    Parameters
    ----------
    contours : list[consts.Contour]
        List of all contours from the image (from cv2.findContours())
        NOTE: cv2.findContours() returns as a tuple, so convert it to list w/ list(the_tuple)
    hierarchy : consts.Hierarchy
        The contour hierarchy information returned from cv2.findContours()
        (The 2nd returned value)
    image_dims : tuple[int, int]
        The dimensions of the image the contours are from.
        y_dim : int
            Image height.
        x_dim : int
            Image width.

    Returns
    -------
    bounding_boxes : list[bbox.BoundingBox]
        A list of BoundingBox objects that are the upright bounding box arround each corresponding
        contour at same index in list and with an attribute that is {"shape": chars.ODLCShape}
        with the identified shape or {"shape": None} if the contour does not match any.
    """
    retval_boxes: list[tuple[int, int, int, int]] = [cv2.boundingRect(cnt) for cnt in contours]
    verts_lst: list[bbox.Vertices] = [
        bbox.tlwh_to_vertices(retval_box[0], retval_box[1], retval_box[2], retval_box[3])
        for retval_box in retval_boxes
    ]
    boxes: list[bbox.BoundingBox] = [
        bbox.BoundingBox(verts, bbox.ObjectType.STD_OBJECT) for verts in verts_lst
    ]

    shape_boxes: list[bbox.BoundingBox] = []

    idx: int
    hier: npt.NDArray[npt.Shape["4"], npt.IntC]
    box: bbox.BoundingBox
    # for each contour (and corresponding elements in hierarchy array and box list)
    for idx, (hier, box) in enumerate(zip(hierarchy[0], boxes)):
        classification: chars.ODLCShape | None

        # as long as the contour is not inside another contour that has been classified as a shape
        if (
            hier[3] == -1
            or not boxes[hier[3]].attributes
            or boxes[hier[3]].attributes["shape"] is None
        ) and get_child_amt(idx, hierarchy) <= MAX_CHILD_AMT:
            classification = classify_shape(contours[idx], image_dims)
        else:
            # if the contour is inside an identified ODLC shape then it should not be recognized
            classification = None

        if classification is not None:
            box.set_attribute("shape", classification)
            shape_boxes.append(box)

    return shape_boxes


def classify_shape(
    contour: consts.Contour,
    image_dims: tuple[int, int],
    approx_contour: consts.Contour | None = None,
) -> chars.ODLCShape | None:
    """
    Will first determine whether the specified contour is an ODLC shape, then will determine
    which ODLC shape it is.

    Parameters
    ----------
    contour : consts.Contour
        A contour returned by the contour detection algorithm
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
    shape : chars.ODLCShape | None
        Will return one of the ODLC shapes defined in vision/common/odlc_characteristics or None
        if the given contour is not an ODLC shape (fails filtering or doesnt match any ODLC)
    """
    if approx_contour is None:
        approx_contour = cv2.approxPolyDP(contour, APPROX_CNT_EPSILON, True)

    is_shape: bool
    is_circular: bool
    is_shape, is_circular = filtering.filter_contour(contour, image_dims, approx_contour)

    if not is_shape:
        return None

    defects: int = check_concavity(approx_contour)

    shape: chars.ODLCShape | None
    if defects not in {0, 4, 5}:
        shape = None  # if has not 0, 4, or 5 defects then not a valid shape
    elif is_circular and defects == 0:
        shape = classify_circular(contour)
    else:
        shape = check_polygons(approx_contour)

        if (defects == 4) ^ (shape == chars.ODLCShape.CROSS):  # logical xor
            shape = None  # one of above cannot be true while the other is false if valid shape
        elif (defects == 5) ^ (shape == chars.ODLCShape.STAR):
            shape = None  # one of above cannot be true while the other is false if valid shape

    return shape


def get_child_amt(idx: int, hier: consts.Hierarchy) -> int:
    """
    Returns the number of child contours that the contour at the given idx has.
    Does not count children of children.

    Parameters
    ----------
    idx : int
        The index of the contour to count the number of children of (idx < len(hier))
    hier : consts.Hierarchy
        The structure that contains the contour hierarchy information

    Returns
    -------
    count : int
        The number of (direct) children that the given contour has
    """
    count: int = 1
    curr: int = hier[0, idx, 2]

    if curr == -1:
        return 0

    while hier[0, curr, 0] != -1:
        curr = hier[0, curr, 0]
        count += 1

    return count


def check_concavity(approx: consts.Contour) -> int:
    """
    Counts for the number of convexity defects that a shape has.

    Parameters
    ----------
    approx : consts.Contour
        Approximated version of the contour (polygon approximation with cv2.approxPolyDP())

    Returns
    -------
    defects_amt : int
        The number of defects that the given contour has.
    """
    # cv2.convexHull() will give a new contour that has filled out any concave "dents" in the
    # given contour. Can be thought of as taking the shape a rubber band makes around the contour
    convex_hull: npt.NDArray[npt.Shape["*, 1"], npt.IntC] = cv2.convexHull(
        approx, returnPoints=False
    )

    # cv2.convexityDefects takes result of cv2.convexHull() and original contour and returns all
    # of the points where the two shapes differ.
    # in rubber band analogy, counting the number of gaps between the shape and the rubber band
    # eg. a plus has 4 corners that point inward so the rubber band would not touch it in 4 spots
    defects: npt.NDArray[npt.Shape["*, 1, 4"], npt.IntC] | None = cv2.convexityDefects(
        approx, convex_hull
    )

    return len(defects) if defects is not None else 0


def get_angle(
    pts: tuple[
        npt.NDArray[npt.Shape["1, 2"], npt.IntC],
        npt.NDArray[npt.Shape["1, 2"], npt.IntC],
        npt.NDArray[npt.Shape["1, 2"], npt.IntC],
    ]
) -> npt.Float64:
    """
    Takes 3 points and calculates the angle they make.

    Parameters
    ----------
    pts : tuple[
        npt.NDArray[npt.Shape["1, 2"], npt.IntC],
        npt.NDArray[npt.Shape["1, 2"], npt.IntC],
        npt.NDArray[npt.Shape["1, 2"], npt.IntC]
    ]
        Three points that make an angle that will be calculated
        All points formatted as done in openCV [[y, x]].
        pt_a : npt.NDArray[npt.Shape["1, 2"], npt.IntC]
            One of the points that form the angle, 0th index in the tuple.
        vertex : npt.NDArray[npt.Shape["1, 2"], npt.IntC]
            The point that is in the middle, where the angle is, 1st index in the tuple.
        pt_b : npt.NDArray[npt.Shape["1, 2"], npt.IntC]
            The other point that forms the angle, 2nd index in the tuple.

    Returns
    -------
    angle : npt.Float64
        The angle (in deg) of the angle formed by the lines (pt_a, vertex) and (vertex, pt_b)

    Notes
    -----
    Angle formula is derived from vector dot product (the one that uses the angle between vectors)
    If there are vectors a and b with angle t between them then:
        a.b = ||a||*||b||*cos(t)
        (Where a.b is the dot product of a and b)
    This can be rearranged to:
        t = arccos((a.b) / (||a||*||b||))
    """
    # vector forms of points a (pts[0]) and b (pts[2]) with vertex (pts[1]) as origin
    vec_a: npt.NDArray[npt.Shape["1, 2"], npt.IntC] = pts[0] - pts[1]
    vec_b: npt.NDArray[npt.Shape["1, 2"], npt.IntC] = pts[2] - pts[1]

    vec_a = np.squeeze(vec_a)
    vec_b = np.squeeze(vec_b)

    return np.degrees(
        np.arccos(np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b)))
    )


def get_angles(approx: consts.Contour) -> npt.NDArray[npt.Shape["*"], npt.Float64]:
    """
    Will find the angle at every point in the given approximated contour.

    Parameters
    ----------
    approx : consts.Contour
        Approximated version of the contour (polygon approximation with cv2.approxPolyDP())

    Returns
    -------
    angles : npt.NDArray[npt.Shape["*"], npt.Float64]
        1d array of angles for each corresponding vertex in the given approximated contour
    """
    angles: npt.NDArray[npt.Shape["*"], npt.Float64] = np.empty(approx.shape[0], npt.Float64)
    idx: int
    a_pt: npt.NDArray[npt.Shape["1, 2"], npt.IntC]  # one point of the approx contour
    for idx, a_pt in enumerate(approx):
        angles[idx] = get_angle((approx[idx - 1], a_pt, approx[(idx + 1) % approx.shape[0]]))

    return angles


def compare_angles(
    angles: npt.NDArray[npt.Shape["*"], npt.Float64], compare_angle: float, thresh: float
) -> npt.NDArray[npt.Shape["*"], npt.Bool8]:
    """
    Takes an array, angles, and compares each element against a specific angle.

    Parameters
    ----------
    angles : npt.NDArray[npt.Shape["*"], npt.Float64]
        An array of angles of some contour (assumed in degrees but would work if all values are
        the same unit)
    compare_angle : float
        The value to compare each element of angles to.
    thresh : float
        The range on each side of angle that each element of angles may be and still pass.

    Returns
    -------
    are_valid : npt.NDArray[npt.Shape["*"], npt.Bool8]
        Each element represents whether the corresponding element of angles was within thresh
        of angle
    """
    are_valid: npt.NDArray[npt.Shape["*"], npt.Bool8] = np.empty(angles.shape[0], npt.Bool8)
    idx: int
    ang: npt.Float64  # each individual angle in angles
    for idx, ang in enumerate(angles):
        are_valid[idx] = abs(ang - compare_angle) < thresh

    return are_valid


def get_lengths(cnt: consts.Contour) -> npt.NDArray[npt.Shape["*"], npt.Float64]:
    """
    Takes a closed contour and will return an array of all its side lengths.

    Parameters
    ----------
    cnt : consts.Contour
        The contour that this will calculate all of the lengths between consecutive points of
        If approximated with cv2.approxPolyDP(), then each length will be a side length

    Returns
    -------
    lengths : npt.NDArray[npt.Shape["*"], npt.Float64]
        Array of each side length of the given approximated contour
        Or just length between consecutive points in an unapproximated contour
    """
    lengths: npt.NDArray[npt.Shape["*"], npt.Float64] = np.empty(cnt.shape[0], npt.Float64)
    idx: int
    cnt_pt: npt.NDArray[npt.Shape["1, 2"], npt.IntC]  # each point in the contour
    for idx, cnt_pt in enumerate(cnt):
        lengths[idx] = np.sqrt(
            np.square(cnt_pt[0, 0] - cnt[(idx + 1) % cnt.shape[0], 0, 0])
            + np.square(cnt_pt[0, 1] - cnt[(idx + 1) % cnt.shape[0], 0, 1])
        )

    return lengths


def check_polygons(approx: consts.Contour) -> chars.ODLCShape | None:
    """
    Checks the shape against the possible noncircular odlc polygons based on number of sides.

    Parameters
    ----------
    approx : consts.Contour
        Approximated version of the contour (polygon approximation with cv2.approxPolyDP())

    Returns
    -------
    polygonal_shape : chars.ODLCShape | None
        Will return one of TRIANGLE, SQUARE, RECTANGLE, TRAPEZOID, PENTAGON, HEXAGON, OCTAGON,
        STAR, or CROSS from ODLCShape Enum or None if shape does not match any of these.
    """
    lengths: npt.NDArray[npt.Shape["*"], npt.Float64] = get_lengths(approx)
    has_eq_side_lengths: bool = compare_side_len_eq(lengths)
    good_aspect_ratio: bool = filtering.test_min_area_box(approx, SHAPE_ASPECT_RATIO_RANGE)

    angles: npt.NDArray[npt.Shape["*"], npt.Float64]
    shape: chars.ODLCShape | None = None
    match len(approx):
        case 3:
            shape = chars.ODLCShape.TRIANGLE
        case 4:
            angles = get_angles(approx)
            # if all angles approximately 90 deg, square or rectangle, else trapezoid
            if np.all(compare_angles(angles, 90, RIGHT_ANG_THRESH)):
                # if all side lengths are (approximately) equal then square, else rectangle
                if has_eq_side_lengths and good_aspect_ratio:
                    shape = chars.ODLCShape.SQUARE
                else:
                    shape = chars.ODLCShape.RECTANGLE
            else:
                shape = chars.ODLCShape.TRAPEZOID
        case 5:
            if good_aspect_ratio:
                shape = chars.ODLCShape.PENTAGON
        case 6:
            if good_aspect_ratio:
                shape = chars.ODLCShape.HEXAGON
        case 7:
            if good_aspect_ratio:
                shape = chars.ODLCShape.HEPTAGON
        case 8:
            if good_aspect_ratio:
                shape = chars.ODLCShape.OCTAGON
        case 10:
            if has_eq_side_lengths:
                shape = chars.ODLCShape.STAR
        case 12:
            angles = get_angles(approx)
            # a plus shape should have exactly 8 right angles *inside* of it (2 on each bar)
            if np.count_nonzero(compare_angles(angles, 90, RIGHT_ANG_THRESH)) == 8:
                shape = chars.ODLCShape.CROSS
        case _:
            shape = None

    return shape


def compare_side_len_eq(lengs: npt.NDArray[npt.Shape["*"], npt.Float64]) -> bool:
    """
    Checks if all of the side lengths given are (approximately) equal.

    Parameters
    ----------
    lengths : npt.NDArray[npt.Shape["*"], npt.Float64]
        An array of all the side lengths of a polygon (from get_lengths())

    Returns
    -------
    eq_side_lengths : bool
        True if all of the given side lengths are approximately equal
    """
    return bool(
        np.all(np.where(abs((lengs / np.mean(lengs)) - 1) < SIDE_LEN_EQ_THRESH, True, False))
    )


def classify_circular(contour: consts.Contour) -> chars.ODLCShape:
    """
    Determines which circular shape the given contour is (assumed to be a circular shape)

    Parameters
    ----------
    contour : consts.Contour
        The original contour to evaluate

    Returns
    -------
    circular_shape : chars.ODLCShape
        Will return one of CIRCLE, SEMICIRCLE, QUARTER_CIRCLE from ODLCShape Enum

    Notes
    -----
    Alternative method to determine which circular shape could be to see how many right angles
    the given shape has a quarter-circle may have 1 or 3 (if corner between straight line and
    curve show up as a right angle), and a semicircle would have 0 or 2 for same reason. But
    a regular circle would have 0 right angles, which may conflict with semicircle.
    """
    approx: consts.Contour = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.01, True)
    max_dist: npt.Float64 = np.max(get_lengths(approx))
    perimeter: npt.Float64 = cv2.arcLength(contour, True)

    if abs((max_dist / perimeter) - QUARTER_CIRCLE_RATIO) < CIRCULAR_RATIO_RANGE:
        return chars.ODLCShape.QUARTER_CIRCLE

    if abs((max_dist / perimeter) - SEMICIRCLE_RATIO) < CIRCULAR_RATIO_RANGE:
        return chars.ODLCShape.SEMICIRCLE
    return chars.ODLCShape.CIRCLE


if __name__ == "__main__":
    # make some test shape
    main_shape: consts.Contour = np.array(
        [[[0, 0]], [[5, 5]], [[0, 10]], [[10, 10]], [[5, 5]], [[10, 0]]]
    )
    # make an approximation
    main_approx: consts.Contour = cv2.approxPolyDP(main_shape, APPROX_CNT_EPSILON, True)

    print(type(main_shape), main_shape.shape, main_shape)
    print(type(main_approx), main_approx.shape, main_approx)
    # run each individual internal testing function to check behavior
    print(check_concavity(main_shape))
    print(check_polygons(main_approx))
    print(classify_circular(main_shape))
