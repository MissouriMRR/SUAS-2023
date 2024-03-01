"""
Testing vision.common.__pycache__.crop.py
"""

import unittest
import numpy as np
import cv2
from vision.common.crop import crop_image
from vision.common.constants import Image
from vision.common.bounding_box import BoundingBox, tlwh_to_vertices, Vertices, ObjectType
def manipulate_image(img):
        height, width = img.shape[:2]

        for y in range(height):
            for x in range(width):
                # Calculate new RGB values based on position
                r = x * 255 // width  # More red as it goes left
                g = img[y, x, 1]  # Green remains unchanged
                b = y * 255 // height  # More blue as it goes down

                # Update pixel with new RGB values
                img[y, x] = [r, g, b]

        return img

class TestCropImage(unittest.TestCase):
    """
    Testing the crop_image function from the crop module
    """
    
    

    def test_crop_size(self) -> None:
        """
        generate a gradiant image red increases on 1 azis blue on the other crop it to a specific 
        size test the right size and test the value in the area is the right value against the gradient
        which we will detemine how do the part of the picture cropped is correct later.
        """
        test_vertices: Vertices = tlwh_to_vertices(1,1,5,5)
        testType: ObjectType = ObjectType.STD_OBJECT
        TestBox: BoundingBox= BoundingBox(test_vertices, testType)
        test_Image: Image = cv2.imread("test_images/test1.jpg")
        resulting_image: Image = crop_image(test_Image, TestBox)
        resulting_image_size_x = resulting_image.shape[1]
        resulting_image_size_y = resulting_image.shape[0]
        
        # Tests to insure the expected output is the same as the actual output, given the same input
        self.assertEqual(5, resulting_image_size_x)
        self.assertEqual(5, resulting_image_size_y)

    def test_crop_area(self) -> None:
        """
        generate a gradiant image red increases on 1 azis blue on the other crop it to a specific 
        size test the right size and test the value in the area is the right value against the gradient
        which we will detemine how do the part of the picture cropped is correct later.
        """
        test_vertices: Vertices = tlwh_to_vertices(1,1,5,5)
        testType: ObjectType = ObjectType.STD_OBJECT
        TestBox: BoundingBox= BoundingBox(test_vertices, testType)
        test_Image: Image = cv2.imread("test_images/whiteSquare.jpg")
        manipulated_img = manipulate_image(test_Image)
        resulting_image: Image = crop_image(manipulated_img, TestBox)

        height, width = resulting_image.shape[:2]
        # Calculate the coordinates of the middle pixel
        middle_x = width // 2
        middle_y = height // 2
        # Get the RGB values of the middle pixel
        b, g, r = resulting_image[middle_y, middle_x]
        #print("RGB values of the middle pixel:", (r, g, b))
        
        self.assertEqual(19, r)
        self.assertEqual(255, g)
        self.assertEqual(18, b)


if __name__ == "__main__":
    unittest.main()