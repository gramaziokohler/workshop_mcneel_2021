import random

import compas
from compas.artists import Artist
from compas.datastructures import Mesh
from compas.geometry import Cylinder
from compas.utilities import flatten

mesh = Mesh.from_off(compas.get('tubemesh.off'))

start = random.choice(list(mesh.edges()))
loop = mesh.edge_loop(start)
strip = [mesh.edge_faces(*edge) for edge in mesh.edge_strip(start)]
strip[:] = list(set(flatten(strip)))

edgecolor = {}
for edge in loop:
    edgecolor[edge] = (0, 255, 0)

edgecolor[start] = (255, 0, 0)

facecolor = {}
for face in strip:
    facecolor[face] = (255, 200, 200)

artist = Artist(mesh, layer='Tubemesh')
artist.clear_layer()
artist.draw_faces(color=facecolor)

for edge in edgecolor:
    o = mesh.edge_midpoint(*edge)
    n = mesh.edge_direction(*edge)
    h = mesh.edge_length(*edge)

    cylinder = Cylinder([(o, n), 0.02], h)
    artist = Artist(cylinder, color=(0, 255, 0), layer='Tubemesh')
    artist.draw()
