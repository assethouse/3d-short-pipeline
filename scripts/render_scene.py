import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Keep test render fast on free runners (72 frames = 3s at 24fps; bump to 50% or 100% once verified)
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 50
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 72

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 12
scene.cycles.use_denoising = False
scene.cycles.max_bounces = 2
scene.cycles.diffuse_bounces = 1
scene.cycles.glossy_bounces = 1

scene.render.image_settings.file_format = "PNG"
scene.render.filepath = "//build/frames/frame_"


def make_mat(name, color, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


# Sky background (stylized daylight blue)
world = bpy.data.worlds.new("SkyWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.35, 0.62, 0.95, 1.0)
    bg.inputs["Strength"].default_value = 1.0

# Ground fields on left and right
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, -0.02))
field = bpy.context.active_object
field.data.materials.append(make_mat("FieldMat", (0.28, 0.52, 0.18, 1.0), 0.9))

# Straight road
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.01))
road = bpy.context.active_object
road.scale = (7.0, 120.0, 0.04)
road.data.materials.append(make_mat("RoadMat", (0.10, 0.11, 0.14, 1.0), 0.75))

# Center yellow line
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.035))
line = bpy.context.active_object
line.scale = (0.18, 120.0, 0.01)
line.data.materials.append(make_mat("LineMat", (0.98, 0.78, 0.10, 1.0), 0.5))

# Roadside tree trunk + stylized canopy
bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=4.0, location=(5.2, 8.0, 2.0))
trunk = bpy.context.active_object
trunk.data.materials.append(make_mat("TrunkMat", (0.36, 0.21, 0.11, 1.0), 0.85))

bpy.ops.mesh.primitive_icosphere_add(subdivisions=2, radius=2.6, location=(5.2, 8.0, 4.8))
foliage = bpy.context.active_object
foliage.scale = (1.1, 1.1, 0.85)
foliage.data.materials.append(make_mat("LeafMat", (0.16, 0.58, 0.18, 1.0), 0.7))

# Bold red warning beacon/sign post next to tree
bpy.ops.mesh.primitive_cube_add(size=1, location=(4.2, 6.2, 1.6))
sign = bpy.context.active_object
sign.scale = (0.3, 1.4, 2.2)
sign.data.materials.append(make_mat("SignMat", (0.90, 0.12, 0.10, 1.0), 0.4))

# Car body + cabin (stylized low-poly car driving down road, subtly steering toward tree)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.6, -25.0, 0.75))
car = bpy.context.active_object
car.scale = (2.1, 4.4, 1.1)
car.data.materials.append(make_mat("CarMat", (0.88, 0.90, 0.94, 1.0), 0.3))

bpy.ops.mesh.primitive_cube_add(size=1, location=(1.6, -25.3, 1.55))
cabin = bpy.context.active_object
cabin.scale = (1.75, 2.2, 0.85)
cabin.parent = car
cabin.location = (0.0, -0.2, 0.8)
cabin.data.materials.append(make_mat("CabinMat", (0.16, 0.22, 0.30, 1.0), 0.25))

# Animate car from y=-25 toward y=12 and drifting slightly right toward the tree
car.location = (1.6, -25.0, 0.75)
car.keyframe_insert(data_path="location", frame=1)
car.location = (2.4, -5.0, 0.75)
car.keyframe_insert(data_path="location", frame=36)
car.location = (4.3, 6.5, 0.75)
car.keyframe_insert(data_path="location", frame=72)

# Camera with quick cuts: high overview (1-24), low roadside angle (25-48), chase angle (49-72)
bpy.ops.object.camera_add(location=(0.0, -18.0, 14.0))
cam = bpy.context.active_object
scene.camera = cam

# Cut 1: High overview
cam.location = (0.0, -18.0, 14.0)
cam.rotation_euler = (0.78, 0.0, 0.0)
cam.keyframe_insert(data_path="location", frame=1)
cam.keyframe_insert(data_path="rotation_euler", frame=1)

cam.location = (0.0, -8.0, 12.0)
cam.keyframe_insert(data_path="location", frame=24)
cam.keyframe_insert(data_path="rotation_euler", frame=24)

# Cut 2: Roadside view looking back along the road past the tree/sign
cam.location = (6.8, 12.0, 2.2)
cam.rotation_euler = (1.35, 0.0, 2.65)
cam.keyframe_insert(data_path="location", frame=25)
cam.keyframe_insert(data_path="rotation_euler", frame=25)
cam.keyframe_insert(data_path="location", frame=48)
cam.keyframe_insert(data_path="rotation_euler", frame=48)

# Cut 3: Low behind-car chase angle
cam.location = (1.8, -14.0, 3.2)
cam.rotation_euler = (1.25, 0.0, 0.0)
cam.keyframe_insert(data_path="location", frame=49)
cam.keyframe_insert(data_path="rotation_euler", frame=49)
cam.location = (2.8, 1.0, 2.8)
cam.keyframe_insert(data_path="location", frame=72)
cam.keyframe_insert(data_path="rotation_euler", frame=72)

# Sun light
bpy.ops.object.light_add(type="SUN", location=(10.0, -10.0, 20.0))
sun = bpy.context.active_object
sun.data.energy = 3.5

bpy.ops.render.render(animation=True)
