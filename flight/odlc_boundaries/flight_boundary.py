import plotter
import point_finder


flyZones = [
    {
        "altitudeMin": 75.0,
        "altitudeMax": 400.0,
        "boundaryPoints": [
            {"latitude": 38.31729702009844, "longitude": -76.55617670782419},
            {"latitude": 38.31594832826572, "longitude": -76.55657341657302},
            {"latitude": 38.31546739500083, "longitude": -76.55376201277696},
            {"latitude": 38.31470980862425, "longitude": -76.54936361414539},
            {"latitude": 38.31424154692598, "longitude": -76.54662761646904},
            {"latitude": 38.31369801280048, "longitude": -76.54342380058223},
            {"latitude": 38.31331079191371, "longitude": -76.54109648475954},
            {"latitude": 38.31529941346197, "longitude": -76.54052104837133},
            {"latitude": 38.31587643291039, "longitude": -76.54361305817427},
            {"latitude": 38.31861642463319, "longitude": -76.54538594175376},
            {"latitude": 38.31862683616554, "longitude": -76.55206138505936},
            {"latitude": 38.31703471119464, "longitude": -76.55244787859773},
            {"latitude": 38.31674255749409, "longitude": -76.55294546866578},
            {"latitude": 38.31729702009844, "longitude": -76.55617670782419},
        ],
    }
][0]

odlc = {"latitude": 37.94873549190636, "longitude": -91.78086677968352}

if __name__ == "__main__":
    boundary_points = flyZones["boundaryPoints"]

    # Add utm coordinates to all
    boundary_points = point_finder.all_latlon_to_utm(boundary_points)
    odlc = point_finder.latlon_to_utm(odlc)

    # Find the closest point
    (closest_point, shrunk_boundary) = point_finder.find_closest_point(
        odlc, boundary_points, 
    )

    # Plot data
    plotter.plot_data(odlc, closest_point, boundary_points, shrunk_boundary)