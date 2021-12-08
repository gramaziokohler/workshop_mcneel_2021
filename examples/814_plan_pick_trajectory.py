import os

import helpers
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene

import compas
from compas.geometry import Frame

HERE = os.path.dirname(__file__)
MAX_STEP = 0.01

# Load assembly
filename = os.path.join(HERE, 'assembly.json')
assembly = compas.json_load(filename)

with RosClient() as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)
    home_config = assembly.attributes['home_config']

    trajectory = robot.plan_cartesian_motion(assembly.pick_t0cf_frames(),
                                             start_configuration=assembly.attributes['home_config'],
                                             options=dict(max_step=MAX_STEP))

    print("Computed cartesian path with %d configurations, " % len(trajectory.points))
    print("following %d%% of requested trajectory." % (trajectory.fraction * 100))
    print("Executing this path at full speed would take approx. %.3f seconds." % trajectory.time_from_start)

    if trajectory and trajectory.fraction < 1.0:
        raise Exception('Incomplete trajectory. Fraction={}'.format(trajectory.fraction))

    assembly.pick_trajectory = trajectory

# Save assembly
compas.json_dump(assembly, filename, pretty=True)
