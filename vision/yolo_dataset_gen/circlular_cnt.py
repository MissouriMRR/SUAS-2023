import numpy as np
import nptyping as npt
import cv2
# import vision.common.constants as consts

def circle_norm_ctr(num_samples):
    """
    Generates a normalized circle contour
    """
    
    sample_angles = np.linspace(0, 2 * np.pi, num_samples, endpoint=False)
    
    xy_array = np.array([np.cos(sample_angles), np.sin(sample_angles)])
    
    point_array = np.swapaxes(xy_array, 0, 1)
    
    point_array = point_array / 2
    
    return point_array


def half_circle_nctr(num_samples):
    """
    Generates a normalized half-circle contour
    """
    
    sample_angles = np.linspace(0, np.pi, num_samples)
    
    xy_array = np.array([np.cos(sample_angles), np.sin(sample_angles)])
    
    point_array = np.swapaxes(xy_array, 0, 1)
    
    point_array = point_array / 2
    
    return point_array


def quarter_circle_nctr(num_samples):
    sample_angles = np.linspace(0, np.pi / 2, num_samples, endpoint=True)
    
    xy_array = np.array([np.cos(sample_angles), np.sin(sample_angles)])
    
    point_array = np.swapaxes(xy_array, 0, 1)
    
    point_array = point_array
    
    return point_array

print(quarter_circle_nctr(8))
