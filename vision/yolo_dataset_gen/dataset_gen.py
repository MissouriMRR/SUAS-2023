import numpy as np
import nptyping as npt
import cv2
import math as m
import vision.common.constants as consts


def regular_polygon_ctr(pts_amt: int, size: int) -> consts.Contour:
    """
    
    """
    HALF_SIZE: int = size//2
    TAU: float = m.pi*2
    RADIAN_STEP: float = TAU/pts_amt

    pts: list[list[float]] = list()

    i: int
    for i in range(pts_amt):
        pts.append([round(HALF_SIZE*m.cos(RADIAN_STEP*i)), round(HALF_SIZE*m.sin(RADIAN_STEP*i))])
    
    return np.array(pts).reshape((-1, 1, 2)).astype(np.intc)