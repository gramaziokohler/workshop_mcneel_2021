import os
from compas.geometry import Frame
from compas.robots import Configuration
from compas.robots import LocalPackageMeshLoader
from compas.robots import RobotModel

from compas_fab.backends.kinematics.solvers import UR5Kinematics

models_path = os.path.join(os.path.dirname(__file__), 'models')
loader = LocalPackageMeshLoader(models_path, 'ur_description')
model = RobotModel.from_urdf_file(loader.load_urdf('ur5.urdf'))

f = Frame((0.417, 0.191, -0.005), (-0.000, 1.000, 0.00), (1.000, 0.000, 0.000))

for jv in UR5Kinematics().inverse(f):
    print(Configuration.from_revolute_values(jv))
