import os

import compas
from compas.geometry import Frame
from compas.robots import Configuration

from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene
import helpers

HERE = os.path.dirname(__file__)

# Load assembly
filename = os.path.join(HERE, 'assembly.json')
assembly = compas.json_load(filename)

with RosClient() as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)

    # create tool from mesh and frame
    helpers.attach_demo_vacuum_gripper(scene)

    # Assign pick frame based on tool
    pick_frame = Frame((0.300, 0.520, 0.032), (1.000, 0.000, 0.000), (0.000, 1.000, 0.000))
    pick_t0cf_frame = robot.from_tcf_to_t0cf([pick_frame])[0]

    # # Remove the tool
    # scene.remove_attached_tool()
    # scene.remove_collision_mesh('attached_tool_link_collision_0')
    # robot.detach_tool()

    assembly.pick_t0cf_frame = pick_t0cf_frame
    assembly.approach_offset = 0.060
    assembly.attributes['home_config'] = Configuration((1.354, -0.810, -0.03, -0.544), (0, 0, 2, 0), ('joint1', 'joint2', 'joint3', 'joint4'))
    assembly.attributes['place_tolerance'] = 0.001

    # Save assembly
    compas.json_dump(assembly, filename, pretty=True)
