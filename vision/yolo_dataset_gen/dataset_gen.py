import numpy as np
import nptyping as npt
import cv2
import math as m
import vision.common.constants as consts
import vision.yolo_dataset_gen.ml_constants as ml_consts


def regular_polygon_ctr(pts_amt: int, out_size: int) -> consts.Contour:
    """
    Generates the contour points of a regular polygon inscribed in a circle of a given size

    Parameters
    ----------
    pts_amt : int
        The number of verticies the shape will have (number of contour points of output)
    size : int
        The diameter (not radius) of the circle that the shape will be inscribed in (px)
    
    Returns
    -------
    contour : consts.Contour
        The points of the regular polygon inscribed in the shape of diameter size.
        NOTE: Centered on (0, 0), so some points will have negative values. Therefore,
        the shape's points must be adjusted before it can be placed on an image.

    Raises
    ------
    TODO: find out the format for this section
    """
    if pts_amt < 3:
        raise ValueError("Shape must have at least 3 points")
    HALF_SIZE: int = out_size//2
    TAU: float = m.pi*2
    RADIAN_STEP: float = TAU/pts_amt

    pts: list[list[float]] = list()

    i: int
    for i in range(pts_amt):
        pts.append([round(HALF_SIZE*m.cos(RADIAN_STEP*i)), round(HALF_SIZE*m.sin(RADIAN_STEP*i))])
    
    return np.array(pts).reshape((-1, 1, 2)).astype(np.intc)


def rotate_norm_ctr(nctr: ml_consts.Norm_Ctr, rot: float) -> ml_consts.Norm_Ctr:
    """
    
    """
    out_nctr: ml_consts.Norm_Ctr = np.empty(nctr.shape, np.float64)
    for idx, pnt in enumerate(nctr):
        out_nctr[idx, 0] = nctr[idx, 0] * m.cos(rot) - nctr[idx, 1] * m.sin(rot)
        out_nctr[idx, 1] = nctr[idx, 0] * m.sin(rot) + nctr[idx, 1] * m.cos(rot)
    
    return out_nctr


def norm_ctr_to_cv2(norm: ml_consts.Norm_Ctr, out_size: int) -> consts.Contour:
    """
    
    """
    out_ctr: consts.Contour = np.empty((len(norm),))