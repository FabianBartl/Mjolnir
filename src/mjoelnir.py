
import matplotlib.pyplot as plt
import networkx as nx
import geocoder
import os
from pprint import pprint
from copy import deepcopy
from geopy.geocoders import Nominatim
from pathlib import Path
from typing import Callable, Iterator, Any, Optional
from collections import namedtuple


def read_koenig_graph(path:str|Path, *, encoding:str="utf-8") -> nx.Graph:
    file = open(path, "r", encoding=encoding)
    
    graph = nx.Graph()
    node_count = 0

    line_num = 0
    for i, line in enumerate(file.readlines()):
        line = line.strip()
        # skip comments and empty lines
        if line.startswith("#") or line == "":
            continue

        # part 1: node count
        if line_num == 0:
            node_count = int(line)
            print(f"{node_count=}")
        
        # part 2: list of node names
        elif 1 <= line_num <= node_count:
            node_id = line_num - 1
            node_name = line
            graph.add_node(node_id, name=node_name, node_id=node_id)
            print(f"add node: {node_id=} {node_name=}")

        # part 3: list of weighted edges
        else:
            parts = [ int(p) for p in line.split(" ") if p != "" and p.isdigit() ]
            if len(parts) == 3:
                node_id_a, node_id_b, weight = parts
                graph.add_edge(node_id_a, node_id_b, weight=weight)
                print(f"add edge: {node_id_a=} {node_id_b=} {weight=}")

        line_num += 1

    file.close()
    return graph


def geo_layout(graph:nx.Graph) -> dict:
    # get (and create) cache file
    cache_filepath = "geodata.cache"
    cache_filemode = "r+" if os.path.isfile(cache_filepath) else "x+"
    cache_file = open(cache_filepath, cache_filemode, encoding="utf-8")

    # load cache file
    cached_geodata = {}
    for line in cache_file.readlines():
        line = line.strip()
        parts = [ p for p in line.split(";") if p != "" ]
        if len(parts) < 3:
            continue
        
        city = parts[0]
        latitude = float(parts[1])
        longitude = float(parts[2])
        cached_geodata[city] = (latitude, longitude)
        print(f"load cached geodata: {city=} {latitude=} {longitude=}")

    # extend cache file
    geolocator = Nominatim(user_agent="mjölnir")
    for node_id, node_data in graph.nodes(data=True):
        city = node_data.get("name")
        if city in cached_geodata.keys():
            continue
        
        location = geolocator.geocode(city, exactly_one=True)
        latitude, longitude = location.latitude, location.longitude

        cached_geodata[city] = (latitude, longitude)
        cache_file.write(f"{city};{latitude};{longitude}\n")
        print(f"extend cached geodata: {node_id=} {city=} {latitude=} {longitude=}")

    # create position dict
    node_positions = {}
    for node_id, node_data in graph.nodes(data=True):
        node_name = node_data.get("name")
        node_positions[node_id] = cached_geodata[node_name][::-1]
        print(f"use node position: {node_id=} {node_name=} pos={node_positions[node_id]}")

    cache_file.close()
    return node_positions


def draw(graph:nx.Graph, *, layout:Callable=nx.kamada_kawai_layout, save_to:str|Path=Optional) -> None:
    pos = layout(graph)

    edge_colors = nx.get_edge_attributes(graph, "color", "orange").values()
    nx.draw_networkx_edges(graph, pos, width=2, alpha=0.8, edge_color=edge_colors)

    edge_labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=6)

    nx.draw_networkx_nodes(graph, pos, node_size=30, alpha=1, node_color="red")

    node_labels = nx.get_node_attributes(graph, "name")
    pos_shifted = { key: (item[0], item[1]+0.1) for key, item in pos.items() }
    nx.draw_networkx_labels(graph, pos_shifted, node_labels, font_size=10)

    if not save_to is Optional:
        plt.savefig(save_to, dpi=500)
    plt.show()


def dijkstra(graph:nx.Graph, start_node_name:str, end_node_name:str) -> list[str]:
    # use deep copy of given graph, delete at the end
    graph = deepcopy(graph)

    # find corresponding node ids
    start_node_id = None
    end_node_id = None

    for node_id, node_data in graph.nodes(data=True):
        node_name = node_data.get("name")

        if node_name == start_node_name:
            start_node_id = node_id
        if node_name == end_node_name:
            end_node_id = node_id
    
    print(f"{start_node_id=} {start_node_name=}")
    print(f"{end_node_id=} {end_node_name=}")

    # init default node attributes: distance=inf, visited=False, successor=None
    inf = float("inf")
    node_route = []

    for node_id, node_data in graph.nodes(data=True):
        nx.set_node_attributes(graph, inf, name="distance")
        nx.set_node_attributes(graph, False, name="visited")
        nx.set_node_attributes(graph, None, name="successor")

    # dijkstra algorithm
    # iterate over neighbors
    neighbors = list( graph.neighbors(start_node_id) )
    for neighbor in neighbors:
        weights = nx.get_edge_attributes(graph, "weight")
        weight = weights[ (start_node_id,neighbor) if (start_node_id,neighbor) in weights else (neighbor,start_node_id) ]
        nx.set_node_attributes(graph, {neighbor: weight}, name="distance")

        # todo

        print(f"{neighbor=} {weight=}")

    del graph
    return []


