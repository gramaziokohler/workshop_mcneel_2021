from __future__ import print_function

import math
import os
import time
from functools import partial

import compas_rhino
from compas_fab.robots import AttachedCollisionMesh
from compas_fab.robots import CollisionMesh
from compas_fab.robots import Tool

import compas
from compas.datastructures import Mesh
from compas.geometry import Frame
from compas.robots import Configuration
from compas.topology import breadth_first_ordering
from compas.topology import breadth_first_traverse
from compas.utilities import color_to_colordict

HERE = os.path.dirname(__file__)
Z_OFFSET = 0.070
COLORDICT = partial(color_to_colordict, colorformat='rgb', normalize=False)


class Rate(object):
    def __init__(self, hz):
        self.hz = hz
        self.last_time = time.time_ns()
        self.sleep_duration = int(1e9 / hz)

    def sleep(self):
        t1 = time.time_ns()
        elapsed = t1 - self.last_time
        sleep_ns = (self.sleep_duration - elapsed)
        if sleep_ns > 0:
            time.sleep(sleep_ns / 1e9)
        self.last_time = self.last_time + self.sleep_duration


def show_trajectory(trajectory):
    import matplotlib.pyplot as plt

    # visualise
    positions = []
    velocities = []
    accelerations = []
    time_from_start = []

    for p in trajectory.points:
        positions.append(p.positions)
        velocities.append(p.velocities)
        accelerations.append(p.accelerations)
        time_from_start.append(p.time_from_start.seconds)

    plt.rcParams['figure.figsize'] = [17, 4]
    plt.subplot(131)
    plt.title('positions')
    plt.plot(positions)
    plt.subplot(132)
    plt.plot(velocities)
    plt.title('velocities')
    plt.subplot(133)
    plt.plot(accelerations)
    plt.title('accelerations')
    plt.show()


def plan_picking_motion(robot, picking_frame, safelevel_picking_frame, start_configuration, attached_element_mesh):
    """Returns a cartesian trajectory to pick an element.

    Parameters
    ----------
    robot : :class:`compas.robots.Robot`
    picking_frame : :class:`Frame`
    safelevel_picking_frame : :class:`Frame`
    start_configuration : :class:`Configuration`
    attached_element_mesh : :class:`AttachedCollisionMesh`

    Returns
    -------
    :class:`JointTrajectory`
    """

    # Calculate frames at tool0 and picking_configuration
    frames = [picking_frame, safelevel_picking_frame]
    frames_tool0 = robot.from_tcf_to_t0cf(frames)

    picking_frame_tool0 = robot.from_tcf_to_t0cf([picking_frame])[0]
    picking_configuration = robot.inverse_kinematics(picking_frame_tool0, start_configuration)

    picking_trajectory = robot.plan_cartesian_motion(frames_tool0,
                                                     picking_configuration,
                                                     options=dict(
                                                        max_step=0.01,
                                                        attached_collision_meshes=[attached_element_mesh]
                                                     ))
    return picking_trajectory



def plan_moving_and_placing_motion(robot, element, start_configuration, tolerance_vector, safelevel_vector, attached_element_mesh):
    """Returns two trajectories for moving and placing an element.

    Parameters
    ----------
    robot : :class:`compas.robots.Robot`
    element : :class:`Element`
    start_configuration : :class:`Configuration`
    tolerance_vector : :class:`Vector`
    safelevel_vector : :class:`Vector`
    attached_element_mesh : :class:`AttachedCollisionMesh`

    Returns
    -------
    list of :class:`JointTrajectory`
    """

    tolerance_position = 0.001
    tolerance_axes = [math.radians(1)] * 3

    target_frame = element._tool_frame.copy()
    target_frame.point += tolerance_vector

    safelevel_target_frame = target_frame.copy()
    safelevel_target_frame.point += safelevel_vector

    # Calculate goal constraints
    safelevel_target_frame_tool0 = robot.from_tcf_to_t0cf(
        [safelevel_target_frame])[0]
    goal_constraints = robot.constraints_from_frame(safelevel_target_frame_tool0,
                                                    tolerance_position,
                                                    tolerance_axes)

    moving_trajectory = robot.plan_motion(goal_constraints,
                                          start_configuration,
                                          options=dict(
                                            planner_id='SBL',
                                            attached_collision_meshes=[attached_element_mesh],
                                            num_planning_attempts=20,
                                            allowed_planning_time=10
                                          ))


    frames = [safelevel_target_frame, target_frame]
    frames_tool0 = robot.from_tcf_to_t0cf(frames)
    # as start configuration take last trajectory's end configuration
    last_configuration = Configuration(moving_trajectory.points[-1].joint_values, moving_trajectory.points[-1].types)


    placing_trajectory = robot.plan_cartesian_motion(frames_tool0,
                                                     last_configuration,
                                                     options=dict(
                                                        max_step=0.01,
                                                        attached_collision_meshes=[attached_element_mesh]
                                                     ))
    return moving_trajectory, placing_trajectory


class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
            self.ansi_support = False
        except ImportError:
            self.impl = _GetchUnix()
            self.ansi_support = True

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import sys
        import tty

    def __call__(self):
        import sys
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.buffer.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

CTRL_CHARS = (8, 9, 13, 27, 127)
__input_context = dict(buffer='')

def get_current_buffer():
    return __input_context['buffer']

def get_input(prompt='> ', end='\n'):
    if prompt:
        print(prompt, end='', flush=True)

    __input_context['buffer'] = ''
    while True:
        c = getch()
        ord_c = ord(c)
        if ord_c in CTRL_CHARS:
            if ord_c == 13:
                # only break if text has content
                if len(__input_context['buffer']) > 0: break
            elif ord_c in (8, 127):
                # only apply backspace if text has content
                if len(__input_context['buffer']) > 0:
                    if getch.ansi_support:
                        print('\033[1D \033[1D', end='', flush=True)
                    else:
                        c = c.decode('ascii')
                        print(c + ' ' + c, end='', flush=True)
                    __input_context['buffer'] = __input_context['buffer'][:-1]
        else:
            c = c.decode('ascii')
            print(c, end='', flush=True)
            __input_context['buffer'] += c

    if end:
        print(end, end='', flush=True)

    return __input_context['buffer']


def draw_directed_edges(artist, edges=None, color=None):
    node_xyz = artist.node_xyz
    edges = edges or list(artist.network.edges())
    edge_color = COLORDICT(color, edges, default=artist.color_edges)
    lines = []
    for edge in edges:
        lines.append({
            'start': node_xyz[edge[0]],
            'end': node_xyz[edge[1]],
            'color': edge_color[edge],
            'arrow': 'end',
            'name': "{}.edge.{}-{}".format(artist.network.name, *edge)})
    return compas_rhino.draw_lines(lines, layer=artist.layer, clear=False, redraw=False)

def traversal_linearly_ordered(assembly):
    return sorted(assembly.nodes())


def traversal_breadth_first_ordering(assembly):
    root = assembly.leaves()[0]
    return breadth_first_ordering(assembly.adjacency, root)


def traversal_buildup_sequence(assembly):
    visited = set()
    elements = []
    for key in assembly.nodes():
        if assembly.degree_out(key) == 0:
            get_dependencies(assembly, key, elements, visited)

    return list(reversed(elements))


def get_dependencies(assembly, key, elements, visited):
    if key not in visited:
        elements.append(key)
        visited.add(key)
    for n in assembly.neighbors_in(key):
        get_dependencies(assembly, n, elements, visited)


def get_last_config(trajectory, robot):
    start_configuration = robot.zero_configuration()

    if trajectory and trajectory.points:
        start_configuration.joint_values = trajectory.points[-1].joint_values

    return start_configuration


def attach_vacuum_gripper(scene):
    # create tool from mesh and frame
    mesh = Mesh.from_stl(os.path.join(HERE, 'vacuum_gripper.stl'))
    frame = Frame([Z_OFFSET, 0, 0], [0, 0, 1], [0, 1, 0])
    tool = Tool(mesh, frame, name='vacuum_gripper')

    scene.robot.attach_tool(tool)
    scene.add_attached_tool()


def attach_demo_vacuum_gripper(scene):
    # create tool from mesh and frame
    vmesh = Mesh.from_stl(os.path.join(HERE, 'vacuum-gripper-visual.stl'))
    cmesh = Mesh.from_stl(os.path.join(HERE, 'vacuum-gripper-collision.stl'))
    frame = Frame([0, 0, -0.04328], [1, 0, 0], [0, 1, 0])
    tool = Tool(visual=vmesh, frame_in_tool0_frame=frame, collision=cmesh)

    scene.robot.attach_tool(tool)
    scene.add_attached_tool()


def add_static_objects(scene, filename='static-objects.json'):
    meshes = compas.json_load(os.path.join(HERE, filename))
    scene.remove_collision_mesh('static_objects')

    for mesh in meshes:
        cm = CollisionMesh(mesh, 'static_objects')
        scene.append_collision_mesh(cm)


def add_built_elements(scene, assembly, built_elements):
    scene.remove_collision_mesh('built_elements')

    for key in built_elements:
        element = assembly.element(key)
        cm = CollisionMesh(element.geometry_at_placement, 'built_elements')
        scene.append_collision_mesh(cm)
        print('.', end='', flush=True)

    # Setup attached element
    scene.remove_attached_collision_mesh('brick')
    scene.remove_collision_mesh('brick')

    ee_link_name = scene.robot.get_end_effector_link_name()
    if scene.robot.attached_tool:
        brick_frame = scene.robot.attached_tool.frame.copy()
    else:
        brick_frame = Frame.worldXY()

    # Centered origin, get half
    element = assembly.attributes['element']
    brick_frame.point.x += element.height / 2
    element_mesh = Mesh.from_shape(element)
    brick_acm = AttachedCollisionMesh(CollisionMesh(element_mesh, 'brick', brick_frame), ee_link_name)
    scene.add_attached_collision_mesh(brick_acm)
