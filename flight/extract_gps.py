from collections import namedtuple
from typing import List, NamedTuple, TypeAlias
import json

GPSData: TypeAlias = dict(list(NamedTuple), list(NamedTuple), int, int)

def extract_gps(path: str) -> GPSData:
    
    Waypoint = namedtuple('Waypoint', ['latitude', 'longitude', 'altitude'])
    BoundaryPoint = namedtuple('BoundaryPoint', ['latitude', 'longitude'])
    
    with open(path) as waypoint_data:
        dataFile = json.load(waypoint_data)

    waypoints = []
    boundaryPoints = []

    for i in dataFile['waypoints']:
        latitude = i['latitude']
        longitude = i['longitude']
        altitude = i['altitude']

        waypoint = Waypoint(latitude, longitude, altitude)
        waypoints.append(waypoint)
    
    print('Boundary Points Loaded:')
    for i in dataFile['flyzones']['boundaryPoints']:
        latitude = i['latitude']
        longitude = i['longitude']

        boundaryPoint = BoundaryPoint(latitude, longitude)
        boundaryPoints.append(boundaryPoint)

    altitudeMin = dataFile['flyzones']['altitudeMin']
    altitudeMax = dataFile['flyzones']['altitudeMax']

    return {'waypoints': waypoints, 'boundaryPoints': boundaryPoints, 'altitudeMin': altitudeMin, 'altitudeMax': altitudeMax}

if __name__ == "__main__":
    extract_gps('flight/waypoint_data.json')

    

    

