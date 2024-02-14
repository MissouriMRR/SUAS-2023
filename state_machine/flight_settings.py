"""Class to contain setters, getters & parameters for current flight"""

from typing import Final

DEFAULT_WAYPOINTS: Final[int] = 5
DEFAULT_RUN_TITLE: Final[str] = "SUAS Test Flight"
DEFAULT_RUN_DESCRIPTION: Final[str] = "Test flight for SUAS 2023"


class FlightSettings:
    """
    Class to contain basic information for a flight, as well as some flight parameters

    Attributes
    ----------
    __simple_takeoff: bool
        Sets if the drone will ascend vertically or at an angle
    __run_title: str
        The name for the current flight operation
    __run_description: str
        A small description for the current flight
    __waypoint_count: int
        The number of waypoints to fly for the current flight test

    Methods
    -------
    simple_takeoff() -> bool
        Returns the status of the takeoff type for the flight
    simple_takeoff(simple_takeoff: bool) -> None
        Sets the parameter for a simple or diagonal takeoff
    waypoint_count() -> int
        Returns the number of waypoints to fly for the current flight
    waypoint_count(count: int) -> None
        Setter for configuring the number of waypoints to fly for the flight test
    run_title() -> str
        `Returns the flight title
    run_title(new_title: str) -> None
        Sets a new title for the current flight
    run_description() -> str
        Returns the small description for the current flight
    run_description(new_description: str) -> None
        Sets a new description for the new flight
    """

    def __init__(
        self,
        simple_takeoff: bool = False,
        title: str = DEFAULT_RUN_TITLE,
        description: str = DEFAULT_RUN_DESCRIPTION,
        waypoints: int = DEFAULT_WAYPOINTS,
    ) -> None:
        """
        Default Constructor for flight settings

        Parameters
        ----------
        simple_takeoff : bool = False
            Sets if flight will use a simple vertical takeoff
        title : str
            The name for the flight execution
        description : str
            Sets a descriptive explanation for the current flight execution
        waypoints : int
            The number of waypoints to fly for the flight plan
        """
        self.__simple_takeoff: bool = simple_takeoff
        self.__run_title: str = title
        self.__run_description: str = description
        self.__waypoint_count: int = waypoints

    # ----- Takeoff Settings ----- #
    @property
    def simple_takeoff(self) -> bool:
        """
        Gets simple_takeoff as a private member variable

        Returns
        -------
        simple_takeoff : bool
            Flag for vertical takeoff implementation or other
        """
        return self.__simple_takeoff

    @simple_takeoff.setter
    def simple_takeoff(self, simple_takeoff: bool) -> None:
        """
        Sets the flag for vertical takeoff

        Parameters
        ----------
        simple_takeoff : bool
            Flag for vertical takeoff
        """
        self.__simple_takeoff = simple_takeoff

    # ----- Waypoint Settings ----- #
    @property
    def waypoint_count(self) -> int:
        """
        Gets the number of waypoints as a private member variable

        Returns
        -------
        waypoint_count : int
            Current number of waypoints to fly for the mission
        """
        return self.__waypoint_count

    @waypoint_count.setter
    def waypoint_count(self, count: int) -> None:
        """
        Sets the number of waypoints to fly for the flight mission

        Parameters
        ----------
        count : int
            Total number of waypoints planning to fly for mission
        """
        self.__waypoint_count = count

    # ----- Flight Initialization Settings ----- #
    @property
    def run_title(self) -> str:
        """
        Return the title for the current flight execution

        Returns
        -------
        run_title : str
            Current title for the flight
        """
        return self.__run_title

    @run_title.setter
    def run_title(self, new_title: str) -> None:
        """
        Sets a new title for the current flight

        Parameters
        ----------
        new_title : str
            New title for the flight execution
        """
        self.__run_title = new_title

    @property
    def run_description(self) -> str:
        """
        Returns the description for the current flight execution

        Returns
        -------
        run_description : str
            Detailed description for the current flight plan
        """
        return self.__run_description

    @run_description.setter
    def run_description(self, new_description: str) -> None:
        """
        Sets a new description for the flight

        Parameters
        ----------
        new_description : str
            New description for the current flight
        """
        self.__run_description = new_description
