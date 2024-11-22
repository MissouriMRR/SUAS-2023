"""
Testing vision.deskew.vector_utils.py
"""

import unittest
import numpy as np

from scipy.spatial.transform import Rotation

from vision.common.constants import SENSOR_HEIGHT, SENSOR_WIDTH, ROTATION_OFFSET

from vision.deskew.vector_utils import pixel_intersect
from vision.deskew.vector_utils import plane_collision
from vision.deskew.vector_utils import pixel_vector
from vision.deskew.vector_utils import pixel_angle
from vision.deskew.vector_utils import focal_length_to_fovs
from vision.deskew.vector_utils import get_fov
from vision.deskew.vector_utils import camera_vector
from vision.deskew.vector_utils import edge_angle
from vision.deskew.vector_utils import rotate_degrees
from vision.deskew.vector_utils import rotate_radians
from vision.deskew.vector_utils import IHAT



class TestVectorUtils(unittest.TestCase):
	"""
	Testing the pixel_intersect function; Finds the intersection [X,Y] of a given pixel with the ground relative to the camera.
	"""
	def test_pixel_intersect(self):
        # Test case 1: Check for intersection with ground
		pixel = (500, 500)
		image_shape = (1000, 1000, 3)
		focal_length = 50
		rotation_deg = [0, 0, 0]
		height = 100.0
		result = pixel_intersect(pixel, image_shape, focal_length, rotation_deg, height)
		self.assertIsNotNone(result)
        
        # Test case 2: No intersection (ray pointing upwards)
		rotation_deg = [0, 180, 0]
		result = pixel_intersect(pixel, image_shape, focal_length, rotation_deg, height)
		self.assertIsNone(result)

	"""
	Testing the plane_collision function; Returns the point where a ray intersects the XY plane.
	"""
	def test_plane_collision(self):
		# Test case 1: Intersection with plane
		ray_direction = np.array([1, 0, -1], dtype=np.float64)
		height = 100.0
		result = plane_collision(ray_direction, height)
		expected = np.array([100.0, 0.0])
		np.testing.assert_array_almost_equal(result, expected)
        
        # Test case 2: No intersection (ray pointing upwards)
		ray_direction = np.array([1, 0, 1], dtype=np.float64)
		result = plane_collision(ray_direction, height)
		self.assertIsNone(result)

	"""
	Testing the pixel_vector function; Generates a vector representing the given pixel.
	"""
	def test_pixel_vector(self):
		# Test for generating vector from pixel
		pixel = (500, 500)
		image_shape = (1000, 1000, 3)        
		focal_length = 50
		result = pixel_vector(pixel, image_shape, focal_length)
		self.assertEqual(result.shape, (3,))
        
        # Ensure vector is normalized
		norm = np.linalg.norm(result)
		self.assertAlmostEqual(norm, 1.0)

	"""
	Testing the pixel_angle function; Calculates a pixel's angle from the center of the camera on a single axis.
	"""
	def test_pixel_angle(self):
        # Test for angle calculation from pixel position
		fov = np.deg2rad(90)  # 90 degrees field of view
		ratio = 0.5
		result = pixel_angle(fov, ratio)
		expected = 0.0
		self.assertAlmostEqual(result, expected)
        
        # Test edge case
		ratio = 0.0
		result = pixel_angle(fov, ratio)
		expected = np.arctan(np.tan(fov / 2) * (1 - 2 * ratio))
		self.assertAlmostEqual(result, expected)

	"""
	Testing the focal_length_to_fovs function; Converts a given focal length to the horizontal and vertical fields of view in radians.
	"""
	def test_focal_length_to_fovs(self):
        # Test for converting focal length to FOVs
		focal_length = 50
		result = focal_length_to_fovs(focal_length)
		expected = (get_fov(focal_length, SENSOR_WIDTH), get_fov(focal_length, SENSOR_HEIGHT))
		self.assertEqual(result, expected)
	
	"""
	Testing the get_fov function; Converts a given focal length and sensor length to the corresponding field of view in radians.
	"""
	def test_get_fov(self):
        # Test for single FOV calculation
		focal_length = 50
		sensor_size = 35.0  # Typical full-frame sensor width in mm
		result = get_fov(focal_length, sensor_size)
		expected = 2 * np.arctan(sensor_size / (focal_length))
		self.assertAlmostEqual(result, expected)

	"""
	Testing the camera_vector function; Generates a vector with the angle h_angle with the horizontal and an angle v_angle with the vertical.
	"""
	def test_camera_vector(self):
        # Test for generating a camera vector
		h_angle = np.deg2rad(45)
		v_angle = np.deg2rad(45)
		result = camera_vector(h_angle, v_angle)
		self.assertEqual(result.shape, (3,))
        
        # Ensure vector is normalized
		norm = np.linalg.norm(result)
		self.assertAlmostEqual(norm, 1.0)

	"""
	Testing the edge_angle function; Finds the angle in radians such that rotating by edge_angle on the Y axis then rotating by h_angle on the Z axis vector an angle v_angle with the Y axis.
	"""
	def test_edge_angle(self):
        # Test for edge angle calculation
		v_angle = np.deg2rad(45)
		h_angle = np.deg2rad(45)
		result = edge_angle(v_angle, h_angle)
		expected = np.arctan(np.tan(v_angle) * np.cos(h_angle))
		self.assertAlmostEqual(result, expected)

	"""
	Testing the rotate_degrees function; Rotates a vector based on a given roll, pitch, and yaw in degrees.
	"""
	def test_rotate_degrees(self):
        # Test for rotating a vector by degrees
		vector = np.array([1, 0, 0], dtype=np.float64)
		rotation_deg = [0, 90, 0]  # Pitch up by 90 degrees
		result = rotate_degrees(vector, rotation_deg)
		expected = rotate_radians(vector, np.deg2rad(rotation_deg).tolist())
		np.testing.assert_array_almost_equal(result, expected)

	"""
	Testing the rotate_radians function; Rotates a vector based on a given roll, pitch, and yaw in radians.
	"""
	def test_rotate_radians(self):
        # Test for rotating a vector by radians
		vector = np.array([1, 0, 0], dtype=np.float64)
		rotation_rad = [0, np.pi / 2, 0]  # Pitch up by 90 degrees
		result = Rotation.from_euler("xyz", rotation_rad).apply(np.array(vector))
		expected = np.array([0, 0, -1], dtype=np.float64)
		np.testing.assert_array_almost_equal(result, expected)


if __name__ == '__main__':
	unittest.main()

		

		
		
		
		
		
		
		
		
		
		
