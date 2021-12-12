from compas.artists import Artist
from compas.robots import LocalPackageMeshLoader
from compas.robots import RobotModel

loader = LocalPackageMeshLoader('models', 'ur_description')
model = RobotModel.from_urdf_file(loader.load_urdf('ur5.urdf'))
model.load_geometry(loader)

config = model.zero_configuration()
frame = model.forward_kinematics(config)

artist = Artist(frame)
artist.draw()

artist = Artist(model)
artist.update(config)
artist.draw_visual()
