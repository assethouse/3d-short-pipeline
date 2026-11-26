import bpy

# Clear default objects first so scene reference stays valid
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 9:16 vertical resolution, 30 fps, 90 frames (3 seconds)
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 90

# Use BLENDER_EEVEE and PNG output
scene.render.engine = "BLENDER_EEVEE"
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = "//build/frames/frame_"

# Road plane
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
road = bpy.context.active_object
road.name = "Road"
road_mat = bpy.data.materials.new("RoadMat")
road_mat.use_nodes = True
road_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.08, 0.09, 0.12, 1.0)
road.data.materials.append(road_mat)

# Moving stylized block
bpy.ops.mesh.primitive_cube_add(size=1.8, location=(0, -10, 0.9))
prop = bpy.context.active_object
prop.name = "HeroProp"
prop_mat = bpy.data.materials.new("PropMat")
prop_mat.use_nodes = True
prop_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.95, 0.35, 0.10, 1.0)
prop.data.materials.append(prop_mat)

prop.location = (0, -10, 0.9)
prop.keyframe_insert(data_path="location", frame=1)
prop.location = (0, 10, 0.9)
prop.keyframe_insert(data_path="location", frame=90)

# Camera pointing at the block
bpy.ops.object.camera_add(location=(4.5, -13, 3.8))
cam = bpy.context.active_object
scene.camera = cam
direction = prop.location - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

# Sunlight
bpy.ops.object.light_add(type="SUN", location=(5, -5, 12))
sun = bpy.context.active_object
sun.data.energy = 3.0

bpy.ops.render.render(animation=True)
