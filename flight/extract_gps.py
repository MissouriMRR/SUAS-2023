from collections import namedtuple
import json

def extract_gps():
    with open("flight/waypoint_data.json") as waypoint_data:
        dataFile = json.load(waypoint_data)

    waypoints = []
    boundaryPoints = []

    Waypoint = namedtuple('Waypoint', ['latitude', 'longitude', 'altitude'])
    BoundaryPoint = namedtuple('BoundaryPoint', ['latitude', 'longitude'])

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
    return waypoints, boundaryPoints, altitudeMin, altitudeMax

extract_gps()
    

    

