# Flight

This is the repository that holds the flight movement code. The code here allows the drone to complete all of its required functions during competition flight. Every function for connection and takeoff, to return and landing and everything else inbetween is here.

Config contains the parameters the drone will abide by for the entire duration of the flight, such as takeoff altitude, max flight altitude, and waypoint wait time.

Extract GPS contains the function for extracting the waypoint coordinates from a JSON file into a single dict for the SUAS competition.

Flight contains the functions necessary for initializing the drone's flight and monitoring the statuses of the drone.

State Settings contains the class that is responsible for setting the state of the drone during each phase of the flight. It also returns the current state of the drone each time it switches to a new phase.
