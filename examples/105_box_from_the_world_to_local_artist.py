"""Example: Bring a box from the world coordinate system into another coordinate
system and view in Rhino.
"""
from compas.geometry import Frame
from compas.geometry import Box
from compas.artists import Artist

# Given: box in the world coordinate system
frame = Frame([1, 0, 0], [-0.45, 0.1, 0.3], [1, 0, 0])
width, length, height = 1, 1, 1
box = Box(frame, width, length, height)

# Given: frame F representing a coordinate system
F = Frame([2, 2, 2], [0.978, 0.010, -0.210], [0.090, 0.882, 0.463])

# Task: represent box frame in frame F and construct new box
box_frame_transformed = F.to_world_coordinates(box.frame)
box_transformed = Box(box_frame_transformed, width, length, height)
print("Box frame transformed:", box_transformed.frame)

# create artists
artist1 = Artist(Frame.worldXY())
artist2 = Artist(box)
artist3 = Artist(F)
artist4 = Artist(box_transformed)

# draw
artist1.draw()
artist2.draw()
artist3.draw()
artist4.draw()
