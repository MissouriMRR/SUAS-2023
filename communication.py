"""Communication object to pass between flight and vision code"""


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
        self.__state: str = "Start_State"

    @property
    def state(self) -> str:
        return self.__state

    @state.setter
    def state(self, new_state: str) -> None:
        self.__state = new_state
        return
