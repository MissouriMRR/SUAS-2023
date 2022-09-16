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

    print('Waypoints Loaded:')
    for i in dataFile['waypoints']:
        latitude = i['latitude']
        longitude = i['longitude']
        altitude = i['altitude']
        print(f'Latitude: {latitude} Longitude: {longitude} @ Altitude {altitude}')

        waypoint = Waypoint(i['latitude'], i['longitude'], i['altitude'])
        waypoints.append(waypoint)
    
    print('Boundary Points Loaded:')
    for i in dataFile['flyzones']['boundaryPoints']:
        latitude = i['latitude']
        longitude = i['longitude']
        print(f'Latitude: {latitude} Longitude: {longitude}')

        boundaryPoint = BoundaryPoint(i['latitude'], i['longitude'])
        boundaryPoints.append(boundaryPoint)

    altitudeMin = dataFile['flyzones']['altitudeMin']
    altitudeMax = dataFile['flyzones']['altitudeMax']

    print(f'{altitudeMin} {altitudeMax}')
    return {'waypoints': waypoints, 'boundaryPoints': boundaryPoints, 'altitudeMin': altitudeMin, 'altitudeMax': altitudeMax}

    

    

