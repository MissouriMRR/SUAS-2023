"""Class to contain setters, getters & parameters for current flight"""

from typing import Final

DEFAULT_RUN_TITLE: Final[str] = "SUAS Test Flight"
DEFAULT_RUN_DESCRIPTION: Final[str] = "Test flight for SUAS 2023"
DEFAULT_STANDARD_OBJECT_COUNT: Final[int] = 5


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
    __skip_waypoint: bool
        Whether to skip the waypoint state.
    __standard_object_count: int
        The number of standard objects to attempt to find.
    __sim_flag: bool
        A flag representing if the connected drone is a simulation
    __path_data_path: str
        The path to the JSON file containing the boundary and waypoint data.

    Methods
    -------
    simple_takeoff() -> bool
        Returns the status of the takeoff type for the flight
    simple_takeoff(simple_takeoff: bool) -> None
        Sets the parameter for a simple or diagonal takeoff
    skip_waypoint() -> bool
        Returns whether to skip the waypoint state.
    skip_waypoint(flag: bool) -> None
        Setter for configuring whether to skip the waypoint state.
    standard_object_count() -> int
        Returns the number of standard objects to attempt to find.
    standard_object_count(count: int) -> None
        Setter for the number of standard objects to attempt to find.
    run_title() -> str
        `Returns the flight title
    run_title(new_title: str) -> None
        Sets a new title for the current flight
    run_description() -> str
        Returns the small description for the current flight
    run_description(new_description: str) -> None
        Sets a new description for the new flight
    sim_flag() -> bool
        Returns the flag for the simulation
    sim_flag(sim_flag: bool) -> None
        Sets the flag for the simulation
    path_data_path() -> str
        Return the path to the JSON file containing the boundary and waypoint data.
    path_data_path(path_data_path: str) -> None
        Set the path to the JSON file containing the boundary and waypoint data.
    """

    def __init__(
        self,
        simple_takeoff: bool = False,
        title: str = DEFAULT_RUN_TITLE,
        description: str = DEFAULT_RUN_DESCRIPTION,
        skip_waypoint: bool = False,
        standard_object_count: int = DEFAULT_STANDARD_OBJECT_COUNT,
        sim_flag: bool = False,
        path_data_path: str = "flight/data/waypoint_data.json",
    ) -> None:
        """
        Default Constructor for flight settings

        Parameters
        ----------
        simple_takeoff : bool, default False
            Sets if flight will use a simple vertical takeoff
        title : str
            The name for the flight execution
        description : str
            Sets a descriptive explanation for the current flight execution
        skip_waypoint : bool
            Whether to skip the waypoint state.
        standard_object_count : int
            The number of standard objects to attempt to find.
        sim_flag : bool, default False
            A flag representing if the connected drone is a simulation
        path_data_path : str, default "flight/data/waypoint_data.json"
            The path to the JSON file containing the boundary and waypoint data.
        """
        self.__simple_takeoff: bool = simple_takeoff
        self.__run_title: str = title
        self.__run_description: str = description
        self.__skip_waypoint: bool = skip_waypoint
        self.__standard_object_count: int = standard_object_count
        self.__sim_flag: bool = sim_flag
        self.__path_data_path: str = path_data_path

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
    def skip_waypoint(self) -> bool:
        """
        Gets whether to skip the waypoint state as a private member variable.

        Returns
        -------
        skip_waypoint : bool
            Whether to skip the waypoint state.
        """
        return self.__skip_waypoint

    @skip_waypoint.setter
    def skip_waypoint(self, flag: bool) -> None:
        """
        Sets whether to skip the waypoint state.

        Parameters
        ----------
        flag : bool
            Whether to skip the waypoint state.
        """
        self.__skip_waypoint = flag

    # ----- ODLC Settings ----- #
    @property
    def standard_object_count(self) -> int:
        """
        Get the number of standard objects to attempt to find.

        Returns
        -------
        count : int
            The number of standard objects to attempt to find.
        """
        return self.__standard_object_count

    @standard_object_count.setter
    def standard_object_count(self, count: int) -> None:
        """
        Set the number of standard objects to attempt to find.

        Parameters
        ----------
        count : int
            The number of standard objects to attempt to find.
        """
        self.__standard_object_count = count

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

    @property
    def sim_flag(self) -> bool:
        """
        Returns the flag for the simulation

        Returns
        -------
        sim_flag : bool
            Flag for the simulation
        """
        return self.__sim_flag

    @sim_flag.setter
    def sim_flag(self, sim_flag: bool) -> None:
        """
        Sets the flag for the simulation

        Parameters
        ----------
        sim_flag : bool
            Flag for the simulation
        """
        self.__sim_flag = sim_flag

    @property
    def path_data_path(self) -> str:
        """
        Return the path to the JSON file containing the boundary and waypoint data.

        Returns
        -------
        path_data_path : str
            The path to the JSON file containing the boundary and waypoint data.
        """
        return self.__path_data_path

    @path_data_path.setter
    def path_data_path(self, path_data_path: str) -> None:
        """
        Set the path to the JSON file containing the boundary and waypoint data.

        Parameters
        ----------
        path_data_path : str
            The path to the JSON file containing the boundary and waypoint data.
        """
