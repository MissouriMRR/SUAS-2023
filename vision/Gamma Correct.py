import cv2 as cv
import numpy as np
def gammaCorrection(src, gamma):
    #recommended gamma value is 2.5. Takes unedited images as input and a gamma value. Changes the gamme of the image
    invGamma = 1 / gamma
    table = [((i / 255) ** invGamma) * 255 for i in range(256)]
    table = np.array(table, np.uint8)

    return cv.LUT(src, table)

    
if __name__ == "__main__":
    #reads and resizes the image
    img = cv.imread('multirotor\\sky_shot.jpg')
    img_resize = cv.resize(img, (640, 480))

    #corrects the image
    cv.imshow('gamma_correct', gammaCorrection(img_resize, 2.5))