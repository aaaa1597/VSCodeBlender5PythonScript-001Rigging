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
# 2. Text → Mesh（回転適用込み）
# =========================
bpy.ops.object.text_add(location=(0, 0, 0))
txt = bpy.context.object
txt.data.body = "T"
txt.data.size = 1.0

# 正面を向かせる（起こす）
txt.rotation_euler = (math.radians(90), 0, 0)

# Mesh化
bpy.ops.object.convert(target='MESH')
mesh = bpy.context.object
mesh.name = "T_mesh"

# 厚み追加
solid = mesh.modifiers.new(name="Solidify", type='SOLIDIFY')
solid.thickness = 0.15

# 回転・スケールを適用
bpy.context.view_layer.objects.active = mesh
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# =========================
# 3. 原点を足元中央に
# =========================
import mathutils

# メッシュのバウンディングボックス（ローカル）
bbox = [mathutils.Vector(v) for v in mesh.bound_box]

# 最小値/最大値取得
min_x = min(v.x for v in bbox)
max_x = max(v.x for v in bbox)
min_y = min(v.y for v in bbox)
max_y = max(v.y for v in bbox)
min_z = min(v.z for v in bbox)
center_x = (min_x + max_x) * 0.5
center_y = (min_y + max_y) * 0.5

# ワールド座標に変換
local_point = mathutils.Vector((center_x, center_y, min_z))
world_point = mesh.matrix_world @ local_point

# 3Dカーソルを足元へ
cursor = bpy.context.scene.cursor
cursor.location = world_point

# 原点を3Dカーソルへ
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

# =========================
# 4. 寸法取得（Zが高さ）
# =========================
dims = mesh.dimensions
width = dims.x
height = dims.z

# =========================
# 5. アーマチュア作成
# =========================
bpy.ops.object.armature_add()
arm = bpy.context.object
arm.name = "T_rig"
arm.location = mesh.location

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

# ログ出力
print("mesh loc:", mesh.location)
print("arm loc :", arm.location)

# =========================
# 7. 簡易ジャンプアニメ
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
root_p.location = (0, 0, -height * 0.1)
body_p.rotation_euler = (math.radians(-10), 0, 0)
keyframe(root_p, 10)
keyframe(body_p, 10)

# ジャンプ頂点
scene.frame_set(20)
root_p.location = (0, 0, height * 0.8)
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
