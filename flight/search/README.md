**Search Subdirectory**

Cell map - A data structure to hold the probability map created by the segmenter functionality, also contains testing functions for the cell maps class.

Cell - Defines the cell data class and represents a grid cell in the search area.

Helper - Contains several useful functions commonly found in other files like ```calculate_dist``` and ```get_bounds```

Plot algo - The algorithm powering the drone's navigation. Contains classes and functions for generating the map based on provided coordinates, compressing it for faster searching, identifying valid locations, marking them, creating the path, and decompressing it back to regular coordinates to use.

Plotter - Provides plotting functionality for visualizing coordinate data. Contains functions for plotting points and creating the probability map.

Segmenter - Divides the ODLC Search Area into a probability map and contains functions for adjusting collections of points,
