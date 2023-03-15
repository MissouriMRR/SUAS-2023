import numpy as np
from vision.common.bounding_box import BoundingBox, ObjectType
from nptyping import NDArray, Shape, Float64


import geopy.distance

from typing import TypeAlias

ODLC_Dict: TypeAlias = dict[int, dict[str, float]]


# Placeholder distance function
def get_distance(coords_1, coords_2):
    return geopy.distance.geodesic(coords_1, coords_2).feet


def evaluate_humanoids(humanoids: list[BoundingBox], odlcs: ODLC_Dict):
    """
    Evaluates all of the potential emergent objects to pick the most likely candidate.
    The metrics that are used in the evaluation are:

    Distance to ODLC Standard Object: 50% of final score
        The judges are more likely to be close to the ODLC Standard Object. Thus, candidates
        that are farther away will be favored.

    Distance to Emergent Object (in a DIFFERENT image): 25% of final score
        This will be smaller for the emergent object - because we have detected it in the same
        place twice. Judges will be walking around a lot more and will be detected in different
        places at different times.

    Bounding Box Area: 20% of final score:
        The Emergent Object will be placed on the ground and (presumably) not standing up. This means
        that the area of its bounding box should, in general, be larger than that of the judges.

    AI Confidence Level: 5% of final score:
        Higher confidence levels should be favored
    """
    # Weights for each metric
    category_weights: NDArray[Shape[4], Float64] = np.array([0.5, 0.25, 0.2, 0.05])

    evaluations_list: list[tuple[float, float, float, float]] = []

    subject_humanoid: BoundingBox
    for subject_humanoid in humanoids:
        # Get the distance to the closest standard object

        min_odlc_distance: float = float("inf")
        odlc: dict[str, float]
        for odlc in odlcs.values():
            distance: float = get_distance(
                (odlc["latitude"], odlc["longitude"]),
                (subject_humanoid.attributes["latitude"], subject_humanoid.attributes["longitude"]),
            )

            min_odlc_distance = min(distance, min_odlc_distance)

        # Invert the odlc distance so that the maximum value will be a low negative value
        min_odlc_distance *= -1

        # Get the distance to the closest emergent object that's not in the same image
        #   In theory, this will be close to zero for the emergent object - because we have detected
        #   it in the same place twice.
        min_humanoid_distance: float = float("inf")
        for humanoid in humanoids:
            if subject_humanoid.attributes["image_path"] != humanoid.attributes["image_path"]:
                distance: float = get_distance(
                    (humanoid.attributes["latitude"], humanoid.attributes["longitude"]),
                    (
                        subject_humanoid.attributes["latitude"],
                        subject_humanoid.attributes["longitude"],
                    ),
                )

                min_humanoid_distance = min(distance, min_humanoid_distance)

        # invert the humanoid distance to prioritize closest humanoids
        min_humanoid_distance *= -1

        evaluation: tuple[float, float, float, float] = (
            min_odlc_distance,
            min_humanoid_distance,
            humanoid.attributes["bounding_box_area"],
            humanoid.attributes["confidence"],
        )

        evaluations_list.append(evaluation)

    evaluation_array: NDArray[Shape["*, 4"], Float64] = np.array(evaluations_list)
    print(evaluation_array)
    print()

    # Get the minimums of each category
    evaluation_mins: NDArray[Shape["4"], Float64] = np.amin(evaluation_array, axis=0)

    # Repeat the array to match the shape of the original for arithmetic operations
    # evaluation_mins = np.expand_dims(evaluation_mins, axis=0)
    # evaluation_mins = np.repeat(evaluation_mins, evaluation_array.shape[0], axis=0)

    print(evaluation_mins)
    print()

    # Get the maximums of each category
    evaluation_maxes: NDArray[Shape["4"], Float64] = np.amax(evaluation_array, axis=0)

    # Repeat the array to match the shape of the original for arithmetic operations
    # evaluation_maxes = np.expand_dims(evaluation_maxes, axis=0)
    # evaluation_maxes = np.repeat(evaluation_maxes, evaluation_array.shape[0], axis=0)

    print(evaluation_maxes)
    print()

    # normalized_evaluations = (evaluation_array - evaluation_mins) / (evaluation_maxes - evaluation_mins)
    normalized_evaluations = np.dstack((evaluation_array[:, 0]))

    # print(normalized_evaluations)


if __name__ == "__main__":

    def make_test_bounding(vertices, attributes):
        # This function is only for testing purposes! Delete when not needed!
        result = BoundingBox(vertices=vertices, obj_type=ObjectType.EMG_OBJECT)
        result.attributes = attributes

        return result

    odlcs = {
        0: {"latitude": 52.10025, "longitude": 20.21222},
        3: {"latitude": 52.80085, "longitude": 21.91021},
    }

    saved_humanoids: list[BoundingBox] = []

    saved_humanoids.append(
        make_test_bounding(
            (0, 0, 0, 0),
            {
                "confidence": 0.5,
                "bounding_box_area": 2,
                "latitude": 52.2296756,
                "longitude": 21.0122287,
                "image_path": "image21.jpg",
            },
        )
    )

    saved_humanoids.append(
        make_test_bounding(
            (0, 0, 0, 0),
            {
                "confidence": 0.3,
                "bounding_box_area": 1,
                "latitude": 52.406374,
                "longitude": 16.9251681,
                "image_path": "image1.jpg",
            },
        )
    )

    evaluate_humanoids(saved_humanoids, odlcs)
