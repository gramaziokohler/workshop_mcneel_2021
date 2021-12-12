from matplotlib import pyplot as plt

import compas.datastructures
import compas.geometry
from compas.artists import Artist

# Make sure matplotlib's based plotter does not block when we show it on CI
plt.ion()


# Register a mock artist for testing
class MockArtist(Artist):
    def draw(self):
        pass
    def draw_mesh(self, *args, **kwargs):
        pass
    def draw_faces(self, *args, **kwargs):
        pass
    def draw_vertexnormals(self, *args, **kwargs):
        pass
    def draw_nodelabels(self, *args, **kwargs):
        pass
    def draw_nodes(self, *args, **kwargs):
        pass
    def draw_edges(self, *args, **kwargs):
        pass
    def clear_layer(self):
        pass

Artist.register(compas.geometry.Box, MockArtist)
Artist.register(compas.geometry.Sphere, MockArtist)
Artist.register(compas.geometry.Cylinder, MockArtist)
Artist.register(compas.datastructures.Mesh, MockArtist)
Artist.register(compas.datastructures.Network, MockArtist)
