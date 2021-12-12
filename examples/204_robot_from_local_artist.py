import compas
from compas.artists import Artist
from compas.robots import LocalPackageMeshLoader
from compas.robots import RobotModel

# Set high precision to import meshes defined in meters
compas.PRECISION = '12f'

# Prepare mesh loading from local folder
loader = LocalPackageMeshLoader('models', 'ur_description')

# Create robot model from URDF
model = RobotModel.from_urdf_file(loader.load_urdf('ur5.urdf'))

# Also load geometry
model.load_geometry(loader)

# Draw model
artist = Artist(model)
artist.draw_visual()
artist.redraw()
