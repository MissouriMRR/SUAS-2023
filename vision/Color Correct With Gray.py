#This file finds the average gray rgb of a given image and attempts to correct the image by replacing all of the gray with the average gray value. 
#This method does not work and only affects the gray currently.
import cv2 as cv
import numpy as np
def show_images(img):
    #has a bunch of images to show in order to check functions.
    #cv.imshow('masked_image', masked_image)
    #cv.imshow('RGB', RGB)
    #cv.imshow('HSV', HSV)
    cv.imshow('mask', find_gray_with_saturation(img_resize))
    cv.imshow('make gray single color', correct_image_gray(img_resize))
    cv.imshow('img', img_resize)
    cv.waitKey(0)
    cv.destroyAllWindows()


#Non functional find grey and use to correct method
def find_gray_with_saturation(img):
    #finds the gray in the image. Takes unedited images as input
    HSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    gray_lower = np.array([2, 2, 2])
    gray_upper = np.array([40, 30, 255])
    mask = cv.inRange(HSV, gray_lower, gray_upper)
    return mask

def average_gray(img):
    #finds the average RGB value of the gray in the image. Takes the average of the 3 channels. Takes unedited images as input
    masked_image = cv.bitwise_and(img, img, mask=find_gray_with_saturation(img))
    average = cv.mean(masked_image)
    average_mean = (average[0] + average[1] + average[2]) / 3
    return average_mean

def correct_image_gray(img):
    #finds all of the gray in the image and replaces it with the average gray value. Takes unedited images as input
    average = average_gray(img)
    mask = find_gray_with_saturation(img)
    img[mask > 0] = (average, average, average)
    cv.imwrite('multirotor\\sky_shot_normalized.jpg', img)
    return img

if __name__ == "__main__":
    #reads and resizes the image
    img = cv.imread('multirotor\\sky_shot.jpg')
    img_resize = cv.resize(img, (640, 480))

    #corrects the image
    masked_image = cv.bitwise_and(img_resize, img_resize, mask=find_gray_with_saturation(img_resize))