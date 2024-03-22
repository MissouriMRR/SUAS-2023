"""Implement the behavior of the Waypoint state."""

# pylint: disable=too-many-locals

import asyncio
import logging
from typing import Final

import mavsdk.telemetry
import utm

from mavsdk.action import ActionError

from flight.extract_gps import extract_gps, GPSData
from flight.extract_gps import (
    WaypointUtm as WaylistUtm,
    BoundaryPointUtm as BoundarylistUtm,
)

from flight.waypoint.geometry import LineSegment, Point
from flight.waypoint.goto import move_to
from flight.waypoint.graph import GraphNode
from flight.waypoint import pathfinding

from state_machine.states.airdrop import Airdrop
from state_machine.states.odlc import ODLC
from state_machine.states.state import State
from state_machine.states.waypoint import Waypoint
from state_machine.state_tracker import update_state

BOUNDARY_SHRINKAGE: Final[float] = 5.0  # in meters


async def run(self: Waypoint) -> State:
    """
    Run method implementation for the Waypoint state.

    This method instructs the drone to navigate to a specified waypoint and
    transitions to the Airdrop or ODLC State.

    Returns
    -------
    Airdrop : State
        The next state after successfully reaching the specified waypoint and
        initiating the Airdrop process.
    ODLC : State
        The next state after successfully reaching the specified waypoint and
        initiating the ODLC process.

    Notes
    -----
    This method is responsible for guiding the drone to a predefined waypoint in its flight path.
    Upon reaching the waypoint, it transitions the drone to the Land state to initiate landing.

    """

    try:
        update_state("Waypoint")
        logging.info("Waypoint state running")

        gps_dict: GPSData = extract_gps(self.flight_settings.path_data_path)
        waypoints_utm: list[WaylistUtm] = gps_dict["waypoints_utm"]

        boundary_points: list[BoundarylistUtm] = gps_dict["boundary_points_utm"]
        boundary_points.pop()  # The last point is a duplicate of the first

        boundary_vertices: list[Point] = []
        for point in boundary_points:
            boundary_vertices.append(Point(point.easting, point.northing))

        search_graph: list[GraphNode[Point, float]] = pathfinding.create_pathfinding_graph(
            boundary_vertices, BOUNDARY_SHRINKAGE
        )

        for waypoint_num, waypoint in enumerate(waypoints_utm):
            drone_position: mavsdk.telemetry.Position = await anext(
                self.drone.system.telemetry.position()
            )
            drone_northing, drone_easting, _, _ = utm.from_latlon(
                drone_position.latitude_deg,
                drone_position.longitude_deg,
                boundary_points[0].zone_number,
                boundary_points[0].zone_letter,
            )

            goto_points: list[Point]
            try:
                goto_points = list(
                    pathfinding.shortest_path_between(
                        Point(drone_easting, drone_northing),
                        Point(waypoint.easting, waypoint.northing),
                        search_graph,
                    )
                )
            except RuntimeError:
                # Unable to find path that doesn't intersect boundary
                # This should never happen
                goto_points = [Point(waypoint.easting, waypoint.northing)]

            path_length: float = (
                sum(
                    line_segment.length()
                    for line_segment in LineSegment.from_points(goto_points, False)
                )
                + (goto_points[0] - Point(drone_easting, drone_northing)).distance_from_origin()
            )

            curr_altitude: float = drone_position.relative_altitude_m
            altitude_slope: float = (waypoint.altitude - curr_altitude) / path_length

            goto_points.pop()  # The last point is just the waypoint

            lat_deg: float
            lon_deg: float
            lat_deg, lon_deg = utm.to_latlon(
                waypoint.easting, waypoint.northing, waypoint.zone_number, waypoint.zone_letter
            )

            logging.info("Moving to waypoint %d (lat=%f, lon=%f)", waypoint_num, lat_deg, lon_deg)

            for line_segment in LineSegment.from_points(goto_points, False):
                lat_deg, lon_deg = utm.to_latlon(
                    line_segment.p_2.x,
                    line_segment.p_2.y,
                    boundary_points[0].zone_number,
                    boundary_points[0].zone_letter,
                )

                # Gradually move toward goal altitude
                curr_altitude += altitude_slope * line_segment.length()

                try:
                    await move_to(self.drone.system, lat_deg, lon_deg, curr_altitude, 0.83)
                except ActionError:
                    logging.warning(ActionError)

            # use 0.9 for fast_param to get within 25 ft of waypoint with plenty of leeway
            # while being fast (values above 5/6 and less than 1 check for lat and lon with
            # 5 digit of precision, or about 1.11 m)
            await move_to(self.drone.system, lat_deg, lon_deg, waypoint.altitude, 0.9)

            logging.info("Reached waypoint %d", waypoint_num)

        return (ODLC if self.drone.odlc_scan else Airdrop)(self.drone, self.flight_settings)

    except asyncio.CancelledError as ex:
        logging.error("Waypoint state canceled")
        raise ex
    finally:
        pass


# Set the run_callable attribute of the Waypoint class to the run function
Waypoint.run_callable = run
