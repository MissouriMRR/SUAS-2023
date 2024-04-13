"""File storing the webserver for our map overlay."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import json
import uvicorn
from state_machine import Drone

app: FastAPI = FastAPI()

app.mount("/map", StaticFiles(directory="flight/map/static", html=True), name="static")


@app.get("/drone")
def get_drone_info() -> None:
    """Get the drone's current location."""
    pass


@app.get("/odlc")
def get_odlc_data() -> dict[int, int]:
    """Get the ODLC data from the drone.

    Returns
    -------
    dict
        The current ODLC data from the drone.
    """
    with open("flight/data/output.json") as f:
        data = json.load(f)
        print(data)
    return data


async def start_server(drone: Drone) -> None:
    """Start the webserver.

    Parameters
    ----------
    drone : Drone
        The drone object to get the data from.
    """
    config = uvicorn.Config(
        "flight.map.map:app",
        port=9191,
        log_level="info",
    )
    server = uvicorn.Server(config)
    app.drone: Drone = drone
    await server.serve()
