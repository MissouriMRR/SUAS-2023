# Declares the Start state class.
from typing import Awaitable, Callable, ClassVar

from .state import State


class Start(State):
    """
    The Start state of the state machine.

    Attributes
    ----------
    run_callable : Callable[["Start"], Awaitable[State]]
        The callable object which gets executed when the `run` method is called.

    Methods
    -------
    run() -> Awaitable[State]
        Executes the start state using the defined callable and transitions to the next state.

        Returns
        -------
        Awaitable[State]
            An awaitable state resulting from the execution of run_callable.
    """

    run_callable: ClassVar[Callable[["Start"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        """
        Executes the run_callable associated with the Start state.

        Returns
        -------
        Awaitable[State]
            An awaitable state resulting from the execution of run_callable.
        """
        return self.run_callable()
