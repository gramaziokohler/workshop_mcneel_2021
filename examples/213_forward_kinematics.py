import os

from compas.robots import LocalPackageMeshLoader
from compas.robots import RobotModel

models_path = os.path.join(os.path.dirname(__file__), 'models')
loader = LocalPackageMeshLoader(models_path, 'ur_description')
model = RobotModel.from_urdf_file(loader.load_urdf('ur5.urdf'))

# Get some relevant link names for FK
print(model.get_base_link_name())
print(model.get_end_effector_link_name())

# Create config
config = model.zero_configuration()

# Get FK for tip
print (model.forward_kinematics(config))
# Get FK for base
print (model.forward_kinematics(config, link_name=model.get_base_link_name()))
