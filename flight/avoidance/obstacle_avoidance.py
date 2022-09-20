from mavsdk import System


def calculate_avoidance_path(drone: System, obstacle: dict) -> list[dict]:
    """
    Given a drone and an obstacle, calculates a path avoiding the obstacle

    Parameters
    ----------
    drone : System
        The drone for which the path will be calculated for
    obstacle : dict
        The obstacle to avoid

    Returns
    -------
    avoidance_path : list[dict]
        The avoidance path, consisting of a list of waypoints
    """

    raise NotImplementedError
