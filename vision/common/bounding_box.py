"""
Bounding box objects represent an area in an image and
are used to convey information between flight and vision processes.
"""

from enum import Enum

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


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
    vertices : Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]
        The main structure of the BoundingBox. Denotes the 4 coordinates
        representing a box in an image. Vertices is a tuple of 4 coordinates. Each
        coordinate consists of a tuple 2 integers.
    obj_type : ObjectType
        Enumeration that denotes what type of object the BoundingBox represents.
    attributes : Optional[Dict[str, Any]]
        Any additional attributes to convey about the object in the BoundingBox.
    """

    def __init__(
        self,
        vertices: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]],
        obj_type: ObjectType,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._vertices: Tuple[
            Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]
        ] = vertices
        self._obj_type: ObjectType = obj_type
        self._attributes: Dict[str, Any] = attributes if attributes is not None else {}

    @property
    def vertices(self) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """
        Getter for _vertices. Gets the 4 vertices that make up the BoundingBox.

        Returns
        -------
        _vertices : Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]
            The 4 coordinates of the BoundingBox.
        """
        return self._vertices

    @vertices.setter
    def vertices(
        self, verts: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]
    ) -> None:
        """
        Setter for _vertices. Sets the 4 vertices that make up the BoundingBox.

        Parameters
        ----------
        vert : Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]
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
    def attributes(self) -> Dict[str, Any]:
        """
        Getter for _attributes. Gets the additional attributes of the BoundingBox.

        Returns
        -------
        _attributes : Dict[str, Any]
            Any additional attributes of the BoundingBox.
        """
        return self._attributes

    @attributes.setter
    def attributes(self, att: Dict[str, Any]) -> None:
        """
        Setter for _attributes. Sets the value of the BoundingBox's additional attributes.

        Parameters
        ----------
        att : Dict[str, Any]
            The additional attributes to assign to the BoundingBox.
        """
        self._attributes = att

    def __repr__(self) -> str:
        """
        Returns a string representation of the BoundingBox
        that contains its id, object type, and vertices.

        Returns
        -------
        str
            The string representation of the BoundingBox object.
        """
        return f"BoundingBox[{id(self)}, {self.obj_type}]: {str(self._vertices)}"

    def get_x_vals(self) -> List[int]:
        """
        Gets the x values of the 4 coordinates.

        Returns
        -------
        x_vals : List[int]
            The 4 x values of the vertices.
        """
        x_vals: List[int] = [vert[0] for vert in self._vertices]
        return x_vals

    def get_y_vals(self) -> List[int]:
        """
        Gets the y values of the 4 coordinates.

        Returns
        -------
        y_vals : List[int]
            The 4 y values of the vertices.
        """
        y_vals: List[int] = [vert[1] for vert in self._vertices]
        return y_vals

    def get_x_extremes(self) -> Tuple[int, int]:
        """
        Gets the minimum and maximum x values of the BoundingBox

        Returns
        -------
        min_x, max_x : Tuple[int, int]
            The minimum and maximum x values.
        """
        x_vals: List[int] = self.get_x_vals()
        min_x: int = np.amin(x_vals)
        max_x: int = np.amax(x_vals)

        return min_x, max_x

    def get_y_extremes(self) -> Tuple[int, int]:
        """
        Gets the minimum and maximum y values of the BoundingBox

        Returns
        -------
        min_y, max_y : Tuple[int, int]
            The minimum and maximum y values.
        """
        y_vals: List[int] = self.get_y_vals()
        min_y: int = np.amin(y_vals)
        max_y: int = np.amax(y_vals)

        return min_y, max_y

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


if __name__ == "__main__":
    pass
