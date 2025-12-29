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

scene.cursor.location = mesh.matrix_world @ mathutils.Vector((center_x, center_y, min_z))
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

# spine（3分割）
sp1 = eb.new("spine_1")
sp1.head = root.tail
sp1.tail = (0, 0, height * 0.35)
sp1.parent = root

sp2 = eb.new("spine_2")
sp2.head = sp1.tail
sp2.tail = (0, 0, height * 0.65)
sp2.parent = sp1

sp3 = eb.new("spine_3")
sp3.head = sp2.tail
sp3.tail = (0, 0, height * 0.9)
sp3.parent = sp2

# arms（左右2分割）
aL1 = eb.new("arm_L_1")
aL1.head = sp3.tail
aL1.tail = (-width * 0.25, 0, height * 0.9)
aL1.parent = sp3

aL2 = eb.new("arm_L_2")
aL2.head = aL1.tail
aL2.tail = (-width * 0.5, 0, height * 0.9)
aL2.parent = aL1

aR1 = eb.new("arm_R_1")
aR1.head = sp3.tail
aR1.tail = (width * 0.25, 0, height * 0.9)
aR1.parent = sp3

aR2 = eb.new("arm_R_2")
aR2.head = aR1.tail
aR2.tail = (width * 0.5, 0, height * 0.9)
aR2.parent = aR1

# ===== IK安定用：肘にわずかな前後オフセット =====
aL1.tail.y += 0.02
aL2.tail.y += 0.02

aR1.tail.y -= 0.02
aR2.tail.y -= 0.02

# =========================
# IK安定用：腕ボーンのロールを固定
# =========================
for bname in ("arm_L_1", "arm_L_2"):
    eb[bname].roll = math.radians(90)

for bname in ("arm_R_1", "arm_R_2"):
    eb[bname].roll = math.radians(-90)

# =========================
# IKターゲット用：tail位置を保存
# =========================
arm_matrix = arm.matrix_world.copy()

tail_L_local = eb["arm_L_2"].tail.copy()
tail_R_local = eb["arm_R_2"].tail.copy()

bpy.ops.object.mode_set(mode='OBJECT')

# =========================
# 6. IKターゲット作成
# =========================
def make_ik(name, local_tail):
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    ik = bpy.context.object
    ik.name = name
    # 親子付け
    ik.parent = arm
    # bone.tail の「アーマチュアローカル」をそのまま使う
    ik.location = local_tail
    return ik

ik_L = make_ik("IK_L", tail_L_local)
ik_R = make_ik("IK_R", tail_R_local)
ik_L.parent = arm
ik_R.parent = arm

# =========================
# Pole Target 作成（肘方向固定）
# =========================
def make_pole(name, offset):
    bpy.ops.object.empty_add(type='PLAIN_AXES')
    pole = bpy.context.object
    pole.name = name
    pole.parent = arm
    pole.location = offset
    return pole

pole_L = make_pole("Pole_L", tail_L_local + mathutils.Vector((0, 0.3, 0)))
pole_R = make_pole("Pole_R", tail_R_local + mathutils.Vector((0, -0.3, 0)))

# =========================
# 7. Pose拘束追加
# =========================
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')

# Limit Rotation（全ボーン）
for pb in arm.pose.bones:
    c = pb.constraints.new('LIMIT_ROTATION')
    c.use_limit_x = True
    c.use_limit_y = True
    c.use_limit_z = True
    c.min_x = c.min_y = c.min_z = math.radians(-30)
    c.max_x = c.max_y = c.max_z = math.radians(30)
    c.owner_space = 'LOCAL'

# Copy Rotation（背骨：段階伝播）
for src, dst, inf in [
    ("spine_1", "spine_2", 0.3),
    ("spine_2", "spine_3", 0.6),
]:
    pb = arm.pose.bones[dst]
    c = pb.constraints.new('COPY_ROTATION')
    c.target = arm
    c.subtarget = src
    c.influence = inf
    c.owner_space = 'LOCAL'
    c.target_space = 'LOCAL'

# IK（腕）
for side, ik, pole in (("L", ik_L, pole_L), ("R", ik_R, pole_R)):
    pb = arm.pose.bones[f"arm_{side}_2"]
    c = pb.constraints.new('IK')
    c.target = ik
    c.pole_target = pole
    c.pole_angle = math.radians(90 if side == "L" else -90)
    c.chain_count = 2
    c.use_stretch = False

bpy.ops.object.mode_set(mode='OBJECT')

# =========================
# 8. メッシュとリグ紐付け
# =========================
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# =========================
# 9. ジャンプアニメーション
# =========================
def key_obj(obj, f):
    obj.keyframe_insert(data_path="location", frame=f)

def key_rot(bone, f):
    bone.keyframe_insert(data_path="rotation_euler", frame=f)

# 重心（アーマチュア）
scene.frame_set(1)
arm.location = (0, 0, 0)
key_obj(arm, 1)

scene.frame_set(6)
arm.location = (0, 0, -height * 0.12)
key_obj(arm, 6)

scene.frame_set(12)
arm.location = (0, 0, height * 0.85)
key_obj(arm, 12)

scene.frame_set(18)
arm.location = (0, 0, 0)
key_obj(arm, 18)

# 体（spine_1）
bpy.ops.object.mode_set(mode='POSE')
sp1p = arm.pose.bones["spine_1"]

scene.frame_set(1)
sp1p.rotation_euler = (0, 0, 0)
key_rot(sp1p, 1)

scene.frame_set(6)
sp1p.rotation_euler = (math.radians(-18), 0, 0)
key_rot(sp1p, 6)

scene.frame_set(12)
sp1p.rotation_euler = (math.radians(22), 0, 0)
key_rot(sp1p, 12)

scene.frame_set(18)
sp1p.rotation_euler = (math.radians(-6), 0, 0)
key_rot(sp1p, 18)

scene.frame_set(22)
sp1p.rotation_euler = (0, 0, 0)
key_rot(sp1p, 22)

# 腕（IKターゲット）
def key_ik(obj, f):
    obj.keyframe_insert(data_path="location", frame=f)

scene.frame_set(1)
ik_L.location.z = ik_R.location.z = height * 0.9
key_ik(ik_L, 1)
key_ik(ik_R, 1)

scene.frame_set(6)
ik_L.location.z = ik_R.location.z = height * 0.8
key_ik(ik_L, 6)
key_ik(ik_R, 6)

scene.frame_set(14)
ik_L.location.z = ik_R.location.z = height * 1.05
key_ik(ik_L, 14)
key_ik(ik_R, 14)

scene.frame_set(20)
ik_L.location.z = ik_R.location.z = height * 0.85
key_ik(ik_L, 20)
key_ik(ik_R, 20)

bpy.ops.object.mode_set(mode='OBJECT')

print("DONE : T jump animation (full integrated rig)")
