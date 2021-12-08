from compas.artists import Artist
from compas.robots import RobotModel

model = RobotModel.from_urdf_file('models/05_with_colors.urdf')

artist = Artist(model)
artist.draw_visual()
artist.redraw()