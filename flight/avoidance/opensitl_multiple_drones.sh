cd ../../../PX4-Autopilot
export PX4_HOME_LAT=37.9490953
export PX4_HOME_LON=-91.7848293
#export PX4_SIM_SPEED_FACTOR=1.5
make px4_sitl_default
gnome-terminal -- /bin/sh -c "./Tools/simulation/sitl_multiple_run.sh 2; ./Tools/simulation/jmavsim/jmavsim_run.sh -l"
gnome-terminal -- ./Tools/simulation/jmavsim/jmavsim_run.sh -p 4561 -l
