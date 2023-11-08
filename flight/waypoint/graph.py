"""Defines a graph node class"""
from typing import Generic, TypeVar

ValueT = TypeVar("ValueT")
WeightT = TypeVar("WeightT")


class GraphNode(Generic[ValueT, WeightT]):
    """
    A node in a graph.

    Attributes
    ----------
    value : ValueT
        The value associated with this node.
    edges: dict[ValueT, WeightT]
        Weights of outgoing edges to other nodes.
    visitor: GraphNode[ValueT, WeightT] | None
        A value that can be used to indicate the node that visited this node
        when performing a search. Defaults to None.
    """

    def __init__(self, value: ValueT) -> None:
        """
        Initialize a new graph node.

        Parameters
        ----------
        value : ValueT
            The value to associate with this node.
        """
        self.value: ValueT = value
        self.edges: dict["GraphNode[ValueT, WeightT]", WeightT] = {}
        self.visitor: "GraphNode[ValueT, WeightT] | None" = None

    # Somewhat hacky methods that make this work in a dict/set

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, rhs: object) -> bool:
        return self is rhs

    def connect(self, node: "GraphNode[ValueT, WeightT]", weight: WeightT) -> None:
        """
        Create an edge between this node andGraphNode another node.

        Parameters
        ----------
        node : GraphNode[ValueT, WeightT]
            The other node.
        weight: WeightT
            The weight to give to the edge.
        """
        self.edges[node] = weight
        node.edges[self] = weight

    def disconnect(self, node: "GraphNode[ValueT, WeightT]") -> bool:
        """
        Remove an edge between this node and another node.

        Parameters
        ----------
        node : GraphNode[ValueT, WeightT]
            The other node.

        Returns
        ------
        bool
            True if the nodes were disconnected, False if they weren't
            connected before.
        """
        try:
            del self.edges[node]
            del node.edges[self]
            return True
        except KeyError:
            return False
