"""File to hold important constant values and configure drone upon startup"""

from mavsdk import System

MAX_ALT: int = 500  # Feet
TAKEOFF_ALT: int = 75  # Feet
WAIT: float = 2.0  # Seconds


async def config_params(drone: System) -> None:
    """
    Sets certain parameters within the drone for flight

    Parameters
    ----------
    drone : System
        MAVSDK object for manual drone control & manipulation
    """
    await drone.param.set_param_float("MIS_TAKEOFF_ALT", TAKEOFF_ALT)

    # Set data link loss failsafe mode HOLD
    await drone.param.set_param_int("NAV_DLL_ACT", 1)
    # Set offboard loss failsafe mode HOLD
    await drone.param.set_param_int("COM_OBL_ACT", 1)
    # Set offboard loss failsafe mode when RC is available to HOLD
    await drone.param.set_param_int("COM_OBL_RC_ACT", 5)

    # Set RC loss failsafe mode HOLD
    await drone.param.set_param_int("NAV_RCL_ACT", 1)
    await drone.param.set_param_float("LNDMC_XY_VEL_MAX", 0.5)
    await drone.param.set_param_float("LNDMC_ALT_MAX", MAX_ALT)
