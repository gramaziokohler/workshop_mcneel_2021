import os

import compas
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene
from compas_fab.robots import CollisionMesh

HERE = os.path.dirname(__file__)

with RosClient() as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)

    # Prepare scene for planning
    meshes = compas.json_load(os.path.join(HERE, 'demo-static-objects.json'))
    scene.remove_collision_mesh('static_objects')

    for mesh in meshes:
        cm = CollisionMesh(mesh, 'static_objects')
        scene.append_collision_mesh(cm)
