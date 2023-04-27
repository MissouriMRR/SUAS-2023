**Waypoint Subdirectory**

Contains the file responsible for moving the drone to waypoints.

Parameters include: drone, latitude, longitude, altitude (in feet), and fast_parameter.
fast parameter explanation: (1 = normal speed, anything lower makes it check the precise waypoint location faster, Example: 0.83).

Also contains functionality for converting feet into meters using a conversion of (altitude * 0.3048)

Process: Checks the value of fast_parameter and changes the rounding of waypoint coordinates to make the drone more or less precise when it decides how close it should fly to a waypoint. When waypoint is reached, the drone will hover in place for a set amount of time until it leaves for the next waypoint in its list.
