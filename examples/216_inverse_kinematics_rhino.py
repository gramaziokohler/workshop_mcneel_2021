from compas.artists import Artist
from compas.geometry import Frame
from compas_fab.robots.ur5 import Robot
from compas_fab.backends.kinematics import AnalyticalInverseKinematics

robot = Robot()
kin = AnalyticalInverseKinematics(solver="ur5")

f = Frame((0.417, 0.191, -0.005), (-0.000, 1.000, 0.000), (1.000, 0.000, 0.000))

artist = Artist(robot.model, layer='IK')

for jv, _ in kin.inverse_kinematics(robot, f):
    config = robot.model.zero_configuration()
    config.joint_values = jv
    artist.update(config)
    artist.draw_visual()
    artist.redraw(1)
    artist.clear_layer()
