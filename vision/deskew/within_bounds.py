"""
Functions for determining if any part of one shape is within another
shape
"""

from nptyping import NDArray, Shape, Float32

import numpy as np
import cv2


def on_line(point1: list[float], point2: list[float], 
            point3: list[float]) -> bool:
    """
    Takes three points and returns True if point2 is on the line
    segment created by point1 and point3. Returns False otherwise.

    Parameters
    ----------
    point1: [float]
        The first point on the line segment.
        An Array that contains the x and y coordinates of the point.
    point2: [float]
        A point that may or may not lie on the line segment that is
        created by point1 and point3.
        An Array that contains the x and y coordinates of the point.
    point3: [float]
        The end point on the line segment.
        An Array that contains the x and y coordinates of the point.

    Returns
    -------
    to_return: bool
        Returns True if point2 lies on the line segment created by
        point1 and point2. Returns False otherwise.
    
    References
    ----------
    https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """

    to_return: bool = False

    if (((point2[0] <= max(point1[0], point3[0])) and 
         (point2[0] >= min(point1[0], point3[0]))) and 
        ((point2[1] <= max(point1[1], point3[1])) and 
         (point2[1] >= min(point1[1], point3[1])))):
        to_return = True
    
    return to_return


def find_orientation(point1: list[float], point2: list[float], 
                     point3: list[float]) -> int:
    """
    Finds the orientation of the three points. Returns int representing
    the orientation.

    Parameters
    ----------
    point1: [float]
        The first point of a shape or possibly line.
        An Array that contains the x and y coordinates of the point.
    point2: [float]
        The second point of a shape or possibly line.
        An Array that contains the x and y coordinates of the point.
    point3: [float]
        The third point of a shape or possibly line.
        An Array that contains the x and y coordinates of the point.

    Returns
    -------
    to_return: int
        Returns an integer value which represents the orientation of
        point1, point2, and point3.
        0 -> Colinear
        1 -> Clockwise
        2 -> Counterclockwise
    
    References
    ----------
    https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """

    to_return: int = 0 # Defaults to_return as Colinear

    # GeeksforGeeks algorithm
    val: int = (((point2[1] - point1[1]) * (point3[0] - point2[0]))
          - ((point2[0] - point1[0]) * (point3[1] - point2[1])))

    if val > 0:
        to_return = 1 # Clockwise
    elif val < 0:
        to_return = 2 # Counterclockwise
    # If val == 0, then to_return = 0

    return to_return


def lines_intersect(line1: list[list[float]], line2: list[list[float]]) -> bool:
    """
    Returns True if line1 and line2 intersect and False otherwise.

    Parameters
    ----------
    line1: [[float]]
        The first line that may or may not intersect with line2.
        A 2D array that contains two points and each point is made up of
        x and y coordinates.
    line2: [[float]]
        The second line that may or may not intersect with line1.
        A 2D array that contains two points and each point is made up of
        x and y coordinates.
    
    Returns
    -------
    to_return: bool
        Returns True if line1 and line2 intersect and False otherwise.
    
    References
    ----------
    https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
    """

    to_return: bool = False

    # Find the 4 orientations required for the general and special cases
    o1: int = find_orientation(line1[0], line1[1], line2[0]) 
    o2: int = find_orientation(line1[0], line1[1], line2[1]) 
    o3: int = find_orientation(line2[0], line2[1], line1[0]) 
    o4: int = find_orientation(line2[0], line2[1], line1[1])

    if (o1 != o2) and (o3 != o4): # General Case
        to_return = True
    else: # Special Cases
        if (o1 == 0) and on_line(line1[0], line2[0], line1[1]):
            to_return = True
        elif (o2 == 0) and on_line(line1[0], line2[1], line1[1]):
            to_return = True
        elif (o3 == 0) and on_line(line2[0], line1[0], line2[1]):
            to_return = True
        elif (o4 == 0) and on_line(line2[0], line1[1], line2[0]):
            to_return = True

    return to_return


def inside_bounds(boundary: list[list[float]], 
                  location_point: list[float]) -> bool:
    """
    Returns True if the location_point is within the bounds of the shape
    created by boundary. Returns False otherwise.

    Parameters
    ----------
    boundary: [[float]]
        Contains a number of points which create a shape.
        A 2D array which contains a number of points where each point
        is made up of x and y coordinates.
    location_point: [float]
        A point that may or may not be located within the shape created
        by boundary.
        An Array that contains the x and y coordinates of the point.
    
    Returns
    -------
    is_in_bounds: bool
        Returns True if the location_point is within the bounds of the
        shape created by boundary. Returns False otherwise.
    """

    is_in_bounds: bool = False

    # Transforms boundary array to numpy array
    new_np_boundary: NDArray[Shape["*, *"], Float32] = np.array(boundary)
    new_np_boundary = new_np_boundary.reshape((-1, 1, 2))

    # Tests if point is within boundary
    ppt_return: float = cv2.pointPolygonTest(new_np_boundary, 
                                              (location_point[0], 
                                               location_point[1]), 
                                             False)

    # pointPolygonTest returns 1.0 if point is within bounds, and -1.0
    # if the point is not within bounds
    if ppt_return > 0:
        is_in_bounds = True

    return is_in_bounds


def contains_airdrop_boundary(image_corners: list[list[float]], 
                              airdrop_boundary: list[list[float]]) -> bool:
    """
    Returns True if any point within the airdrop_boundary is within the
    image, False otherwise.

    Parameters
    ----------
    image_corners: [[float]]
        Contains a number of points which create a shape.
        A 2D array which contains a number of points where each point
        is made up of x and y coordinates.
    airdrop_boundary : [[float]]
        Contains a number of points which create a shape.
        A 2D array which contains a number of points where each point
        is made up of x and y coordinates.
    
    Returns
    -------
    is_in_bounds: bool
        Returns True if any point within the airdrop_boundary is within
        the image, False otherwise.
    """
    is_in_bounds: bool = False

    # Checks if any corner of the airdrop boundary is within the image
    # boundary
    for point in airdrop_boundary:
        point_inside_image: bool = inside_bounds(image_corners, point)

        if point_inside_image:
            is_in_bounds = True
            break

    # If no corner of the airdrop boundary is within the image boundary
    # Will check if any lines of the airdrop boundary intersect with the
    # image boundary
    if is_in_bounds == False:
        # For every point in airdrop_boundary
        for num_point in range(len(airdrop_boundary)):
            airdrop_point1: list[float] = airdrop_boundary[num_point]
            airdrop_point2: list[float] = airdrop_boundary[(num_point + 1) 
                                                   % len(airdrop_boundary)]
            airdrop_line: list[list[float]] = [airdrop_point1, airdrop_point2]
      
            # For every point in image_corners
            for num_point in range(len(image_corners)):
                image_point1: list[float] = image_corners[num_point]
                image_point2: list[float] = image_corners[(num_point + 1)
                                                     % len(image_corners)]
                image_line: list[list[float]] = [image_point1, image_point2]

                # Checks if lines intersect
                if lines_intersect(airdrop_line, image_line):
                    is_in_bounds = True

    return is_in_bounds