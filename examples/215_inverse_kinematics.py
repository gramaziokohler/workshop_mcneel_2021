from compas.geometry import Frame
from compas.robots import Configuration

from compas_fab.robots.ur5 import Robot
from compas_fab.backends.kinematics import AnalyticalInverseKinematics

robot = Robot()
kin = AnalyticalInverseKinematics(solver="ur5")

f = Frame((0.417, 0.191, -0.005), (-0.000, 1.000, 0.000), (1.000, 0.000, 0.000))

for jv, jn in kin.inverse_kinematics(robot, f):
    print(Configuration.from_revolute_values(jv, jn))
