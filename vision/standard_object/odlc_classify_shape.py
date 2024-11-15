"""Takes the contour of an ODLC shape and determine which shape it is in the certain file path"""

import json
import cv2
import numpy as np
import scipy
from nptyping import NDArray, Shape, Float64
from scipy import signal
import scipy.interpolate
from typing import List, Tuple, TypeAlias
from vision.common import constants as consts
from vision.common import odlc_characteristics as chars
from vision.common.bounding_box import BoundingBox as bbox
from vision.common.bounding_box import tlwh_to_vertices
from vision.common.bounding_box import ObjectType

# constants
PolarArray: TypeAlias = NDArray[Shape["128"], Float64]

# Represents the number of intervals used when analyzing polar graph of shape
NUM_STEPS: int = 128

# Minimum prominence for a peak to be recognized on a shape contour
PROMINENCE: float = 0.05

# Lowered prominence to find all peaks of a cross
CROSS_PROMINENCE: float = 0.02

# Minimum allowed smallest radius to be considered a circle
MIN_CIRCLE_RADIUS: float = 0.9
# Minimum allowed difference between the shortest peaks of a quarter circle
MIN_DIFF_SHORT_PEAKS_QC: float = 0.10

# Maximum allowed difference between the longest peaks of a quarter circle
# Quarter Circle should have 2 long peaks which are very close in length,
# and one peak which is a bit shorter
MAX_DIFF_LONG_PEAKS_QC: float = 0.5

MIN_SMALLEST_RADIUS_RECTANGLE: float = 0.75

# Maximum allowed smallest radius for a shape to be considered a star
MAX_SMALLEST_RADIUS_STAR: float = 0.65

# The bottom percentage of a shape's polar graph that is removed to
# safely lower prominece and highlight the cross's slight peaks
PERCENT_CROSS_IGNORED: float = 0.85

# The maximum allowed average difference between points in
# compared shape to be considered the same type
MAX_ABS_ERROR: float = 1 / 6

# Read the appropriate Array from json file
SHAPE_JSON = "vision/standard_object/sample_ODLCs.json"

# Keys are the number of peaks, targets are the cooresponding shape
shape_from_peaks = {
    1: chars.ODLCShape.CIRCLE,
    2: chars.ODLCShape.SEMICIRCLE,
    4: chars.ODLCShape.RECTANGLE,
    8: chars.ODLCShape.CROSS,
}

# Keys are ODLC shapes, and targets are their cooresponding order their sample arrays are stored in
SHAPE_INDICES = {
    chars.ODLCShape.CIRCLE: 0,
    chars.ODLCShape.QUARTER_CIRCLE: 1,
    chars.ODLCShape.SEMICIRCLE: 2,
    chars.ODLCShape.TRIANGLE: 3,
    chars.ODLCShape.PENTAGON: 4,
    chars.ODLCShape.STAR: 5,
    chars.ODLCShape.RECTANGLE: 6,
    chars.ODLCShape.CROSS: 7,
}


def process_shapes(contours: list[consts.Contour]) -> list[bbox]:
    """
    Takes all of the contours of an image and will return BoundingBox list w/ shape attributes

    Parameters
    ----------
    contours : tuple[consts.Contour]
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
    bbox_list: List[bbox] = []
    for contour in contours:
        shape_type: chars.ODLCShape | None = classify_shape(np.copy(contour))
        vertices: consts.Corners
        min_x: int
        min_y: int
        width: int
        height: int
        min_x, min_y, width, height = cv2.boundingRect(contour)
        vertices = tlwh_to_vertices(min_x, min_y, width, height)

        bounding_box: bbox = bbox(vertices, ObjectType.STD_OBJECT, None)
        bounding_box.set_attribute("shape", shape_type)
        bbox_list.append(bounding_box)
    return bbox_list


def classify_shape(contour: consts.Contour) -> chars.ODLCShape | None:
    """
    Will determine if the contour matches any ODLC shape,
    then verify that choice by comparing to sample

    Parameters
    ----------
    contour : consts.Contour
        A contour returned by the contour detection algorithm

    Returns
    -------
    odlc_guess : chars.ODLCShape | None
        Will return one of the ODLC shapes defined in vision/common/odlc_characteristics or None
        if the given contour is not an ODLC shape (doesn't match any ODLC)
    """
    radius_polar_array: PolarArray = generate_polar_array(contour)
    odlc_guess: chars.ODLCShape | None = compare_based_on_peaks(radius_polar_array)
    return odlc_guess


def compare_based_on_peaks(polar_array: PolarArray) -> chars.ODLCShape | None:
    """
    Will determine if a polar array matches any ODLC shape,
    then verify that choice by comparing to sample

    Parameters
    ----------
    polar_array : PolarArray
        An array storing the radii values of a normalized polar array

    Returns
    -------
    shape : chars.ODLCShape | None
        Will return one of the ODLC shapes defined in vision/common/odlc_characteristics or None
        if the given contour is not an ODLC shape (doesnt match any ODLC)
    """

    min_index: int

    # Normalizes radii to all be between 0 and 1
    polar_array /= np.max(polar_array)
    # min_index = np.argmin(polar_array)
    min_index = int(np.argmin(polar_array))
    # Rolls all values to put minimum radius at x = 0
    polar_array = np.roll(polar_array, -min_index)

    peaks: NDArray[Shape["*"], Float64]
    peaks = signal.find_peaks(polar_array, prominence=PROMINENCE)[0]
    num_peaks: int
    num_peaks = len(peaks)
    odlc_guess: chars.ODLCShape | None

    # If the minimum value is greater than Maximum Radius
    # (e.g.. data may change), then it is a circle
    if polar_array[0] > MIN_CIRCLE_RADIUS:
        odlc_guess = chars.ODLCShape.CIRCLE

    # If we have a shape able to be uniquely defined by its number of peaks
    elif num_peaks in (2, 8):
        odlc_guess = shape_from_peaks[num_peaks]

    # Must narrow down from triangle or quarter circle
    elif num_peaks == 3:
        # Sort peaks in by increasing value
        peaks = np.asarray(peaks)
        peaks_vals: NDArray[Shape["3"], Float64] = np.zeros(3)
        peaks_vals = [polar_array[peak] for peak in peaks[:3]]
        peaks_vals = np.sort(peaks_vals)
        # If there is a small enough difference between 2 greatest peaks,
        # And large enough difference between 2 smallest peaks, we have
        # A quarter cricle
        if (
            peaks_vals[2] - peaks_vals[1] < MAX_DIFF_LONG_PEAKS_QC
            and peaks_vals[1] - peaks_vals[0] > MIN_DIFF_SHORT_PEAKS_QC
        ):
            odlc_guess = chars.ODLCShape.QUARTER_CIRCLE
        else:
            odlc_guess = chars.ODLCShape.TRIANGLE

    # Must narrow down from rectangle or crosses
    elif num_peaks in (4, 8):
        cropped_cross_array: PolarArray = [
            0 if val < PERCENT_CROSS_IGNORED else val for val in polar_array
        ]
        num_cross_peaks: int = len(
            signal.find_peaks(
                cropped_cross_array,
                prominence=CROSS_PROMINENCE,
            )[0]
        )
        # If minimum radius is less than .65 (65% of maximum radius), the we have a star
        if num_cross_peaks >= 5:
            odlc_guess = chars.ODLCShape.CROSS
        else:
            odlc_guess = chars.ODLCShape.RECTANGLE

    # Must narrow down from pentagon or star
    elif num_peaks == 5:
        minimum: float = np.min(polar_array)
        # If minimum radius is less than .65 (65% of maximum radius), the we have a star
        if minimum < MAX_SMALLEST_RADIUS_STAR:
            odlc_guess = chars.ODLCShape.STAR
        else:
            odlc_guess = chars.ODLCShape.PENTAGON

    else:
        # The number of peaks is outside of our range of detection
        # We will just assume there is no shape
        return None

    # This else states that is the upper 15% of a shape has 8 peaks
    # when prominence is decreased, it is likely a cross
    # This was added because many crosses were not showing 2 peaks per
    # "beam" in higher prominence, but rather those peaks were blending into one

    shape_json_address: str = SHAPE_JSON

    with open(shape_json_address, encoding="UTF-8") as sample_odlc_file:
        sample_shapes: NDArray[Shape["8, 128"], Float64] = json.load(sample_odlc_file)

    # Finds the correct sample shape's array
    sample_shape: PolarArray = sample_shapes[SHAPE_INDICES[odlc_guess]]
    sample_shape = np.asarray(sample_shape)
    if not verify_shape_choice(polar_array, sample_shape):
        return None
    return odlc_guess


def generate_polar_array(cnt: consts.Contour) -> PolarArray:
    """
    Generates an array storing the radii values of a normalized polar array

    Parameters
    ----------
    cnt : consts.Contour
        A contour returned by the contour detection algorithm

    Returns
    -------
    y: PolarArray
        Will return one of the ODLC shapes defined in vision/common/odlc_characteristics or None
        if the given contour is not an ODLC shape (doesnt match any ODLC)
    """
    x_avg: float
    y_avg: float
    x_avg, y_avg = np.mean(cnt, axis=0)[0]
    cnt[:, 0, 0] -= int(x_avg)
    cnt[:, 0, 1] -= int(y_avg)

    # Converts array of rectangular coordinates (x,y) to polar (angle, radius)
    pol_cnt: NDArray[Shape["*, 2"], Float64] = cartesian_array_to_polar(cnt)
    polar_sorted_indices = np.argsort(pol_cnt[:, 1])
    pol_cnt_sorted = pol_cnt[polar_sorted_indices]
    radius_array: NDArray[Shape["*"], Float64]
    _angle_array: NDArray[Shape["*"], Float64]
    radius_array, _angle_array = condense_polar(pol_cnt_sorted)

    return radius_array


def condense_polar(
    polar_array: NDArray[Shape["*, 2"], Float64]
) -> NDArray[Shape["128,2"], Float64]:
    """
    Condenses a polar array to have 'NUM_STEPS' data points for analysis

    Parameters
    ----------
    polar_array : NDArray[Shape["*, 2"], Float64]
        An array of polar points of unknown length

    Returns
    -------
    new_angle, new_radius : PolarArray, PolarArray

    """
    # Remove dupes
    polar_array = polar_array[np.unique(polar_array[:, 1], return_index=True)[1]]

    # Converting data to a form able to be passed into scipy.interp1d
    angle: NDArray[Shape["*"]] = np.empty(len(polar_array))
    radius: NDArray[Shape["*"]] = np.empty(len(polar_array))
    for i in range(len(polar_array)):
        angle[i] = polar_array[i][1]
        radius[i] = polar_array[i][0]

    # Linear interpolation to normalize all shapes to have the same number of data points
    # Create the scipy interpolation model and initializes the x-values to be uniformly spaced
    new_angle: PolarArray = np.linspace(-np.pi, np.pi, num=NUM_STEPS, endpoint=True)
    # Runs the interpolation model on the x values to generate
    # the cooresponding y-values to fit to the original data
    new_radius: PolarArray = scipy.interpolate.interp1d(
        angle, radius, kind="linear", fill_value="extrapolate"
    )(new_angle)

    return new_radius, new_angle


def cartesian_to_polar(x: float, y: float) -> tuple[float, float]:
    """
    Converts a rectangular (cartesian) coordinate to polar

    Parameters
    ----------
    x, y : float, float
        the x and y value of a point in rectangular (cartesian) coordinates

    Returns
    -------
    (rho, phi) : (float, float)
        Returns a tuple of the radius and angle of the
        cartesian point converted to polar coordinates
    """
    rho: float = np.sqrt(x**2 + y**2)
    phi: float = np.arctan2(y, x)
    polar_point: Tuple[float, float] = (rho, phi)
    return polar_point


def cartesian_array_to_polar(
    cartesian_array: NDArray[Shape["*,2,2"], Float64]
) -> NDArray[Shape["*,2"], Float64]:
    """
    Converts an array of rectangular (cartesian) coordinates to an array of polar coordinates

    Parameters
    ----------
    arr : List[float]
        An array of rectangular (cartesian) coordinates

    Returns
    -------
    shape : chars.ODLCShape | None
        Returns an array of polar coordinates
    """
    cartesian_array_x: NDArray[Shape["*, 2"], Float64] = cartesian_array[:, 0, 1]
    cartesian_array_y: NDArray[Shape["*, 2"], Float64] = cartesian_array[:, 0, 0]
    rho_array: NDArray[Shape["*, 2"], Float64] = np.hypot(cartesian_array_x, cartesian_array_y)
    phi_array: NDArray[Shape["*, 2"], Float64] = np.arctan2(cartesian_array_y, cartesian_array_x)
    polar_array: NDArray[Shape["2, *"], Float64] = np.stack((rho_array, phi_array), axis=1)
    return polar_array


def verify_shape_choice(
    mystery_radii_list: PolarArray,
    sample_odlc_radii: PolarArray,
) -> bool:
    """
    Verifies that an ODLC's Polar graph is adequately similar to the "guessed" ODLC's sample graph

    Parameters
    ----------
    mystery_radii_list : PolarArray
        The list of radii of the ODLC shape we are trying to classify
    sample_ODLC_radii : PolarArray
        The sample list of radii for the guessed ODLC shape

    Returns
    -------
    shape : bool
        Returns true if the absolute difference of the two radii lists is small enough, false if not
    """
    difference: float = np.sum(np.abs(mystery_radii_list - sample_odlc_radii))
    return difference < NUM_STEPS * MAX_ABS_ERROR
