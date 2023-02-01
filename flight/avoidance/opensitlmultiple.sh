# Requires a working directory of flight

cd ../../PX4-Autopilot
export PX4_HOME_LAT=37.9490953
export PX4_HOME_LON=-91.7848293
# export PX4_SIM_SPEED_FACTOR=1.5
DONT_RUN=1 make px4_sitl_default gazebo
gnome-terminal -- ./Tools/simulation/gazebo/sitl_multiple_run.sh -n 2
