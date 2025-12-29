import bpy
import math
import mathutils

# =========================
# 1. シーン初期化
# =========================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 40

# =========================
# 2. Text → Mesh
# =========================
bpy.ops.object.text_add(location=(0, 0, 0))
txt = bpy.context.object
txt.data.body = "T"
txt.data.size = 1.0

# 正面向き
txt.rotation_euler = (math.radians(90), 0, 0)

# Mesh化
bpy.ops.object.convert(target='MESH')
mesh = bpy.context.object
mesh.name = "T_mesh"

# 厚み
solid = mesh.modifiers.new(name="Solidify", type='SOLIDIFY')
solid.thickness = 0.15

# 回転適用
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# =========================
# 3. 原点を足元中央に
# =========================
bbox = [mathutils.Vector(v) for v in mesh.bound_box]

min_x = min(v.x for v in bbox)
max_x = max(v.x for v in bbox)
min_y = min(v.y for v in bbox)
max_y = max(v.y for v in bbox)
min_z = min(v.z for v in bbox)

center_x = (min_x + max_x) * 0.5
center_y = (min_y + max_y) * 0.5

cursor = scene.cursor
cursor.location = mesh.matrix_world @ mathutils.Vector((center_x, center_y, min_z))

bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# =========================
# 4. サイズ取得
# =========================
width = mesh.dimensions.x
height = mesh.dimensions.z

# =========================
# 5. アーマチュア作成
# =========================
bpy.ops.object.armature_add(location=mesh.location)
arm = bpy.context.object
arm.name = "T_rig"

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')

eb = arm.data.edit_bones
eb.remove(eb[0])

# root（地面接地）
root = eb.new("root")
root.head = (0, 0, 0)
root.tail = (0, 0, height * 0.1)

# body（縦棒）
body = eb.new("body")
body.head = root.tail
body.tail = (0, 0, height * 0.9)
body.parent = root

# bar_L（左腕）
bar_l = eb.new("bar_L")
bar_l.head = body.tail
bar_l.tail = (-width * 0.5, 0, height * 0.9)
bar_l.parent = body

# bar_R（右腕）
bar_r = eb.new("bar_R")
bar_r.head = body.tail
bar_r.tail = (width * 0.5, 0, height * 0.9)
bar_r.parent = body

bpy.ops.object.mode_set(mode='OBJECT')

# =========================
# 6. メッシュとリグを紐付け
# =========================
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# =========================
# 7. ジャンプアニメーション
# =========================

# --- ジャンプ（アーマチュア全体） ---
def key_obj(obj, frame):
    obj.keyframe_insert(data_path="location", frame=frame)

scene.frame_set(1)
arm.location = (0, 0, 0)
key_obj(arm, 1)

scene.frame_set(10)  # ため
arm.location = (0, 0, -height * 0.1)
key_obj(arm, 10)

scene.frame_set(20)  # ジャンプ頂点
arm.location = (0, 0, height * 0.8)
key_obj(arm, 20)

scene.frame_set(30)  # 着地
arm.location = (0, 0, 0)
key_obj(arm, 30)

# --- しなり（ボーン） ---
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')

body_p = arm.pose.bones["body"]
bar_l_p = arm.pose.bones["bar_L"]
bar_r_p = arm.pose.bones["bar_R"]

def key_bone(bone, frame):
    bone.keyframe_insert(data_path="rotation_euler", frame=frame)

# 初期
scene.frame_set(1)
body_p.rotation_euler = (0, 0, 0)
bar_l_p.rotation_euler = (0, 0, 0)
bar_r_p.rotation_euler = (0, 0, 0)
key_bone(body_p, 1)
key_bone(bar_l_p, 1)
key_bone(bar_r_p, 1)

# ため
scene.frame_set(10)
body_p.rotation_euler = (math.radians(-12), 0, 0)
key_bone(body_p, 10)

# ジャンプ
scene.frame_set(20)
body_p.rotation_euler = (math.radians(15), 0, 0)
bar_l_p.rotation_euler = (0, math.radians(10), 0)
bar_r_p.rotation_euler = (0, math.radians(-10), 0)
key_bone(body_p, 20)
key_bone(bar_l_p, 20)
key_bone(bar_r_p, 20)

# 着地
scene.frame_set(30)
body_p.rotation_euler = (math.radians(-5), 0, 0)
bar_l_p.rotation_euler = (0, 0, 0)
bar_r_p.rotation_euler = (0, 0, 0)
key_bone(body_p, 30)
key_bone(bar_l_p, 30)
key_bone(bar_r_p, 30)

bpy.ops.object.mode_set(mode='OBJECT')

print("DONE: T jump animation (Z-up fixed)")
