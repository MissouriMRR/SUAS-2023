import plotter
import point_finder


flyZones = [
    {
        "altitudeMin": 75.0,
        "altitudeMax": 400.0,
        "boundaryPoints": [
            {"latitude": 38.31442311312976, "longitude": -76.54522971451763},
            {"latitude": 38.31421041772561, "longitude": -76.54400246436776},
            {"latitude": 38.3144070396263, "longitude": -76.54394394383165},
            {"latitude": 38.31461622313521,"longitude": -76.54516993186949},
            {"latitude": 38.31442311312976, "longitude": -76.54522971451763},
        ],
    }
][0]

obstacles = [
    {
        "latitude": 37.94922429469271,
        "longitude": -91.7825514554602,
        "radius": 0,
        "height": 0,
    },
]

odlc = {"latitude": 37.94873549190636, "longitude": -91.78086677968352}

if __name__ == "__main__":
    boundary_points = flyZones["boundaryPoints"]

    # Add utm coordinates to all
    boundary_points = point_finder.all_latlon_to_utm(boundary_points)
    obstacles = point_finder.all_latlon_to_utm(obstacles)
    odlc = point_finder.latlon_to_utm(odlc)

    # Find the closest point
    (closest_point, shrunk_boundary) = point_finder.find_closest_point(
        odlc, boundary_points, obstacles
    )

    # Plot data
    plotter.plot_data(odlc, closest_point, boundary_points, shrunk_boundary, obstacles)