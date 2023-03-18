"""Picks the most likely emergent object out of the pool of candidates"""

from nptyping import NDArray, Shape, Float64

import numpy as np
import geopy.distance

from vision.common.bounding_box import BoundingBox, ObjectType, Vertices

from vision.common.constants import Location, ODLC_Dict


def pick_emergent_object(humanoids: list[BoundingBox], odlcs: ODLC_Dict) -> BoundingBox:
    """
    Evaluates all of the potential emergent objects to pick the most likely candidate.
    The metrics that are used in the evaluation are, in order:

    Distance to ODLC Standard Object: 50% of final score
        The judges are more likely to be close to the ODLC Standard Object. Thus, candidates
        that are farther away will be favored.

    Distance to Emergent Object (in a DIFFERENT image): 25% of final score
        This will be smaller for the emergent object - because we have detected it in the
        same place twice. Judges will be walking around a lot more and will be detected in
        different places at different times.

    Bounding Box Area: 20% of final score:
        The Emergent Object will be placed on the ground and (presumably) not standing up.
        This means that the area of its bounding box should, in general, be larger than
        that of the judges.

    AI Confidence Level: 5% of final score:
        Higher confidence levels should be favored

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
        The candidate that has scored the highest, and so is probably the actual emergent
        object
    """

    # Weights for each metric
    category_weights: NDArray[Shape[4], Float64] = np.array([0.5, 0.25, 0.20, 0.05])

    evaluations_list: list[tuple[float, float, float, float]] = []

    subject_humanoid: BoundingBox
    for subject_humanoid in humanoids:
        # Get the distance to the closest standard object
        min_odlc_distance: float = float("inf")
        odlc: Location
        for odlc in odlcs.values():
            odlc_distance: float = geopy.distance.geodesic(
                (odlc["latitude"], odlc["longitude"]),
                (subject_humanoid.attributes["latitude"], subject_humanoid.attributes["longitude"]),
            ).feet

            min_odlc_distance = min(odlc_distance, min_odlc_distance)

        # Get the distance to the closest emergent object that's not in the same image
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

                min_humanoid_distance = min(humanoid_distance, min_humanoid_distance)

        # invert the humanoid distance to prioritize closest humanoids
        min_humanoid_distance *= -1

        evaluation: tuple[float, float, float, float] = (
            min_odlc_distance,
            min_humanoid_distance,
            subject_humanoid.attributes["bounding_box_area"],
            subject_humanoid.attributes["confidence"],
        )

        evaluations_list.append(evaluation)

    evaluation_array: NDArray[Shape["*, 4"], Float64] = np.array(evaluations_list)

    # Get the minimums of each category
    evaluation_mins: NDArray[Shape["4"], Float64] = np.amin(evaluation_array, axis=0)

    # Get the maximums of each category
    evaluation_maxes: NDArray[Shape["4"], Float64] = np.amax(evaluation_array, axis=0)

    # An error here could mean that all candidates were detected in the same image - This
    #   is okay to ignore
    with np.errstate(invalid="ignore"):
        ranges: NDArray[Shape["4"], Float64] = evaluation_maxes - evaluation_mins

    # Suppress warnings when getting 0/0 errors - This is okay because that means that
    #   all candidates scored the same in that category
    with np.errstate(invalid="ignore"):
        normalized_evaluations: NDArray[Shape["*, 4"], Float64] = (
            evaluation_array - evaluation_mins
        ) / ranges

    weighted_evaluations: NDArray[Shape["*, 4"], Float64] = (
        normalized_evaluations * category_weights
    )

    # Use nansum to ignore categories with divide by zero errors
    scores: NDArray[Shape["*"], Float64] = np.nansum(weighted_evaluations, axis=1)

    return humanoids[np.argmax(scores)]


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

    pick_emergent_object(saved_humanoids, saved_odlcs)
