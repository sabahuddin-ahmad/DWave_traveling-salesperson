# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

## ------- import packages -------
import networkx as nx
import dimod

import matplotlib.pyplot as plt

# TODO:  Import your sampler
from dwave.samplers import SimulatedAnnealingSampler
# TODO:  Import your Traveling Salesperson QUBO generator
from dwave_networkx import traveling_salesperson_qubo

def get_qubo(G, lagrange, n):
    """Returns a dictionary representing a QUBO"""

    # TODO:  Add QUBO construction here
    Q = traveling_salesperson_qubo(G, lagrange)
    offset = 2 * n * lagrange

    return Q, offset


def get_sampler():
    """Returns a sampler"""

    # TODO: Enter your sampler here
    sampler = SimulatedAnnealingSampler()

    return sampler

def draw_graph(G, route=None, filename=None):
    """Draws the graph, optionally with a TSP route, and saves it if filename is provided."""
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(6, 6))

    # Draw the base graph
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", edge_color="gray", font_size=13)

    # Draw edge labels (weights)
    edge_labels = {(u, v): f"{d['weight']}" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)

    if route:
        # Draw arrows for the route
        for i in range(len(route)):
            start = route[i]
            end = route[(i + 1) % len(route)]
            #nx.draw_networkx_edges(G, pos, edgelist=[(start, end)], edge_color="red", width=2, arrowstyle='->', arrows=True)
            offset = 0.1 * (pos[end] - pos[start])  # Slightly move the arrow away from nodes
            nx.draw_networkx_edges(G, pos, edgelist=[(start, end)], edge_color="red", width=2,
                                   arrowstyle='-|>', arrows=True, connectionstyle=f"arc3,rad={0.1}",
                                   min_source_margin=15, min_target_margin=15)

    if filename:
        plt.savefig(filename)
    plt.show()


## ------- Main program -------
if __name__ == "__main__":

    lagrange = 4000
    n = 7
    G = nx.Graph()
    G.add_weighted_edges_from([
        (0, 1, 2230),
        (0, 2, 1631),
        (0, 3, 1566),
        (0, 4, 1346),
        (0, 5, 1352),
        (0, 6, 1204),
        (1, 2, 845),
        (1, 3, 707),
        (1, 4, 1001),
        (1, 5, 947),
        (1, 6, 1484),
        (2, 3, 627),
        (2, 4, 773),
        (2, 5, 424),
        (2, 6, 644),
	(3, 4, 302),
	(3, 5, 341),
	(3, 6, 1027),
	(4, 5, 368),
	(4, 6, 916),
	(5, 6, 702)
    ])

    # Visualize and save the original graph
    draw_graph(G, filename="original_graph_simulated.png")

    Q, offset = get_qubo(G, lagrange, n)
    sampler = get_sampler()
    bqm = dimod.BinaryQuadraticModel.from_qubo(Q, offset=offset)
    response = sampler.sample(bqm, label="Training - TSP")

    start = None
    sample = response.first.sample
    cost = response.first.energy
    route = [None] * n

    for (city, time), val in sample.items():
        if val:
            route[time] = city

    if start is not None and route[0] != start:
        # rotate to put the start in front
        idx = route.index(start)
        route = route[-idx:] + route[:-idx]

    if None not in route:
        print("Route: ",route)
        print("Cost: ",cost)

        # Visualize and save the TSP route
        draw_graph(G, route=route, filename="tsp_route_simulated.png")
