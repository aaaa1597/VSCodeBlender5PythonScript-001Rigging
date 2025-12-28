import bpy
import math

# =========================
# 1. シーン初期化
# =========================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 40

# =========================
# 2. T メッシュ作成
# =========================
bpy.ops.object.text_add(location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
txt = bpy.context.object
txt.data.body = "T"

bpy.ops.object.convert(target='MESH')
mesh = bpy.context.object
mesh.name = "T_mesh"

# 少し太くする
mod = mesh.modifiers.new(name="Solidify", type='SOLIDIFY')
mod.thickness = 0.15

# =========================
# 3. アーマチュア作成
# =========================
bpy.ops.object.armature_add(location=(0, 0, 0))
arm = bpy.context.object
arm.name = "T_rig"

bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')

eb = arm.data.edit_bones
eb.remove(eb[0])

# root
root = eb.new("root")
root.head = (0, 0, 0)
root.tail = (0, 0, 0.2)

# body
body = eb.new("body")
body.head = (0, 0, 0.2)
body.tail = (0, 0, 1.6)
body.parent = root

# bar_L
bar_l = eb.new("bar_L")
bar_l.head = (0, 0, 1.6)
bar_l.tail = (-0.8, 0, 1.6)
bar_l.parent = body

# bar_R
bar_r = eb.new("bar_R")
bar_r.head = (0, 0, 1.6)
bar_r.tail = (0.8, 0, 1.6)
bar_r.parent = body

bpy.ops.object.mode_set(mode='OBJECT')

# =========================
# 4. メッシュとリグを紐付け
# =========================
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# =========================
# 5. ジャンプアニメーション
# =========================
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')

root_p = arm.pose.bones["root"]
body_p = arm.pose.bones["body"]

def keyframe(bone, frame):
    bone.keyframe_insert(data_path="location", frame=frame)
    bone.keyframe_insert(data_path="rotation_euler", frame=frame)

# 初期
scene.frame_set(1)
root_p.location = (0, 0, 0)
body_p.rotation_euler = (0, 0, 0)
keyframe(root_p, 1)
keyframe(body_p, 1)

# ため
scene.frame_set(10)
root_p.location = (0, 0, -0.2)
body_p.rotation_euler = (math.radians(-10), 0, 0)
keyframe(root_p, 10)
keyframe(body_p, 10)

# ジャンプ頂点
scene.frame_set(20)
root_p.location = (0, 0, 1.2)
body_p.rotation_euler = (math.radians(15), 0, 0)
keyframe(root_p, 20)
keyframe(body_p, 20)

# 着地
scene.frame_set(30)
root_p.location = (0, 0, 0)
body_p.rotation_euler = (math.radians(-5), 0, 0)
keyframe(root_p, 30)
keyframe(body_p, 30)

bpy.ops.object.mode_set(mode='OBJECT')
