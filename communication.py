"""Communication object to pass between flight and vision code"""

from flight.states import StateEnum


class Communication:
    """
    Object that is passed between flight and vision code to convey
    current state, and update if necessary

    Attributes
    ----------
    __state: str
        The name of the current state in the Flight State Machine

    Methods
    -------
    state() -> str
        Returns the name of the current state
    state(new_state) -> None
        Updates the name of the current state
    """

    def __init__(self) -> None:
        """
        Initializes the Communication module to the first state in the state machine
        """
        self.__state: str = StateEnum.Start_State

    @property
    def state(self) -> str:
        """
        Function to return the name of the state

        Returns
        -------
        __state : str
            State name assigned to the individual state
        """
        return self.__state

    @state.setter
    def state(self, new_state: str) -> None:
        """
        Changes the current state to the one passed

        Parameters
        ----------
        new_state : str
            Name of teh new state in the state machine
        """
        self.__state = new_state
