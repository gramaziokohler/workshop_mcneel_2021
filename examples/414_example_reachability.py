import os
import compas
import compas_fab
from compas.robots import LocalPackageMeshLoader
from compas_fab.robots import Tool
from compas_fab.backends.kinematics.exceptions import InverseKinematicsError
from compas_fab.backends.kinematics.client import AnalyticalPyBulletClient

urdf_filename = compas_fab.get('universal_robot/ur_description/urdf/ur5.urdf')
srdf_filename = compas_fab.get('universal_robot/ur5_moveit_config/config/ur5.srdf')


jsonfile_in = os.path.join(os.path.dirname(__file__), "414_example_reachability_in.json")
jsonfile_out = os.path.join(os.path.dirname(__file__), "414_example_reachability_out.json")
tool_jsonfile = os.path.join(os.path.dirname(__file__), "414_example_reachability_tool.json")
tool = Tool.from_json(tool_jsonfile)

frames_in = compas.json_load(jsonfile_in)
frames_out = []

with AnalyticalPyBulletClient(connection_type='gui') as client:  # direct

    loader = LocalPackageMeshLoader(compas_fab.get('universal_robot'), 'ur_description')
    robot = client.load_robot(urdf_filename, [loader])
    client.load_semantics(robot, srdf_filename)
    robot.attach_tool(tool)
    # this is not really nice.. 
    client.disabled_collisions.add(('wrist_3_link', robot.attached_tool.attached_collision_meshes[0].collision_mesh.id))

    for frame in frames_in:
        frame_t0cf = robot.from_tcf_to_t0cf([frame])[0]
        options = {"solver": "ur5", "check_collision": True, "keep_order": True}
        ik_index = 2
        
        try:
            configurations = list(robot.iter_inverse_kinematics(frame_t0cf, options=options))
            if configurations[ik_index]:
                frames_out.append(frame)
        except InverseKinematicsError:
            pass
        

compas.json_dump(frames_out, jsonfile_out)
