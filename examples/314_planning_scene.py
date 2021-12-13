from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene

from compas.geometry import Frame
from compas.geometry import Transformation

with RosClient('localhost') as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)

    collision_meshes = []
    attached_collision_meshes = []

    configuration = robot.zero_configuration()
    scene = robot.client.get_planning_scene()

    for co in scene.world.collision_objects:
        header = co.header
        frame_id = header.frame_id
        cms = co.to_collision_meshes()

        for cm in cms:
            if cm.frame != Frame.worldXY():
                t = Transformation.from_frame(cm.frame)
                mesh = cm.mesh.transformed(t)
            else:
                mesh = cm.mesh

            collision_meshes.append(mesh)

        for aco in scene.robot_state.attached_collision_objects:
            # Noetic compat fix
            if 'pose' in aco.object:
                del aco.object['pose']

            for acm in aco.to_attached_collision_meshes():
                frame_id = aco.object['header']['frame_id']
                frame = robot.forward_kinematics(configuration, options=dict(link=frame_id))
                t = Transformation.from_frame(frame)

                # Local CM frame
                if acm.collision_mesh.frame and acm.collision_mesh.frame != Frame.worldXY():
                    t = t * Transformation.from_frame(acm.collision_mesh.frame)

                mesh = acm.collision_mesh.mesh.transformed(t)

                attached_collision_meshes.append(mesh)

    print('Found {} collision meshes and {} attached collision meshes in the scene'.format(
        len(collision_meshes),
        len(attached_collision_meshes)
    ))
