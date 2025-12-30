# アルファベットTKSにリグを入れる

## Pixerのロゴアニメみたくアルファベットが擬人化して有機的に動く3DCGアニメをBlender5.0の Pythonスクリプトで作りたいのだけど、先に3Dモデルの文字にリグを入れた方がいいって言われて。 だけど、そもそもリグが分かんない。リグって何？関連する言葉も説明してほしい。骨格関連とメッシュ関連とアニメーション関連に分けれるのかな？なんかいい感じに説明してくれる？

- Copilot君 ずらずらと。

## アルファベットはTKSの3文字から始めたい。まずはT。Tにリグを入れたいのだけど、どんなコマンドにすればいい？一般的にリグ入れてって言ったら、指示するときはどんな情報を渡すの？

- Copilot君
まず結論（超要約）

「Tにリグを入れる」＝実際にはこの4点を決めて指示すること

1️⃣ どんな骨構造にするか（ボーン設計）
2️⃣ どの骨がどこを動かすか（ウェイトの考え方）
3️⃣ 操作用か・変形用か（コントローラの有無）
4️⃣ 最終的にどんな動きをさせたいか（用途）

「リグ入れて」は
👉 抽象的すぎるので、最低限これを言語化するのが一般的。

T の場合：まず決めるべき設計
Pixar風「擬人化T」の最小構成（おすすめ）
     ─ ─ ─ ─  ← 横棒
        |
        |  ← 縦棒
        |


これを キャラとして動かすなら👇

🎯 ボーン構成（最小）
ボーン名	役割
root	全体の移動
body	縦棒（胴体）
bar_L	横棒 左
bar_R	横棒 右

👉 4本で十分
👉 人間の腕っぽく横棒を使える

Blenderでの「リグを入れる」基本コマンド群

以下は Pythonで完全自動化する場合の最小セット。

① T の文字メッシュを作る
import bpy

bpy.ops.object.text_add(location=(0, 0, 0))
txt = bpy.context.object
txt.data.body = "T"

bpy.ops.object.convert(target='MESH')
mesh = bpy.context.object
mesh.name = "T_mesh"

② アーマチュア作成（＝リグの核）
bpy.ops.object.armature_add(location=(0, 0, 0))
arm = bpy.context.object
arm.name = "T_rig"

③ ボーンを「設計通り」に作る
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')

eb = arm.data.edit_bones

# 既存ボーン削除
eb.remove(eb[0])

# root
root = eb.new("root")
root.head = (0, 0, 0)
root.tail = (0, 0, 0.2)

# body（縦棒）
body = eb.new("body")
body.head = (0, 0, 0.2)
body.tail = (0, 0, 1.6)
body.parent = root

# 横棒 左
bar_l = eb.new("bar_L")
bar_l.head = (0, 0, 1.6)
bar_l.tail = (-0.8, 0, 1.6)
bar_l.parent = body

# 横棒 右
bar_r = eb.new("bar_R")
bar_r.head = (0, 0, 1.6)
bar_r.tail = (0.8, 0, 1.6)
bar_r.parent = body

bpy.ops.object.mode_set(mode='OBJECT')


👉 これで「T用リグ」が完成

④ メッシュとリグを関連付け（スキニング）
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm

bpy.ops.object.parent_set(type='ARMATURE_AUTO')


👉 自動ウェイト
👉 後で手直し可能

「リグ入れて」って言うときに渡す情報（超重要）
人に頼むとき／AIに頼むとき
✅ 最低限これを渡す
・対象：アルファベット T
・用途：Pixarロゴ風に跳ねる・しなる
・骨構造：
    root
    body（縦棒）
    bar_L（横棒 左）
    bar_R（横棒 右）
・変形方式：アーマチュア＋自動ウェイト
・操作単位：1文字＝1リグ


これだけで 「分かってる人」には通じる。

もう一段レベル高い指示（プロ寄り）
・横棒は腕のように回転させたい
・ジャンプ時にbodyが少し遅れてついてくる
・rootは地面移動用
・制御は全てPose Modeで可能にしたい


👉 Pixarっぽさはここで決まる

よくある勘違い

❌「リグ入れる＝自動でいい感じになる」
⭕「どんな動きをさせたいかを先に決める」

次の一手（おすすめ）

次はどれ行く？

1️⃣ Tがぴょんって跳ねる最小アニメーション（Python）
2️⃣ bar_L / bar_R を腕っぽく振る
3️⃣ TKS 3文字を同じ関数でリグ生成

「まずは①」って言われたら、そのまま動くコード出すよ。

# まずは①でお願いしまっす。

了解 👍
じゃあ **「T が ぴょんって跳ねる最小アニメーション」**を
Blender5.0でそのまま実行できる Python スクリプトとして出すね。

目的はこれ👇

T にリグを入れる

root で上下移動

body を少し遅らせて回転

Pixarロゴっぽい「ため → ジャンプ → 着地」

完成イメージ（動きの設計）
frame  1 : しゃがむ（ため）
frame 15 : ジャンプ頂点
frame 30 : 着地


root：上下移動

body：少し遅れて前後に傾く

bar_L / bar_R：今回は固定（次ステップで腕化）

👉 そのまま貼って実行できるコード（Blender 5.0）
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
bpy.ops.object.text_add(location=(0, 0, 0))
txt = bpy.context.object
txt.data.body = "T"

bpy.ops.object.convert(target='MESH')
mesh = bpy.context.object
mesh.name = "T_mesh"

# 少し太くする
bpy.ops.object.modifier_add(type='SOLIDIFY')
mesh.modifiers["Solidify"].thickness = 0.15

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

このコードで「何をやってるか」
✔ Pixarっぽさの正体

root と body を別に動かしてる

body が

ため：後ろに傾く

ジャンプ：少し遅れて前に傾く

これだけで「生きてる感」が出る

Blender上で確認するポイント

Pose Mode に入る

root だけ動かす → 全体移動

body だけ回す → しなる

👉 「骨を触ると意味が分かる」状態になってる

次にやると一気に Pixar 化する

おすすめ順👇

1️⃣ bar_L / bar_R を腕みたいに振る
2️⃣ Fカーブで着地を少しバウンドさせる
3️⃣ TKS 3文字をループで生成＋時間ずらし

次はどれ行く？
「②で！」って言われたら、そのまま腕振りコード出すよ。
