import math
import os
import bpy

os.makedirs("build/frames", exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 60 seconds at 15 fps = 900 frames (1080x1920 9:16 vertical)
FPS = 15
DURATION_SEC = 60
TOTAL_FRAMES = FPS * DURATION_SEC

scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = TOTAL_FRAMES

# Fast Workbench engine with flat/studio lighting for reliable headless rendering
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = os.path.abspath("build/frames/frame_")


def make_mat(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat


# Grass field
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
grass = bpy.context.active_object
grass.name = "Grass"
grass.data.materials.append(make_mat("GrassMat", (0.20, 0.58, 0.16, 1.0)))

# Straight road
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.02))
road = bpy.context.active_object
road.scale = (8.0, 200.0, 0.04)
road.data.materials.append(make_mat("RoadMat", (0.12, 0.13, 0.16, 1.0)))

# Road center line
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.05))
line = bpy.context.active_object
line.scale = (0.22, 200.0, 0.02)
line.data.materials.append(make_mat("LineMat", (0.98, 0.80, 0.10, 1.0)))

# Tree (trunk + foliage; shrinks to stump after frame 540 / 36s)
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=4.5, location=(5.5, 10.0, 2.25))
trunk = bpy.context.active_object
trunk.name = "TreeTrunk"
trunk.data.materials.append(make_mat("TrunkMat", (0.38, 0.22, 0.10, 1.0)))

bpy.ops.mesh.primitive_icosphere_add(subdivisions=2, radius=2.7, location=(5.5, 10.0, 5.4))
foliage = bpy.context.active_object
foliage.name = "TreeFoliage"
foliage.data.materials.append(make_mat("LeafMat", (0.14, 0.65, 0.20, 1.0)))

# Keyframe tree chopping down at 36s (frame 540) -> stump (frame 555+)
trunk.scale = (1.0, 1.0, 1.0)
trunk.keyframe_insert(data_path="scale", frame=1)
trunk.keyframe_insert(data_path="scale", frame=540)
trunk.scale = (1.1, 1.1, 0.22)
trunk.keyframe_insert(data_path="scale", frame=555)

foliage.scale = (1.0, 1.0, 1.0)
foliage.keyframe_insert(data_path="scale", frame=1)
foliage.keyframe_insert(data_path="scale", frame=540)
foliage.scale = (0.001, 0.001, 0.001)
foliage.keyframe_insert(data_path="scale", frame=550)

# Stickman character standing near the roadside/tree and reacting
stick_root = bpy.data.objects.new("StickmanRoot", None)
scene.collection.objects.link(stick_root)
stick_root.location = (3.6, 7.5, 0.0)

black_mat = make_mat("StickBlack", (0.05, 0.05, 0.06, 1.0))

# Head
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.32, location=(0, 0, 2.15))
head = bpy.context.active_object
head.parent = stick_root
head.data.materials.append(black_mat)

# Torso
bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.09, depth=1.1, location=(0, 0, 1.3))
torso = bpy.context.active_object
torso.parent = stick_root
torso.data.materials.append(black_mat)

# Left & Right Legs
for side, name in [(-0.18, "LegL"), (0.18, "LegR")]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=0.85, location=(side, 0, 0.42))
    leg = bpy.context.active_object
    leg.name = name
    leg.parent = stick_root
    leg.data.materials.append(black_mat)

# Left & Right Arms
for side, name in [(-0.35, "ArmL"), (0.35, "ArmR")]:
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.065, depth=0.75, location=(side, 0, 1.55))
    arm = bpy.context.active_object
    arm.name = name
    arm.parent = stick_root
    arm.rotation_euler = (0.0, side * 1.4, 0.0)
    arm.data.materials.append(black_mat)

# Animate stickman subtle wave/jump
for f in range(1, TOTAL_FRAMES + 1, 15):
    stick_root.location = (3.6, 7.5, 0.15 if (f // 15) % 2 == 1 else 0.0)
    stick_root.keyframe_insert(data_path="location", frame=f)

# Car that loops down the road and drifts toward the tree/stump
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.8, -30.0, 0.75))
car = bpy.context.active_object
car.name = "Car"
car.scale = (2.2, 4.5, 1.2)
car.data.materials.append(make_mat("CarMat", (0.92, 0.94, 0.97, 1.0)))

for cycle_start in range(1, TOTAL_FRAMES, 180):
    cycle_end = min(cycle_start + 179, TOTAL_FRAMES)
    mid = cycle_start + (cycle_end - cycle_start) // 2
    car.location = (1.8, -35.0, 0.75)
    car.keyframe_insert(data_path="location", frame=cycle_start)
    car.location = (2.6, -10.0, 0.75)
    car.keyframe_insert(data_path="location", frame=mid)
    car.location = (4.8, 9.0, 0.75)
    car.keyframe_insert(data_path="location", frame=cycle_end)

# Camera with dynamic cuts across the 60 seconds
bpy.ops.object.camera_add(location=(0.0, -22.0, 12.0))
cam = bpy.context.active_object
scene.camera = cam

cuts = [
    (1, (0.0, -22.0, 12.0), (0.85, 0.0, 0.0)),
    (150, (7.5, 14.0, 2.4), (1.35, 0.0, 2.75)),
    (300, (1.5, -18.0, 3.2), (1.25, 0.0, 0.0)),
    (450, (6.2, 4.5, 2.0), (1.40, 0.0, 2.40)),
    (600, (-4.0, 2.0, 5.5), (1.15, 0.0, -0.75)),
    (750, (0.0, -16.0, 8.0), (1.05, 0.0, 0.0)),
]
for frame_num, loc, rot in cuts:
    cam.location = loc
    cam.rotation_euler = rot
    cam.keyframe_insert(data_path="location", frame=frame_num)
    cam.keyframe_insert(data_path="rotation_euler", frame=frame_num)

bpy.ops.render.render(animation=True)
