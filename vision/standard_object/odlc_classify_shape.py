"""
Takes the contour of an ODLC shape and determine which shape it is
"""
import numpy as np
import nptyping as npt
import cv2
import vision.common.constants as consts
import vision.common.odlc_characteristics as chars
import vision.standard_object.odlc_contour_filtering as filtering


# constants
QUAD_ANG_THRESH: float = 5.0
# When checking if quadrilateral has right angles the max range of angles allowed (ex 85 to 95)

QUAD_LEN_THRESH: float = 0.05
# when comparing the side lengths of a quadrilateral, the max diff and it still be a square

APPROX_CNT_THRESH: float = 0.05
# Value used to calculate epsilon parameter for polygon contour approximation
# epsilon is the max distance between the approximation's and the original's curves

QUARTER_CIRCLE_RATIO: float = 0.280
# 0.280 is ratio of radius to total perimeter of quarter circle = r / (r + r + pi*r/2)

SEMICIRCLE_RATIO: float = 0.389
# 0.388 is ratio of diameter to total perimeter of semi circle = 2r / (2r + pi*r)

CIRCULAR_RATIO_RANGE: float = 0.1
# The max amount that the calculated ratio in classify_circular() may differ from the exact value
# NOTE: do not set to above 0.109, this will result in overlap between two ratios


def check_concave_shapes(approx: consts.Contour) -> chars.ODLCShape | None:
    """
    Checks if the shape is a plus or star because these are concave shapes and will have inside
    angles that are >180 deg.

    Parameters
    ----------
    approx : consts.Contour
        Approximated version of the contour (polygon approximation with cv2.approxPolyDP())

    Returns
    -------
    concave_shape : chars.ODLCShape | None
        Will return STAR or CROSS from ODLCShape Enum or None if shape is neither of these
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

    if defects is not None:
        if len(defects) == 5:
            return chars.ODLCShape.STAR
        if len(defects) == 4:
            return chars.ODLCShape.CROSS
    return None


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
        pt_a : npt.NDArray[npt.Shape["1, 2"], npt.IntC]
            One of the points that form the angle, 0th index in the tuple.
            All points formatted as done in openCV [[y, x]].
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
        are_valid[idx] = -thresh < ang - compare_angle < thresh

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
    Checks the shape against the possible "regular" odlc polygons, not regular the geometric term,
    regular as in not concave or (partly) circular.

    Parameters
    ----------
    approx : consts.Contour
        Approximated version of the contour (polygon approximation with cv2.approxPolyDP())

    Returns
    -------
    polygonal_shape : chars.ODLCShape | None
        Will return one of TRIANGLE, SQUARE, RECTANGLE, TRAPEZOID, PENTAGON, HEXAGON, or OCTAGON
        from ODLCShape Enum or None if shape does not match any of these.
    """
    shape: chars.ODLCShape | None = None
    match len(approx):
        case 3:
            shape = chars.ODLCShape.TRIANGLE
        case 4:
            angles: npt.NDArray[npt.Shape["*"], npt.Float64] = get_angles(approx)
            if np.all(compare_angles(angles, 90, QUAD_ANG_THRESH)):
                lengths: npt.NDArray[npt.Shape["*"], npt.Float64] = get_lengths(approx)
                if (lengths[0]) / (np.sum(lengths) / 4) < QUAD_LEN_THRESH:
                    shape = chars.ODLCShape.SQUARE
                else:
                    shape = chars.ODLCShape.RECTANGLE
            else:
                shape = chars.ODLCShape.TRAPEZOID
        case 5:
            shape = chars.ODLCShape.PENTAGON
        case 6:
            shape = chars.ODLCShape.HEXAGON
        case 7:
            shape = chars.ODLCShape.HEPTAGON
        case 8:
            shape = chars.ODLCShape.OCTAGON
        case _:
            shape = None

    return shape


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


def classify_shape(
    contours: list[consts.Contour],
    hierarchy: consts.Hierarchy,
    index: int,
    image_dims: tuple[int, int],
    approx_contour: consts.Contour | None = None,
) -> chars.ODLCShape | None:
    """
    Will first determine whether the specified contour is an ODLC shape, then will determine
    which ODLC shape it is.

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
    shape : chars.ODLCShape | None
        Will return one of the ODLC shapes defined in vision/common/odlc_characteristics or None
        if the given contour is not an ODLC shape (fails filtering or doesnt match any ODLC)
    """
    if approx_contour is None:
        approx_contour = cv2.approxPolyDP(
            contours[index], cv2.arcLength(contours[index], True) * APPROX_CNT_THRESH, True
        )

    is_shape: bool
    is_circular: bool
    is_shape, is_circular = filtering.filter_contour(
        contours, hierarchy, index, image_dims, approx_contour
    )

    if not is_shape:
        return None

    shape: chars.ODLCShape | None = None
    if is_circular:
        shape = classify_circular(contours[index])
    else:
        shape = check_concave_shapes(approx_contour)
        if shape is None:
            shape = check_polygons(approx_contour)

    return shape


if __name__ == "__main__":
    main_shape: consts.Contour = np.array(
        [[[0, 0]], [[5, 5]], [[0, 10]], [[10, 10]], [[5, 5]], [[10, 0]]]
    )
    main_approx: consts.Contour = cv2.approxPolyDP(
        main_shape, cv2.arcLength(main_shape, True) * 0.05, True
    )
    print(type(main_shape), main_shape.shape, main_shape)
    print(type(main_approx), main_approx.shape, main_approx)
    print(check_concave_shapes(main_shape))
    print(check_polygons(main_approx))
    print(classify_circular(main_shape))
