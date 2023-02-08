"""
Bounding box objects represent an area in an image and
are used to convey information between flight and vision processes.
"""

from enum import Enum
from typing import Any, TypeAlias

import numpy as np

# A set of 4 coordinates that distinguish a region of an image.
# The order of the coordinates is (top-left, top-right, bottom-right, bottom-left).
Vertices: TypeAlias = tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]


def tlwh_to_vertices(tl_x: int, tl_y: int, width: int, height: int) -> Vertices:
    """
    Gets the vertices of a bounding box from a coordinate, width, and height.

    Parameters
    ----------
    tl_x : int
        the top-left x coordinate of the bounding box
    tl_y : int
        the top-left y coordinate of the bounding box
    width : int
        the width of the bounding box
    height : int
        the height of the bounding box

    Returns
    -------
    vertices : Vertices
        Denotes the 4 coordinates representing a box in an image.
        Vertices is a tuple of 4 coordinates.
        Each coordinate consists of a tuple 2 integers.
        Order is (top-left, top-right, bottom-right, bottom-left).
    """
    tl_coord: tuple[int, int] = (tl_x, tl_y)  # top left
    tr_coord: tuple[int, int] = (tl_x + width, tl_y)  # top right
    br_coord: tuple[int, int] = (tl_x + width, tl_y + height)  # bottom right
    bl_coord: tuple[int, int] = (tl_x, tl_y + height)  # bottom left

    return (tl_coord, tr_coord, br_coord, bl_coord)


class ObjectType(Enum):
    """
    Type of object that a BoundingBox represents.
    """

    STD_OBJECT: str = "std_object"
    EMG_OBJECT: str = "emg_object"
    TEXT: str = "text"


class BoundingBox:
    """
    A set of 4 coordinates that distinguish a region of an image.
    The order of the coordinates is (top-left, top-right, bottom-right, bottom-left).

    Parameters
    ----------
    vertices : Vertices
        The main structure of the BoundingBox. Denotes the 4 coordinates
        representing a box in an image. Vertices is a tuple of 4 coordinates. Each
        coordinate consists of a tuple 2 integers.
    obj_type : ObjectType
        Enumeration that denotes what type of object the BoundingBox represents.
    attributes : dict[str, Any] | None
        Any additional attributes to convey about the object in the BoundingBox.
    """

    def __init__(
        self,
        vertices: Vertices,
        obj_type: ObjectType,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self._vertices: tuple[
            tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]
        ] = vertices
        self._obj_type: ObjectType = obj_type
        self._attributes: dict[str, Any] = attributes if attributes is not None else {}

    def __repr__(self) -> str:
        """
        Returns a string representation of the BoundingBox
        that contains its id, object type, and vertices.

        Returns
        -------
        str
            the string representation of the BoundingBox object
        """
        return f"BoundingBox[{id(self)}, {self.obj_type}]: {str(self._vertices)}"

    @property
    def vertices(self) -> Vertices:
        """
        Getter for _vertices. Gets the 4 vertices that make up the BoundingBox.

        Returns
        -------
        _vertices : Vertices
            The 4 coordinates of the BoundingBox.
        """
        return self._vertices

    @vertices.setter
    def vertices(self, verts: Vertices) -> None:
        """
        Setter for _vertices. Sets the 4 vertices that make up the BoundingBox.

        Parameters
        ----------
        vert : Vertices
            The 4 coordinates to assign to the BoundingBox.
        """
        self._vertices = verts

    @property
    def obj_type(self) -> ObjectType:
        """
        Getter for _obj_type. Gets the ObjectType of the BoundingBox.

        Returns
        -------
        _obj_type : ObjectType
            The ObjectType of the BoundingBox.
        """
        return self._obj_type

    @obj_type.setter
    def obj_type(self, o_type: ObjectType) -> None:
        """
        Setter for _obj_type. Sets the value of the BoundingBox's ObjectType.

        Parameters
        ----------
        o_type : ObjectType
            The ObjectType to assign to the BoundingBox.
        """
        self._obj_type = o_type

    @property
    def attributes(self) -> dict[str, Any]:
        """
        Getter for _attributes. Gets the additional attributes of the BoundingBox.

        Returns
        -------
        _attributes : dict[str, Any]
            Any additional attributes of the BoundingBox.
        """
        return self._attributes

    @attributes.setter
    def attributes(self, att: dict[str, Any]) -> None:
        """
        Setter for _attributes. Sets the value of the BoundingBox's additional attributes.

        Parameters
        ----------
        att : dict[str, Any]
            The additional attributes to assign to the BoundingBox.
        """
        self._attributes = att

    def set_attribute(self, attribute_name: str, attribute: Any) -> None:
        """
        Sets an attribute of the BoundingBox.

        Parameters
        ----------
        attribute_name : str
            the name of the attribute
        attribute : Any
            the value to set the attribute to, which can be of any type
        """
        self.attributes[attribute_name] = attribute

    def get_attribute(self, attribute_name: str) -> Any:
        """
        Gets an attribute of the BoundingBox.

        Parameters
        ----------
        attribute_name : str
            the name of the attribute

        Returns
        -------
        attribute : Any
            the value of the attribute, which can be of any type
        """
        return self.attributes[attribute_name]

    def get_x_vals(self) -> list[int]:
        """
        Gets the x values of the 4 coordinates.

        Returns
        -------
        x_vals : list[int]
            The 4 x values of the vertices.
        """
        x_vals: list[int] = [vert[0] for vert in self._vertices]
        return x_vals

    def get_y_vals(self) -> list[int]:
        """
        Gets the y values of the 4 coordinates.

        Returns
        -------
        y_vals : list[int]
            The 4 y values of the vertices.
        """
        y_vals: list[int] = [vert[1] for vert in self._vertices]
        return y_vals

    def get_x_extremes(self) -> tuple[int, int]:
        """
        Gets the minimum and maximum x values of the BoundingBox

        Returns
        -------
        min_x, max_x : tuple[int, int]
            The minimum and maximum x values.
        """
        x_vals: list[int] = self.get_x_vals()
        min_x: int = np.amin(x_vals)
        max_x: int = np.amax(x_vals)

        return min_x, max_x

    def get_y_extremes(self) -> tuple[int, int]:
        """
        Gets the minimum and maximum y values of the BoundingBox

        Returns
        -------
        min_y, max_y : tuple[int, int]
            The minimum and maximum y values.
        """
        y_vals: list[int] = self.get_y_vals()
        min_y: int = np.amin(y_vals)
        max_y: int = np.amax(y_vals)

        return min_y, max_y

    def get_x_avg(self) -> int:
        """
        Gets the average x coordinate of the bounding box.

        Returns
        -------
        average : int
            the average of the 4 coordinates' x-values
        """
        return int(np.mean(self.get_x_vals()))

    def get_y_avg(self) -> int:
        """
        Gets the average y coordinate of the bounding box.

        Returns
        -------
        average : int
            the average of the 4 coordinates' y-values
        """
        return int(np.mean(self.get_y_vals()))

    def get_center_coord(self) -> tuple[int, int]:
        """
        Gets the coordinate of the center of the BoundingBox

        Returns
        -------
        center_pt : tuple[int, int]
            the coordinate point at the center of the bounding box
        """
        return (self.get_x_avg(), self.get_y_avg())

    def get_rotation_angle(self) -> float:
        """
        Calculates the angle of rotation of the BoundingBox
        based on the top left and right coordinates.

        Returns
        -------
        angle : float
            The angle of rotation of the BoundingBox in degrees.
        """
        tl_x: int = self.vertices[0][0]
        tr_x: int = self.vertices[1][0]
        tl_y: int = self.vertices[0][1]
        tr_y: int = self.vertices[1][1]

        angle: float = 0
        if tr_x - tl_x == 0:  # prevent division by 0
            angle = 90.0 if (tr_y - tl_y > 0) else -90.0
        else:
            angle = np.rad2deg(np.arctan((tr_y - tl_y) / (tr_x - tl_x)))

        return angle

    def get_width(self) -> int:
        """
        Get the width of the BoundingBox.

        Returns
        -------
        width: int
            the width of the BoundingBox based on max and min x values.
        """
        min_x: int
        max_x: int
        min_x, max_x = self.get_x_extremes()
        width: int = max_x - min_x

        return width

    def get_height(self) -> int:
        """
        Get the height of the BoundingBox.

        Returns
        -------
        height: int
            the height of the BoundingBox based on max and min x values.
        """
        min_y: int
        max_y: int
        min_y, max_y = self.get_y_extremes()
        height: int = max_y - min_y

        return height

    def get_width_height(self) -> tuple[int, int]:
        """
        Gets the width and height of the BoundingBox.

        Returns
        -------
        (width, height) : tuple[int, int]
            the width and height of the bounding box
        """
        return self.get_width(), self.get_height()

    def get_tlwh(self) -> tuple[int, int, int, int]:
        """
        Gets the BoundingBox formatted with top left coordinate, width, and height.

        Returns
        -------
        tlwh_coord : tuple[int, int, int, int]
            the bounding box in top left, width, height format

            tl_x : int
                the top-left x coordinate of the bounding box
            tl_y : int
                the top-left y coordinate of the bounding box
            width : int
                the width of the bounding box
            height : int
                the height of the bounding box
        """
        tl_x: int = self.vertices[0][0]
        tl_y: int = self.vertices[0][1]
        width: int = self.get_width()
        height: int = self.get_height()

        return tl_x, tl_y, width, height


# Driver for testing functionality of BoundingBox object
if __name__ == "__main__":
    coordinates: Vertices = (
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    )
    object_type: ObjectType = ObjectType.STD_OBJECT
    object_attributes: dict[str, Any] = {"shape": "triangle", "latitude": 89.9}

    # constructor
    object_bounds = BoundingBox(
        vertices=coordinates, obj_type=object_type, attributes=object_attributes
    )

    # repr
    print(object_bounds)

    # vertices
    print("Vertices:", object_bounds.vertices)

    # object type
    print("Object Type:", object_bounds.obj_type)

    # various ways to interact with attributes
    print("Attributes:", object_bounds.attributes)
    print("Shape Attribute:", object_bounds.attributes["shape"])

    object_bounds.set_attribute("longitude", 120.3)
    print("Longitude Attribute:", object_bounds.get_attribute("longitude"))

    object_bounds.attributes["altitude"] = 50
    print("Altitude Attribute:", object_bounds.attributes["altitude"])

    # values, extremes, average
    print()
    print("X values:", object_bounds.get_x_vals())
    print("Y values:", object_bounds.get_y_vals())
    print("X extremes:", object_bounds.get_x_extremes())
    print("Y extremes:", object_bounds.get_y_extremes())
    print("X average:", object_bounds.get_x_avg())
    print("Y average:", object_bounds.get_y_avg())

    # center and rotation
    print()
    print("Center coordinate:", object_bounds.get_center_coord())
    print("Rotation angle:", object_bounds.get_rotation_angle())
