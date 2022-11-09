"""Functions for calculating locations of objects in an image"""

import numpy as np
from constants import Point

import coordinate_lengths
import vector_utils


def get_coordinates(
    pixel: tuple[int, int],
    image_shape: tuple[int, int, int],
    focal_length: float,
    rotation_deg: list[float],
    drone_coordinates: list[float],
    altitude_m: float,
) -> tuple[float, float] | None:
    """
    Calculates the coordinates of the given pixel.
    Returns None if there is no valid intersect.

    Parameters
    ----------
    pixel: tuple[int, int]
        The coordinates of the pixel in [Y, X] form
    image_shape : tuple[int, int, int]
        The shape of the image (returned by `image.shape` when image is a numpy image array)
    focal_length : float
        The camera's focal length
    rotation_deg: list[float]
        The rotation of the drone/camera. The ROTATION_OFFSET in vector_utils.py will be applied
        after.
    drone_coordinates: list[float]
        The coordinates of the drone in degrees of (latitude, longitude)
    altitude_m: float
        The altitude of the drone in meters

    Returns
    -------
    pixel_coordinates : tuple[float, float] | None
        The (latitude, longitude) coordinates of the pixel in degrees.

        Equal to None if there is no valid intersect.
    """
    # Calculate the latitude and longitude lengths (in meters)
    latitude_length: float = coordinate_lengths.latitude_length(drone_coordinates[0])
    longitude_length: float = coordinate_lengths.longitude_length(drone_coordinates[0])

    # Find the pixel's intersect with the ground to get the location relative to the drone
    intersect: Point | None = vector_utils.pixel_intersect(
        pixel, image_shape, focal_length, rotation_deg, altitude_m
    )

    if intersect is None:
        return None

    # Invert the X axis so that the longitude is correct
    intersect[1] *= -1

    # Convert the location to latitude and longitude and add it to the drone's coordinates
    pixel_lat = drone_coordinates[0] + intersect[0] / latitude_length
    pixel_lon = drone_coordinates[1] + intersect[1] / longitude_length

    return pixel_lat, pixel_lon


def calculate_distance(
    pixel1: tuple[int, int],
    pixel2: tuple[int, int],
    image_shape: tuple[int, int, int],
    focal_length: float,
    rotation_deg: list[float],
    altitude: float,
) -> float | None:
    """
    Calculates the physical distance between two points on the ground represented by pixel
    locations. Units of `distance` are the same as the units of `altitude`

    Parameters
    ----------
    pixel1, pixel2: tuple[int, int]
        The two input pixel locations in [Y,X] form. The distance between them will be calculated
    image_shape : tuple[int, int, int]
        The shape of the image (returned by `image.shape` when image is a numpy image array)
    focal_length : float
        The camera's focal length
    rotation_deg : list[float]
        The [roll, pitch, yaw] rotation in degrees
    altitude: float
        The altitude of the drone in any units. If an altitude is given, the units of the output
        will be the units of the input.

    Returns
    -------
    distance : float | None
        The distance between the two pixels. Units are the same units as `altitude`

        Returns None if one or both of the points did not have an intersection
    """
    intersect1: Point | None = vector_utils.pixel_intersect(
        pixel1, image_shape, focal_length, rotation_deg, altitude
    )
    intersect2: Point | None = vector_utils.pixel_intersect(
        pixel2, image_shape, focal_length, rotation_deg, altitude
    )

    # Checks if the intersects were valid
    if intersect1 is None or intersect2 is None:
        return None

    # Calculate the distance between the two intersects
    distance: float = float(np.linalg.norm(intersect1 - intersect2))

    return distance
