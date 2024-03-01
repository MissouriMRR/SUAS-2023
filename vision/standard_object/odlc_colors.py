"""
Functions relating to finding the colors of the text and shape on the standard ODLC objects.
"""

import cv2
import numpy as np

from nptyping import NDArray, Shape, UInt8, Float32, Int32, Float64

from vision.common.bounding_box import BoundingBox
from vision.common.constants import Image
from vision.common.crop import crop_image
from vision.common.odlc_characteristics import ODLCColor, COLOR_RANGES


def find_colors(image: Image, text_bounds: BoundingBox) -> tuple[ODLCColor, ODLCColor]:
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
    colors : tuple[ODLCColor, ODLCColor]
        the colors of the standard object
        shape_color : ODLCColor
            the color of the shape
        text_color : ODLCColor
            the color of the text on the object
    """
    # slice image around bounds of text
    cropped_img: Image = crop_image(image, text_bounds)

    # kmeans clustering with k=2
    kmeans_img: Image = run_kmeans(cropped_img)

    # get the 2 color values
    shape_color_val: NDArray[Shape["3"], UInt8]
    text_color_val: NDArray[Shape["3"], UInt8]
    shape_color_val, text_color_val = get_color_vals(kmeans_img)

    # match colors to closest color in ODLCColor
    shape_color: ODLCColor = parse_color(shape_color_val)
    text_color: ODLCColor = parse_color(text_color_val)

    # return the 2 colors
    return shape_color, text_color


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

    kernel: NDArray[Shape["5, 5"], UInt8] = np.ones(
        (5, 5), np.uint8
    )  # 5x5 kernal for use in dilation/erosion
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
    )  # specifies termination criteria of kmeans algorithm (maximum iterations/desired accuracy)
    k_val: int = 2  # K=2 yields 2 clusters from kmeans

    label: NDArray[Shape["*, *"], Int32]  # label array for the clusters
    center: NDArray[Shape["2, 5"], Float32]  # cluster centers
    _, label, center = cv2.kmeans(
        np.float32(vectorized), K=k_val, bestLabels=None, criteria=term_crit, attempts=10, flags=0
    )

    center_int: NDArray[Shape["2, 3"], UInt8] = center.astype(np.uint8)[:, :3]  # xy removed

    # Convert back to BGR
    kmeans_flat: NDArray[Shape["*, 3"], UInt8] = center_int[label.flatten()]
    kmeans_img: Image = kmeans_flat.reshape((dilated_img.shape))

    return kmeans_img


def get_color_vals(
    kmeans_img: Image,
) -> tuple[NDArray[Shape["3"], UInt8], NDArray[Shape["3"], UInt8]]:
    """
    Get the two unique color values in the kmeans image and determines which is the
    shape and which is the text.

    Parameters
    ----------
    kmeans_img : Image
        the cropped image of the text after kmeans has been performed

    Returns
    -------
    color_vals : tuple[NDArray[Shape["3"], UInt8], NDArray[Shape["3"], UInt8]]
        the color values of the shape and the text
        shape_color_val : NDArray[Shape["3"], UInt8]
            RGB value of the shape color
        text_color_val : NDArray[Shape["3"], UInt8]
            RGB value of the text color
    """
    # Find the two colors in the image
    color_vals: NDArray[Shape["2, 3"], UInt8] = np.unique(
        kmeans_img.reshape(-1, kmeans_img.shape[2]), axis=0
    )

    # Mask of Color 1
    color_1_r: NDArray[Shape["*, *"], UInt8] = np.where(
        kmeans_img[:, :, 0] == color_vals[0][0], 1, 0
    )
    color_1_g: NDArray[Shape["*, *"], UInt8] = np.where(
        kmeans_img[:, :, 1] == color_vals[0][1], 1, 0
    )
    color_1_b: NDArray[Shape["*, *"], UInt8] = np.where(
        kmeans_img[:, :, 2] == color_vals[0][2], 1, 0
    )

    color_1_mat: NDArray[Shape["*, *"], UInt8] = np.bitwise_and(
        color_1_r, color_1_g, color_1_b
    ).astype(np.uint8)
    color_1_adj_mat: NDArray[Shape["*, *"], UInt8] = np.where(color_1_mat == 1, 255, 128).astype(
        np.uint8
    )

    # Mask of Color 2
    color_2_mat: NDArray[Shape["*, *"], UInt8] = np.where(color_1_mat == 1, 0, 1).astype(np.uint8)

    # Set middle pixel of adj mat to 0
    dimensions: tuple[int, int] = color_1_adj_mat.shape
    center_pt: tuple[int, int] = (int(dimensions[0] / 2), int(dimensions[1] / 2))
    color_1_adj_mat[center_pt] = 0

    # calculate distance of each pixel to center pixel
    distance_mat: NDArray[Shape["*, *"], Float32] = cv2.distanceTransform(
        color_1_adj_mat, cv2.DIST_L2, 3
    )

    # average distance for each color
    dist_1: float = cv2.mean(distance_mat, color_1_mat)[0]
    dist_2: float = cv2.mean(distance_mat, color_2_mat)[0]

    # sort color values, assumes that text color value is closer to the center
    text_color_val: NDArray[Shape["3"], UInt8] = (
        color_vals[0] if min(dist_1, dist_2) == dist_1 else color_vals[1]
    )
    shape_color_val: NDArray[Shape["3"], UInt8] = (
        color_vals[0] if np.all(text_color_val == color_vals[1]) else color_vals[1]
    )

    return shape_color_val, text_color_val


def parse_color(color_val: NDArray[Shape["3"], UInt8]) -> ODLCColor:
    """
    Parse an BGR color value to determine what color it is.

    Parameters
    ----------
    color_val : NDArray[Shape["3"], UInt8]
        the BGR color value

    Returns
    -------
    color : ODLCColor
        the color that the value is closest to
    """
    # Convert color to HSV
    frame: NDArray[Shape["1, 1, 3"], UInt8] = np.reshape(
        color_val, (1, 1, 3)
    )  # store as single-pixel image
    hsv_color_val: NDArray[Shape["3"], UInt8] = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)

    # Determine which ranges color value falls in
    matched: list[ODLCColor] = []  # colors matched to the value

    col: ODLCColor
    ranges: NDArray[Shape["*, 2, 3"], UInt8]
    for col, ranges in COLOR_RANGES.items():  # for each color and its set of ranges
        col_range: NDArray[Shape["2, 3"], UInt8]
        for col_range in ranges:  # for each range of the color
            if cv2.inRange(hsv_color_val, col_range[1], col_range[0])[0, 0] == 255:
                matched.append(col)

    if len(matched) == 0:  # no matches
        return best_color_range(hsv_color_val, list(COLOR_RANGES.keys()))

    if len(matched) > 1:  # more than 1 match
        return best_color_range(hsv_color_val, matched)

    # only 1 matched color (perfection)
    return matched[0]


def best_color_range(
    color_val: NDArray[Shape["3"], UInt8], possible_colors: list[ODLCColor]
) -> ODLCColor:
    """
    Find the closest color to the value from the possible colors.

    Parameters
    ----------
    color_val : NDArray[Shape["3"], UInt8]
        the color value in HSV space
    possible_colors : list[ODLCColor]
        the possible colors to check

    Returns
    -------
    color : ODLCColor
        the closest color to the value
    """
    # find matched color with min dist to color value
    best_dist: float = float("inf")
    best_col: ODLCColor = possible_colors[0]

    col: ODLCColor
    for col in possible_colors:
        dist: float = float("inf")

        col_range: NDArray[Shape["2, 3"], UInt8]
        for col_range in COLOR_RANGES[col]:  # for each range of the color
            mid: NDArray[Shape["3"], Float64] = np.array(
                [np.mean(col_range[:, 0]), np.mean(col_range[:, 1]), np.mean(col_range[:, 2])]
            )  # midpoint of range
            dist = np.sum(np.abs(color_val - mid)).astype(float)  # dist of color to range mid

            if dist < best_dist:  # color with min distance is the color chosen
                best_dist = dist
                best_col = col

    return best_col  # return color with lowest distance


if __name__ == "__main__":
    import argparse

    from vision.common.bounding_box import ObjectType

    # parse arguments
    parser: argparse.ArgumentParser = argparse.ArgumentParser("Find ODLC colors.")

    parser.add_argument(
        "-f", "--file_name", type=str, help="Name and path to the image file. Required argument."
    )

    args: argparse.Namespace = parser.parse_args()

    if not args.file_name:
        raise RuntimeError("No image file specified.")
    file_name: str = args.file_name

    # read in the image and run algorithm
    img: Image = cv2.imread(file_name)

    # NOTE: to test an image, specify the bounds of the text in the image here
    bbox = BoundingBox(vertices=((0, 0), (10, 0), (10, 10), (0, 10)), obj_type=ObjectType.TEXT)

    # run algorithm
    print(find_colors(img, bbox))
