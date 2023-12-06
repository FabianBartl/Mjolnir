
import matplotlib.pyplot as plt
import networkx as nx

import os
from pathlib import Path
from typing import Callable, Iterator, Any, Optional


class Node:
    def __init__(self, unique_name:str, **data) -> None:
        if not isinstance(unique_name, str):
            raise TypeError(f"{unique_name=} is not of type str")
        self.name = str(unique_name)

        self.data = data


class Edge:
    def __init__(self, start_node:Node, end_node:Node, *, weight:float|int=1, **data) -> None:
        if not isinstance(start_node, Node):
            raise TypeError(f"{start_node=} is not of type Node")
        if not isinstance(end_node, Node):
            raise TypeError(f"{end_node=} is not of type Node")
        self.start_node = start_node
        self.end_node = end_node

        if not isinstance(weight, float) or not isinstance(weight, int):
            raise TypeError(f"{weight=} is not of type float or int")
        self.weight = weight

        self.data = data


class Graph:
    def __init__(self, *, path:str|Path=None, format:str=None) -> None:
        if not isinstance(path, str) or not isinstance(path, Path):
            raise TypeError(f"{path=} is not of type str or Path")

        if format == "custom":
            self.read_custom(path)
        elif format == "adjacency-list":
            self.read_adjacency_list(path)
        elif format == "adjacency-matrix":
            self.read_adjacency_matrix(path)
        else:
            raise ValueError(f"selected {format=} is not supported")
        
        self.__nodes_dict = {}
        self.__edges_list = []
    
    def __read_custom(self, path:str):
        pass
    def __read_adjacency_list(self, path:str):
        pass
    def __read_adjacency_matrix(self, path:str):
        pass

    def get_nodes(self) -> dict[str: Node]:
        return { node.name: node for node in self.__nodes_dict }
    def get_edges(self) -> list[Edge]:
        return self.__edges_list
    
    def add_node(self, unique_name:str, *, raise_error:bool=False, **data) -> bool:
        if not isinstance(unique_name, str):
            raise TypeError(f"{unique_name} is not of type str")

        if str(unique_name) in self.__nodes_dict:
            if raise_error:
                raise ValueError(f"a node with this {unique_name=} already exists")
            else:
                return False
        
        self.__nodes_dict[unique_name] = Node(unique_name, **data)
        return True

    def add_edge(self, start_node_name:str, end_node:Node, *, weight:float|int=1, raise_error:bool=False, **data) -> bool:
        if not isinstance(start_node, Node):
            raise TypeError(f"{start_node} is not of type Node")
        if not isinstance(end_node, Node):
            raise TypeError(f"{end_node} is not of type Node")

        if not start_node.name in self.__nodes_dict:
            raise 
        
        self.__nodes_dict[unique_name] = Node(unique_name, **data)
        return True

