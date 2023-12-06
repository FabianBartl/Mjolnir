
from time import time
import mjoelnir as mj

path = "../data/zentral.txt"
G = mj.read_koenig_graph(path)
mj.draw(G, layout=mj.geo_layout)

route = mj.dijkstra(G, "Berlin", "Frankfurt/Main")
# print(route)
