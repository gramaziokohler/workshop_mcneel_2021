from helpers import draw_directed_edges

from compas.artists import Artist
from compas.datastructures import Network

n = Network()

n.add_edge(1, 2)
n.add_edge(1, 3)
n.add_edge(1, 5)
n.add_edge(1, 7)

n.add_edge(2, 4)
n.add_edge(2, 6)
n.add_edge(2, 10)

n.add_edge(3, 6)
n.add_edge(3, 9)

n.add_edge(4, 8)

n.add_edge(5, 10)

print(n.summary())

visited = set()

def layout(node, y=1):
    if node in visited: return
    visited.add(node)

    nodes_in_row = list(n.nodes_where({'y': y}))
    n.node_attributes(node, 'xyz', [len(nodes_in_row), y, 0])

    for nb in n.neighbors_out(node):
        layout(nb, y+1)

root = 1
layout(root)

artist = Artist(n, layer='network')
artist.clear_layer()
artist.draw_nodelabels(text='key')

if __file__ != '<stdin>':
    draw_directed_edges(artist, n)
artist.redraw()

