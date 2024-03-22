import unittest
import numpy as np
import json
import chars
from odlc_classify_shape import cart2pol, toPolar, merge_sort, condense_polar, Generate_Polar_Array, Verify_Shape_Choice, Compare_Based_On_Peaks, classify_shape, Image_Address_To_Contour

class TestShapeClassification(unittest.TestCase):

    # Convertes x and y rectangular values to radius, angle tuples
    def test_cart2pol(self):
        x, y = 3, 4
        expected_rho = 5.0
        expected_phi = np.arctan(4, 3)
        rho, phi = cart2pol(x, y)
        self.assertAlmostEqual(rho, expected_rho)
        self.assertAlmostEqual(phi, expected_phi)


    
# Converts an array of Rectangular Coordinates to Polar
    def test_toPolar(self):
        input_data = [((0, 0),), ((1, 0),), ((0, 1),), ((-1, 0),), ((0, -1),)]
        expected_output = [(0.0, 0.0), (1.0, 0.0), (1.0, np.pi/2), (1.0, np.pi), (1.0, -np.pi)]
        for i in range(len()):
            {
                for i, coords in enumerate(input_data):
                    with self.subTest (i =i):
                        result = toPolar(np.array(coords))
                        self.assertAlmostEqual(result[0][0], expected_output[i][0], places=8)
                        self.assertAlmostEqual(result[0][1], expected_output[i][1], places=8)
            }
# Python implementation of merge sort algorithm, slightly edited to fit our array structure of tuples (sorted based on increasing angle).
    def test_merge_sort(self):
        data = [(1, 3), (2, 2), (3, 1)]
        sorted_data = merge_sort(data)
        self.assertEqual(sorted_data, [(3, 1), (2, 2), (1, 3)])


# Condenses the array of polar coordinates to have 'NUM_STEPS' points stored for analysis    def Generate_Polar_Array(self):
        contour = [[(1, 1)], [(-1, 1)], [(-1, -1)], [(1, -1)]]
        x_expected = [0.0, 1.0, 1.0, -1.0]
        y_expected = [0.0, 0.0, 1.5708, 3.14159]

        x_actual, y_actual = Generate_Polar_Array(contour)

        self.assertEqual(x_actual, x_expected)
        self.assertEqual(y_actual, y_expected)  


    def test_verify_shape_choice(self):

        mystery_radii_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        shape_choice = chars.ODLCShape.CIRCLE

        sample_ODLC_radii = [0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.77, 0.88]
        self.assertTrue(Verify_Shape_Choice(mystery_radii_list, shape_choice, sample_ODLC_radii))

        mystery_radii_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
        shape_choice = chars.ODLCShape.TRIANGLE

        sample_ODLC_radii = [0.11, 0.22, 0.33, 0.44, 0.55, 0.66, 0.77, 0.88]
        self.assertFalse(Verify_Shape_Choice(mystery_radii_list, shape_choice, sample_ODLC_radii))

    def test_compare_based_on_peaks(self):
        mysteryArr = ([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
        self.assertEqual(Compare_Based_On_Peaks(mysteryArr), chars.ODLCShape.CIRCLE)

        mysteryArr = ([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1])
        self.assertEqual(Compare_Based_On_Peaks(mysteryArr), chars.ODLCShape.CROSS)

        


    def test_all_shapes():
        for i in range(8):
            image_address = "/Users/ouyangyuxuan/Desktop/NewImg/shape" + str(i + 1) + ".png"
            contour = Image_Address_To_Contour(image_address)
            image_dims = (image.shape[0], image.shape[1])  
            shape = classify_shape(contour, image_dims)
            print(f"Shape {i+1}: {shape}")


        
    if __name__ == '__main__':
        unittest.main()