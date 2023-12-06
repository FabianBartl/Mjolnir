
import matplotlib.pyplot as plt
import networkx as nx
import geocoder
from pprint import pprint
from geopy.geocoders import Nominatim
from pathlib import Path
from typing import Callable, Iterator, Any, Optional
from collections import namedtuple


def read_koenig_graph(path:str|Path, *, encoding:str="utf-8") -> nx.Graph:
    file = open(path, "r", encoding=encoding)
    lines = file.readlines()
    
    graph = nx.Graph()
    node_count = 0

    line_num = 0
    for i, line in enumerate(lines):
        line = line.strip()
        # skip comments and empty line
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
            graph.add_node(node_id, name=node_name)
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
    cache_file = open("geodata.cache", "r+", encoding="utf-8")
    geolocator = Nominatim(user_agent="mjölnir")

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

    nx.draw_networkx_edges(graph, pos, width=2, alpha=0.8, edge_color="orange")

    edge_weights = nx.get_edge_attributes(graph, "weight")
    edge_labels = { edge: edge_weights[edge] for edge in edge_weights }
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=6)

    nx.draw_networkx_nodes(graph, pos, node_size=30, alpha=1, node_color="red")

    node_names = nx.get_node_attributes(graph, "name")
    node_labels = { node: node_names[node] for node in node_names }
    pos_shifted = { key: (item[0], item[1]+0.1) for key, item in pos.items() }
    nx.draw_networkx_labels(graph, pos_shifted, node_labels, font_size=10)

    if not save_to is Optional:
        plt.savefig(save_to, dpi=500)
    plt.show()
