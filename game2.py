import numpy as np

w, h = 0.43, 0.65 # ストライクゾーン幅
x, z = -w/2, 0.4 # ストライクゾーン始点
dm = 18.44 # マウンドまでの距離
db = 27.431 # 塁間の距離

[STRAIGHT, SLIDER, CURVE, FORK, SINKER, SHOOT, H_SLIDER, CUT, SLOW_CURVE, DROP_CURVE, SLERVE, KNUCKLE_CURVE, V_SLIDER, PALM, 
SFF, CHANGEUP, H_SINKER, CIRCLE_CHANGE, H_SHOOT] = list(range(19))
speed_diff = np.array([0, 20, 25, 21, 22, 15, 10, 11, 30, 18, 15, 14, 15, 25, 10, 26, 12, 22, 10]) # 球速差

Max = 100
breaking_diff = {STRAIGHT: np.zeros(2), SLIDER: np.array([0.22, -0.05])/Max, CURVE: np.array([0.19, -0.16])/Max} # 右投手

# -------------------------------------------------------------
def rotation(x, y, deg=45):
    sin, cos = np.sin(np.deg2rad(deg)), np.cos(np.deg2rad(deg))
    return x*cos - y*sin, x*sin + y*cos
# -------------------------------------------------------------

# -------------------------------------------------------------
def circle_cr(p1, p2, p3):
    a, b = np.arctan((p2[1]-p1[1]) / (p2[0] - p1[0])) + np.pi/2, np.arctan((p3[1]-p2[1]) / (p3[0] - p2[0])) + np.pi/2
    e, f = (np.array(p1) + np.array(p2)) / 2, (np.array(p3) + np.array(p2)) / 2
    cx = (e[1]-f[1]-e[0]*np.tan(a) + f[0]*np.tan(b)) / (np.tan(b) - np.tan(a))
    cy = e[1]-(e[0]-cx)*np.tan(a)
    r = ((p1[0] - cx)**2 + (p1[1] - cy)**2)**(1/2)
    return (cx, cy), r
# -------------------------------------------------------------

l_wing, l_center, l_fence = 100, 122, 2 # 球場の広さ
left_pole, right_pole = rotation(0, l_wing), rotation(l_wing, 0) # 左、右ポール座標
circle_center, radius = circle_cr(left_pole, (0, l_center), right_pole) # 球場円の中心、半径
circle_y = lambda x: (radius**2 - (x - circle_center[0])**2)**(1/2) + circle_center[1] # 円の方程式、xを与えるとyが返る。

# -------------------------------------------------------------
class Fielder():
    def __init__(self):
        outfix = 0.7 # 外野の定位置（球場の割合）
        # 定位置座標
        fixed = {1: (0, dm), 2: (0, -1), 3: rotation(db + 2, 3), 4: rotation(db + 6, db - 10), 5: rotation(3, db - 1),
        6: rotation(db - 12, db + 6), 7: rotation(db - 12, l_wing*outfix), 8: (0, l_center*outfix), 9: rotation(l_wing*outfix, db - 10)}
        self.fielder = {i: {'r': 50, 's': 50, 'f': 50, 'pos': fixed[i]} for i in range(1, 10)}
# -------------------------------------------------------------
fielder = Fielder()

# -------------------------------------------------------------
def pitch(B=0, control=50, max_speed=130, condition=3):
    kinds = np.array(((STRAIGHT, 50), (SLIDER, 50), (CURVE, 50)))
    control_sigma = lambda control: -0.29/100 * control + 0.3 # コントロール分散

    if B == 3: goal = np.array((np.random.uniform(x, x + w), np.random.uniform(z, z + h))) # ストライク狙い
    else: goal = np.array((np.random.uniform(x - 0.1, x + w + 0.1), np.random.uniform(z - 0.1, z + h + 0.1)))
    ball_pos = goal + np.random.normal(0, control_sigma(control), 2) # ボール座標
    kind = np.random.choice(kinds[:,0], p=kinds[:,1]/kinds[:,1].sum()) # 球種
    speed = max_speed - (5 - condition + np.random.randint(0, 6)) - speed_diff[kind]
    breaking = kinds[np.where(kinds[:,0] == kind)[0][0]][1] + np.random.normal(0, 5) # 変化量
    if breaking < 0: breaking = 0
    elif breaking > 100: breaking = 100
    init_ball_pos = ball_pos - breaking_diff[kind] * breaking # 曲がる前の座標
    return speed, init_ball_pos, ball_pos, len(kinds)
# -------------------------------------------------------------

# バント未実装
# -------------------------------------------------------------
def bat(speed, init_ball_pos, ball_pos, n_kinds, meet=50, power=50):
    speed *= (1000/3600)
    bat_length = 0.9
    v_react = lambda meet, n_kinds, strong: ((0.5/100*meet + 0.1) / 3) * (-0.4/5*(n_kinds-1) + 1) if strong else 0.5/100*meet + 0.1 # 反応速度
    degree = lambda x: 55/0.04*x + 45 if x >= -0.01 else 110/0.03*x + 140/3 # 打球角度
    direction = lambda y, r: -np.rad2deg(np.arcsin(y/r)) * 1.3 # 打球方向
    bat_max_speed = lambda power, strong: (0.45*power + 115) * 1000 / 3600 if strong else (0.35*power + 80) * 1000 / 3600
    identify = 6 # 見極め距離
    aim = np.array((np.random.uniform(x, x + w), np.random.uniform(z, z + h))) # 狙い位置
    pred_pos = init_ball_pos + np.random.multivariate_normal([0, 0], [[0.05**2, 0], [0, 0.01**2]]) # ボールの推定位置(y=6)
    d_aim_pred = np.linalg.norm(aim - pred_pos)
    swing = True if d_aim_pred < np.random.normal(0.4, 0.1) else False # 振るかどうか
    if pred_pos[0] < x: pred_pos[0] = x
    elif pred_pos[0] > x + w: pred_pos[0] = x + w
    if pred_pos[1] < z: pred_pos[1] = z
    elif pred_pos[1] > z + h: pred_pos[1] = z + h
    if swing:
        error = (x - pred_pos[0] if pred_pos[0] < x else 0) + (pred_pos[0] - (x + w) if pred_pos[0] > x + w else 0) + (z - pred_pos[1] if pred_pos[1] < z else 0) + (pred_pos[1] - (z + h) if pred_pos[1] > z + h else 0)
        if np.random.rand() > np.exp(-6*error): swing = False
    if swing: # 振る場合
        strong = True if np.random.rand() < 0.5 + 0.2/50*(power - 50) else False # 強振するかどうか
        v = v_react(meet, n_kinds, strong) # 反応速度
        swing_y = np.random.normal(0, 0.3) # 振るy座標
        if swing_y < -bat_length or swing_y > bat_length: return [True] # 早すぎ、遅すぎ空振り
        t1 = (dm - identify) / speed # 見極めまでの時間
        move = v * t1 # 反応距離
        # 見極め時点での打撃位置
        if move >= d_aim_pred: bat_pos = pred_pos
        else: bat_pos = ((d_aim_pred - move)*aim + move*pred_pos) / d_aim_pred
        t2 = (identify - swing_y) / speed # 見極めから打撃位置までの時間
        pred_pos += ((ball_pos - init_ball_pos) / (identify / speed) * t2)
        d_bat_pred = np.linalg.norm(bat_pos - pred_pos) # 見極め打撃位置と推定位置との距離
        move = v * t2
        # 打撃位置
        if move >= d_bat_pred: bat_pos = pred_pos
        else: bat_pos = ((d_bat_pred - move)*bat_pos + move*pred_pos) / d_bat_pred
        if (ball_pos[0] - bat_pos[0] > 0.15) or (bat_pos[0] - ball_pos[0] > 0.3) or abs(bat_pos[1] - ball_pos[1]) > 0.04: return [True] # 空振り
        else:
            v = bat_max_speed(power, strong) * (-1/0.45*abs(ball_pos[0] - bat_pos[0]) + 1) * (-1/0.16*abs(bat_pos[1] - ball_pos[1]) + 1) * (5/9*swing_y + 1) # 打球速度
            deg = degree(bat_pos[1] - ball_pos[1]) # 打球角度
            direct = direction(swing_y, 0.75 + ball_pos[0] - bat_pos[0]) # 打球方向
            return [v, deg, direct]
    else:
        if x <= ball_pos[0] <= x + w and z <= ball_pos[1] <= z + h: return [True] # 見逃しストライク
        else: return [False] # 見逃しボール
# -------------------------------------------------------------

# -------------------------------------------------------------
def defend(batting_results):
    if len(batting_results) == 3:
        v, deg, direct = batting_results
        if deg > 0:
            g = 9.80665
            rad = np.deg2rad(deg)
            H = ball_pos[1] + ((v*np.sin(rad))**2)/(2*g)
            v_e = ((v*np.cos(rad))**2 + 2*g*H)**(1/2) # 着地点での速度
            deg_e = np.arctan(((2*g*H)**(1/2)) / (v*np.cos(rad))) # 着地点での角度
            L = ((v**2)*np.sin(2 * rad) + (v_e**2)*np.sin(2 * deg_e)) / (2*g) # 着地までの距離
            T = (v*np.sin(rad) + v_e*np.sin(deg_e)) / g # 着地までの時間
        else:
            rad = np.deg2rad(-deg)
            T = ball_pos[1] / (v*np.sin(rad)) # 着地までの時間
            L = ball_pos[1] / np.tan(rad) # 着地までの距離
# -------------------------------------------------------------

# -------------------------------------------------------------
def main():
    while True:
        speed, init_ball_pos, ball_pos, n_kinds = pitch()
        batting_results = bat(speed, init_ball_pos, ball_pos, n_kinds)
        defend(batting_results)
# -------------------------------------------------------------


if __name__ == '__main__': main()


