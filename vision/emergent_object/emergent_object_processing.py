"""Picks the most likely emergent object out of the pool of candidates"""

from nptyping import NDArray, Shape, Float64

import numpy as np
import geopy.distance

from vision.common.bounding_box import BoundingBox, ObjectType, Vertices

from vision.common.constants import Location, ODLC_Dict


# Weights for each metric in pick_emergent_object()
# is [standard_object_dist, emergent_object_dist, bounding_box_area, ai_confidence]
# see pick_emergent_object() notes
CATEGORY_WEIGHTS: NDArray[Shape[4], Float64] = np.array([0.5, 0.25, 0.20, 0.05])


def pick_emergent_object(humanoids: list[BoundingBox], odlcs: ODLC_Dict) -> BoundingBox:
    """
    Evaluates all of the potential emergent objects to pick the most likely candidate.

    Parameters
    ----------
    humanoids: list[BoundingBox]
        A list of all candidate emergent objects. Required attributes:
            latitude, longitude, bounding_box_area, image_path, confidence
    odlcs: ODLC_Dict
        A dictionary containing the locations of all discovered ODLCs

    Returns
    -------
    emergent_object: BoundingBox
        The most likely candidate for the emergent object.

    Notes
    -----
    The metrics that are used in the evaluation are, in order:

    Distance to ODLC Standard Object:
        The judges are more likely to be close to the ODLC Standard Object. Thus, candidates
        that are farther away will be favored.

    Distance to Emergent Object (in a DIFFERENT image):
        This will be smaller for the emergent object - because we have detected it in the
        same place twice. Judges will be walking around a lot more and will be detected in
        different places at different times.

    Bounding Box Area:
        The Emergent Object will be placed on the ground and (presumably) not standing up.
        This means that the area of its bounding box should, in general, be larger than
        that of the judges.

    AI Confidence Level:
        Higher confidence levels should be favored
    """
    evaluations_list: list[tuple[float, float, float, float]] = []

    subject_humanoid: BoundingBox
    for subject_humanoid in humanoids:
        # Get the distance to the closest standard object
        min_odlc_distance: float = calc_std_odlc_min_dist(subject_humanoid, odlcs)

        # Get the distance to the closest emergent object that's not in the same image
        min_humanoid_distance: float = calc_emerg_obj_min_dist(humanoids, subject_humanoid)

        evaluation: tuple[float, float, float, float] = (
            min_odlc_distance,
            min_humanoid_distance,
            subject_humanoid.attributes["bounding_box_area"],
            subject_humanoid.attributes["confidence"],
        )

        evaluations_list.append(evaluation)

    evaluation_array: NDArray[Shape["*, 4"], Float64] = np.array(evaluations_list)

    return humanoids[emergent_obj_selection(evaluation_array)]


def calc_std_odlc_min_dist(humanoid: BoundingBox, odlcs: ODLC_Dict) -> float:
    """
    Calculates the distance from the given humanoid to the closest standard odlc object.

    Parameters
    ----------
    humanoid : BoundingBox
        A candidate emergent object. Required attributes:
            latitude, longitude, bounding_box_area, image_path, confidence
    odlcs: ODLC_Dict
        A dictionary containing the locations of all discovered ODLCs

    Returns
    -------
    min_odlc_distance : float
        The distance of the closest standard object to the candidate emergent object.
    """
    min_odlc_distance: float = float("inf")
    odlc: Location
    for odlc in odlcs.values():
        odlc_distance: float = geopy.distance.geodesic(
            (odlc["latitude"], odlc["longitude"]),
            (humanoid.attributes["latitude"], humanoid.attributes["longitude"]),
        ).feet

        if odlc_distance < min_odlc_distance:
            min_odlc_distance = odlc_distance

    return min_odlc_distance


def calc_emerg_obj_min_dist(humanoids: list[BoundingBox], subject_humanoid: BoundingBox) -> float:
    """
    Calculates the distance from the given humanoid to the closest humanoid from a different image

    Parameters
    ----------
    humanoids : list[BoundingBox]
        A list of all candidate emergent objects. Required attributes:
            latitude, longitude, bounding_box_area, image_path, confidence
    subject_humanoid : BoundingBox
        A candidate emergent object.

    Returns
    -------
    min_humanoid_distance : float
    """
    min_humanoid_distance: float = float("inf")
    humanoid: BoundingBox
    for humanoid in humanoids:
        # Don't check candidates that are in the same image
        if subject_humanoid.attributes["image_path"] != humanoid.attributes["image_path"]:
            humanoid_distance: float = geopy.distance.geodesic(
                (humanoid.attributes["latitude"], humanoid.attributes["longitude"]),
                (
                    subject_humanoid.attributes["latitude"],
                    subject_humanoid.attributes["longitude"],
                ),
            ).feet

            if humanoid_distance < min_humanoid_distance:
                min_humanoid_distance = humanoid_distance

    # invert the humanoid distance to prioritize closest humanoids
    min_humanoid_distance *= -1

    return min_humanoid_distance


def emergent_obj_selection(evaluation_array: NDArray[Shape["*, 4"], Float64]) -> int:
    """
    Performs operations on evaluation array and selects the best scoring emergent object.

    Parameters
    ----------
    evaluation_array : NDArray[Shape["*, 4"], Float64]
        The evaluations of all of the emergent objects
        (standard_object_dist, emergent_object_dist, bounding_box_area, ai_confidence)

    Returns
    -------
    top_score : int
        The index of the emergent object with the highest score.
    """
    # Get the minimums of each category
    evaluation_mins: NDArray[Shape["4"], Float64] = np.amin(evaluation_array, axis=0)

    # Get the maximums of each category
    evaluation_maxes: NDArray[Shape["4"], Float64] = np.amax(evaluation_array, axis=0)

    # Suppress warnings when min_humanoid_distance is infinity, resulting in NaN value warnings
    with np.errstate(invalid="ignore"):
        ranges: NDArray[Shape["4"], Float64] = evaluation_maxes - evaluation_mins

    # Suppress warnings when getting 0/0 - This is okay because that means that
    #   all candidates scored the same in that category
    with np.errstate(invalid="ignore"):
        normalized_evaluations: NDArray[Shape["*, 4"], Float64] = (
            evaluation_array - evaluation_mins
        ) / ranges

    # NaN values are unimportant at this step
    weighted_evaluations: NDArray[Shape["*, 4"], Float64] = (
        normalized_evaluations * CATEGORY_WEIGHTS
    )

    # Use nansum to ignore NaN values in final calculation because they can be treated as 0s
    scores: NDArray[Shape["*"], Float64] = np.nansum(weighted_evaluations, axis=1)

    return int(np.argmax(scores))


if __name__ == "__main__":
    saved_odlcs: ODLC_Dict = {
        0: {"latitude": 52.10025, "longitude": 20.21222},
        3: {"latitude": 52.80085, "longitude": 21.91021},
    }

    saved_humanoids: list[BoundingBox] = []

    empty_vertices: Vertices = (
        (0, 0),
        (0, 0),
        (0, 0),
        (0, 0),
    )

    emergent_1: BoundingBox = BoundingBox(vertices=empty_vertices, obj_type=ObjectType.EMG_OBJECT)
    emergent_1.attributes = {
        "confidence": 0.5,
        "bounding_box_area": 2,
        "latitude": 52.2296756,
        "longitude": 21.0122287,
        "image_path": "image2.jpg",
    }
    saved_humanoids.append(emergent_1)

    emergent_2: BoundingBox = BoundingBox(vertices=empty_vertices, obj_type=ObjectType.EMG_OBJECT)
    emergent_2.attributes = {
        "confidence": 0.3,
        "bounding_box_area": 1,
        "latitude": 52.406374,
        "longitude": 16.9251681,
        "image_path": "image1.jpg",
    }
    saved_humanoids.append(emergent_2)

    print(pick_emergent_object(saved_humanoids, saved_odlcs))
