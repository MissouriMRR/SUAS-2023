import cv2
import numpy as np
#from vision.standard_object.odlc_classify_shape import classify_shape

#filename = "dji_fly_20230930_154916_57_1696107023985_timed.jpg"


filename = "Copy of dji_fly_20221203_131406_6_1670094877955_photo_optimized.jpg"
bgr_img = cv2.imread(filename)

# bgr_img = cv2.GaussianBlur(bgr_img, (11,11), 0)

hsv_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

saturation = hsv_img[:, :, 1]

cv2.imwrite("saturation.png", saturation)

_, image = cv2.threshold(saturation, np.average(saturation) + 20, 255, cv2.THRESH_BINARY)

cv2.imwrite("thresh.png", image)

contours, _hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)


# draw_img = np.copy(image)
draw_img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

# draw_img = cv2.drawContours(draw_img, contours, -1, (0, 255, 0), 1)

num_detections = 0
for cnt in contours:
    if len(cnt) > 1:
        #classification = classify_shape(np.copy(cnt), [])
        ##if classification is not None:
            # print(classification)
            draw_img = cv2.drawContours(draw_img, [cnt], -1, (0, 255, 0), 5)
            num_detections += 1

cv2.imwrite("drawn.png", draw_img)
# print(num_detections)