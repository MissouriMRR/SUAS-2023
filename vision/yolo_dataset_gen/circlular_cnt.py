import numpy as np
import nptyping as npt
import cv2

# import vision.common.constants as consts


def circle_norm_ctr(num_samples):
    """
    Generates a normalized circle contour
    """
    
    # Creates the set of angles at which the samples will be taken
    sample_angles = np.linspace(0, 2 * np.pi, num_samples, endpoint=False)

    # Generates an array in the format [x_values, y_values]
    xy_array = np.array([np.cos(sample_angles), np.sin(sample_angles)])

    # Swap the axes to get an array of length 2 arrays
    point_array = np.swapaxes(xy_array, 0, 1)
    
    # Recenter the shape on (1,1) and divide by 2 to normalize to the range [0,1]
    point_array = (point_array + 1) / 2

    return point_array


def half_circle_nctr(num_samples):
    """
    Generates a normalized half-circle contour
    """
    
    # Creates the set of angles at which the samples will be taken
    sample_angles = np.linspace(0, np.pi, num_samples)
    
    # Generates an array in the format [x_values, y_values]
    xy_array = np.array([np.cos(sample_angles), np.sin(sample_angles)])
    
    # Swap the axes to get an array of length 2 arrays
    point_array = np.swapaxes(xy_array, 0, 1)
    
    # Nudge the half-circle downwards
    point_array[:, 1] -= 0.5
    
    # Recenter the shape on (1,1) and divide by 2 to normalize to the range [0,1]
    point_array = (point_array + 1) / 2
    
    return point_array


def quarter_circle_nctr(num_samples):
    """
    Creates a normalized quarter circle contour
    """
    
    # Creates the set of angles at which the samples will be taken
    sample_angles = np.linspace(0, np.pi / 2, num_samples, endpoint=True)

    # Generates an array in the format [x_values, y_values]
    xy_array = np.array([np.cos(sample_angles), np.sin(sample_angles)])

    # Swap the axes to get an array of length 2 arrays
    point_array = np.swapaxes(xy_array, 0, 1)
    
    # Add the corner point at (0,0)
    point_array = np.append(point_array, [[0,0]], axis=0)
    
    # Contour is already normalized because it is just the top-right quarter of a circle

    return point_array



