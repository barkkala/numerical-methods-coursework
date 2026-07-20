import importlib.util
import math
from pathlib import Path

import tkinter as tk
from tkinter import messagebox

import readme


WINDOW_WIDTH = 960
WINDOW_HEIGHT = 740

CROCODILE_DELAY = 16
CROCODILE_BODY_COUNT = 36
CROCODILE_BODY_STEP = 10
CROCODILE_MAX_SPEED = 3.8
CROCODILE_TURN_SPEED = 0.075
CROCODILE_HIP_OFFSET = 8
CROCODILE_FOOT_SIDE = 32
CROCODILE_FOOT_FORWARD = 22
CROCODILE_STEP_DISTANCE = 30
CROCODILE_STEP_SPEED = 0.09
CROCODILE_UPPER_LEG = 28
CROCODILE_LOWER_LEG = 28

crocodile_mouse = {"x": WINDOW_WIDTH / 2.5, "y": WINDOW_HEIGHT / 2.5}
crocodile_body = []
crocodile_legs = []
crocodile_state = {"angle": 0.0, "speed": 0.0, "tick": 0}


def crocodile_clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def crocodile_angle_diff(a, b):
    return (a - b + math.pi) % (math.pi * 2) - math.pi


def crocodile_point_at(x, y, angle, distance):
    return [
        x + math.cos(angle) * distance,
        y + math.sin(angle) * distance,
    ]


def crocodile_make_body():
    cx = WINDOW_WIDTH / 2
    cy = WINDOW_HEIGHT / 2

    crocodile_body.clear()
    for i in range(CROCODILE_BODY_COUNT):
        crocodile_body.append([cx - i * CROCODILE_BODY_STEP, cy])


def crocodile_body_angle(index):
    index = crocodile_clamp(index, 0, len(crocodile_body) - 2)
    a = crocodile_body[index]
    b = crocodile_body[index + 1]
    return math.atan2(a[1] - b[1], a[0] - b[0])


def crocodile_hip_position(leg):
    x, y = crocodile_body[leg["body_index"]]
    angle = crocodile_body_angle(leg["body_index"])
    side_angle = angle + math.pi / 2

    return [
        x + math.cos(side_angle) * leg["side"] * CROCODILE_HIP_OFFSET,
        y + math.sin(side_angle) * leg["side"] * CROCODILE_HIP_OFFSET,
    ]


def crocodile_ideal_foot_position(leg):
    hip = crocodile_hip_position(leg)
    angle = crocodile_body_angle(leg["body_index"])
    side_angle = angle + math.pi / 2

    return [
        hip[0]
        + math.cos(side_angle) * leg["side"] * CROCODILE_FOOT_SIDE
        + math.cos(angle) * CROCODILE_FOOT_FORWARD,
        hip[1]
        + math.sin(side_angle) * leg["side"] * CROCODILE_FOOT_SIDE
        + math.sin(angle) * CROCODILE_FOOT_FORWARD,
    ]


def crocodile_make_legs():
    crocodile_legs.clear()

    leg_places = [
        (7, -1, 0),
        (7, 1, 1),
        (18, -1, 1),
        (18, 1, 0),
    ]

    for body_index, side, group in leg_places:
        leg = {
            "body_index": body_index,
            "side": side,
            "group": group,
            "foot": [0, 0],
            "from": [0, 0],
            "to": [0, 0],
            "step": 0.0,
            "moving": False,
        }
        leg["foot"] = crocodile_ideal_foot_position(leg)
        leg["from"] = leg["foot"][:]
        leg["to"] = leg["foot"][:]
        crocodile_legs.append(leg)


def crocodile_moving_leg_count():
    return sum(1 for leg in crocodile_legs if leg["moving"])


def crocodile_start_step_if_needed(leg):
    if leg["moving"]:
        return

    wanted = crocodile_ideal_foot_position(leg)
    dx = wanted[0] - leg["foot"][0]
    dy = wanted[1] - leg["foot"][1]

    if math.hypot(dx, dy) < CROCODILE_STEP_DISTANCE:
        return

    if crocodile_moving_leg_count() >= 2:
        return

    same_side_is_moving = any(
        other is not leg and other["moving"] and other["side"] == leg["side"]
        for other in crocodile_legs
    )
    if same_side_is_moving:
        return

    leg["moving"] = True
    leg["step"] = 0.0
    leg["from"] = leg["foot"][:]
    leg["to"] = wanted


def crocodile_update_one_leg(leg):
    crocodile_start_step_if_needed(leg)

    if not leg["moving"]:
        return

    leg["step"] += CROCODILE_STEP_SPEED
    t = crocodile_clamp(leg["step"], 0.0, 1.0)
    smooth_t = t * t * (3 - 2 * t)

    leg["foot"][0] = leg["from"][0] + (leg["to"][0] - leg["from"][0]) * smooth_t
    leg["foot"][1] = leg["from"][1] + (leg["to"][1] - leg["from"][1]) * smooth_t

    if t >= 1.0:
        leg["moving"] = False
        leg["foot"] = leg["to"][:]


def crocodile_update_legs():
    crocodile_state["tick"] += 1

    active_group = (crocodile_state["tick"] // 24) % 2
    ordered = [leg for leg in crocodile_legs if leg["group"] == active_group]
    ordered += [leg for leg in crocodile_legs if leg["group"] != active_group]

    for leg in ordered:
        crocodile_update_one_leg(leg)


def crocodile_move_body():
    head = crocodile_body[0]
    dx = crocodile_mouse["x"] - head[0]
    dy = crocodile_mouse["y"] - head[1]
    distance = math.hypot(dx, dy)

    if distance > 1:
        wanted_angle = math.atan2(dy, dx)
        turn = crocodile_clamp(
            crocodile_angle_diff(wanted_angle, crocodile_state["angle"]),
            -CROCODILE_TURN_SPEED,
            CROCODILE_TURN_SPEED,
        )
        crocodile_state["angle"] += turn

    planted = len(crocodile_legs) - crocodile_moving_leg_count()
    leg_power = 0.28 + 0.72 * planted / len(crocodile_legs)
    wanted_speed = crocodile_clamp(distance * 0.045, 0, CROCODILE_MAX_SPEED) * leg_power

    if distance < 18:
        wanted_speed = 0

    crocodile_state["speed"] += (wanted_speed - crocodile_state["speed"]) * 0.12
    head[0] += math.cos(crocodile_state["angle"]) * crocodile_state["speed"]
    head[1] += math.sin(crocodile_state["angle"]) * crocodile_state["speed"]

    for i in range(1, len(crocodile_body)):
        prev = crocodile_body[i - 1]
        cur = crocodile_body[i]
        dx = cur[0] - prev[0]
        dy = cur[1] - prev[1]
        distance = math.hypot(dx, dy)

        if distance == 0:
            cur[0] = prev[0] - CROCODILE_BODY_STEP
            cur[1] = prev[1]
            continue

        cur[0] = prev[0] + dx / distance * CROCODILE_BODY_STEP
        cur[1] = prev[1] + dy / distance * CROCODILE_BODY_STEP


def crocodile_leg_knee(hip, foot, side, spine_angle):
    dx = foot[0] - hip[0]
    dy = foot[1] - hip[1]
    raw_distance = math.hypot(dx, dy)
    if raw_distance == 0:
        raw_distance = 1
    distance = crocodile_clamp(raw_distance, 1, CROCODILE_UPPER_LEG + CROCODILE_LOWER_LEG - 1)

    dir_x = dx / raw_distance
    dir_y = dy / raw_distance
    mid = [
        hip[0] + dir_x * distance * 0.5,
        hip[1] + dir_y * distance * 0.5,
    ]

    height = math.sqrt(max(0, CROCODILE_UPPER_LEG * CROCODILE_UPPER_LEG - (distance * 0.5) ** 2))
    perp = [-dir_y, dir_x]
    outward = [
        math.cos(spine_angle + math.pi / 2) * side,
        math.sin(spine_angle + math.pi / 2) * side,
    ]

    if perp[0] * outward[0] + perp[1] * outward[1] < 0:
        perp[0] *= -1
        perp[1] *= -1

    return [
        mid[0] + perp[0] * height,
        mid[1] + perp[1] * height,
    ]


def crocodile_visible_foot(leg):
    foot = leg["foot"][:]
    if leg["moving"]:
        lift = math.sin(leg["step"] * math.pi) * 7
        angle = crocodile_body_angle(leg["body_index"])
        foot[0] += math.cos(angle + math.pi / 2) * leg["side"] * lift
        foot[1] += math.sin(angle + math.pi / 2) * leg["side"] * lift
    return foot


def crocodile_draw_foot(canvas, foot, angle, side):
    toe_angles = [
        angle + side * 0.35,
        angle,
        angle - side * 0.35,
    ]

    for toe_angle in toe_angles:
        end = crocodile_point_at(foot[0], foot[1], toe_angle, 8)
        canvas.create_line(foot[0], foot[1], end[0], end[1],
                           fill="#102815", width=1)


def crocodile_draw_legs(canvas):
    for leg in crocodile_legs:
        hip = crocodile_hip_position(leg)
        foot = crocodile_visible_foot(leg)
        angle = crocodile_body_angle(leg["body_index"])
        knee = crocodile_leg_knee(hip, foot, leg["side"], angle)

        canvas.create_line(hip[0], hip[1], knee[0], knee[1],
                           foot[0], foot[1], fill="#2f6b37", width=3,
                           smooth=True)
        canvas.create_oval(knee[0] - 2, knee[1] - 2,
                           knee[0] + 2, knee[1] + 2,
                           outline="#102815", fill="#9ac46a")
        crocodile_draw_foot(canvas, foot, angle, leg["side"])


def crocodile_body_radius(index):
    t = index / (len(crocodile_body) - 1)

    if t < 0.12:
        return 8 + t * 30
    if t < 0.55:
        return 12
    return max(2.0, 12 * (1 - t) / 0.45)


def crocodile_draw_body(canvas):
    left_side = []
    right_side = []

    for i, (x, y) in enumerate(crocodile_body):
        angle = crocodile_body_angle(min(i, len(crocodile_body) - 2))
        side_angle = angle + math.pi / 2
        radius = crocodile_body_radius(i)

        left_side.append([
            x + math.cos(side_angle) * radius,
            y + math.sin(side_angle) * radius,
        ])
        right_side.append([
            x - math.cos(side_angle) * radius,
            y - math.sin(side_angle) * radius,
        ])

    points = []
    for point in left_side + right_side[::-1]:
        points.extend(point)

    canvas.create_polygon(points, fill="#3f7f35", outline="#102815",
                          width=2, smooth=True)

    spine = []
    for point in crocodile_body:
        spine.extend(point)
    canvas.create_line(spine, fill="#9ac46a", width=1, smooth=True)


def crocodile_draw_head(canvas):
    head = crocodile_body[0]
    angle = crocodile_body_angle(0)
    tip = crocodile_point_at(head[0], head[1], angle, 24)
    left = crocodile_point_at(head[0], head[1], angle + 2.35, 13)
    right = crocodile_point_at(head[0], head[1], angle - 2.35, 13)

    canvas.create_polygon(
        tip[0], tip[1],
        left[0], left[1],
        right[0], right[1],
        outline="#102815",
        fill="#3f7f35",
        width=2,
    )

    eye_left = crocodile_point_at(head[0], head[1], angle + 0.72, 8)
    eye_right = crocodile_point_at(head[0], head[1], angle - 0.72, 8)
    canvas.create_oval(eye_left[0] - 2, eye_left[1] - 2,
                       eye_left[0] + 2, eye_left[1] + 2,
                       fill="white", outline="#102815")
    canvas.create_oval(eye_right[0] - 2, eye_right[1] - 2,
                       eye_right[0] + 2, eye_right[1] + 2,
                       fill="white", outline="#102815")


def crocodile_update(canvas):
    crocodile_update_legs()
    crocodile_move_body()

    canvas.delete("all")
    crocodile_draw_legs(canvas)
    crocodile_draw_body(canvas)
    crocodile_draw_head(canvas)

    canvas.after(CROCODILE_DELAY, crocodile_update, canvas)


def crocodile_on_mouse_move(root, event):
    x = event.x_root - root.winfo_rootx()
    y = event.y_root - root.winfo_rooty()

    if 0 <= x <= WINDOW_WIDTH and 0 <= y <= WINDOW_HEIGHT:
        crocodile_mouse["x"] = x
        crocodile_mouse["y"] = y


# Крокодил: анимированный фон главного окна
def create_crocodile_background(root):
    crocodile_make_body()
    crocodile_make_legs()

    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
                       bg="white", highlightthickness=0)
    canvas.place(x=0, y=0, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

    root.bind_all("<Motion>", lambda event: crocodile_on_mouse_move(root, event))
    crocodile_update(canvas)


def load_module(filename, module_name):
    module_path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Не удалось загрузить {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 1 часть: раздел интегралов
def create_integral_section(root):
    tk.Label(root, text="1 - Интегралы", font=("Arial", 14), bg="white").place(x=30, y=20)
    integral_frame = tk.LabelFrame(root, text="Выберите интеграл", relief="solid", borderwidth=0.5, bg="white")
    integral_frame.place(x=30, y=55, width=250, height=150)
    integral_var = tk.StringVar(value="option1")
    tk.Radiobutton(
        integral_frame,
        text="1 Интеграл", fg="black",
        variable=integral_var,
        value="option1",
        justify=tk.LEFT,
        bg="white",
    ).place(x=10, y=20)
    tk.Radiobutton(
        integral_frame,
        text="2 Интеграл", fg="black",
        variable=integral_var,
        value="option2",
        justify=tk.LEFT,
        bg="white",
    ).place(x=10, y=70)
    return integral_var


# 2 часть: раздел нелинейных уравнений
def create_nonlinear_section(root):
    tk.Label(root, text="2 - Нелинейные уравнения", font=("Arial", 14), bg="white").place(x=30, y=240)
    nonlinear_frame = tk.LabelFrame(root, text="Выберите уравнение", relief="solid", borderwidth=0.5, bg="white")
    nonlinear_frame.place(x=30, y=275, width=250, height=205)
    nonlinear_var = tk.StringVar(value="eq1")
    tk.Radiobutton(
        nonlinear_frame,
        text="3x⁴ + 8x³ + 6x² - 10 = 0", fg="black",
        variable=nonlinear_var,
        value="eq1",
        justify=tk.LEFT,
        bg="white",
    ).place(x=10, y=20)
    tk.Radiobutton(
        nonlinear_frame,
        text="3ˣ - 2x - 5 = 0", fg="black",
        variable=nonlinear_var,
        value="eq2",
        justify=tk.LEFT,
        bg="white",
    ).place(x=10, y=60)
    tk.Radiobutton(
        nonlinear_frame,
        text="2x² - 0.5ˣ - 3 = 0", fg="black",
        variable=nonlinear_var,
        value="eq3",
        justify=tk.LEFT,
        bg="white",
    ).place(x=10, y=100)
    tk.Radiobutton(
        nonlinear_frame,
        text="x·log(x + 1) = 1", fg="black",
        variable=nonlinear_var,
        value="eq4",
        justify=tk.LEFT,
        bg="white",
    ).place(x=10, y=140)
    return nonlinear_var


# 1 часть: открытие файла "1 часть.py"
def open_integral(root, integral_var):
    try:
        integral_module = load_module("1 часть.py", "integral_part")
        if integral_var.get() == "option1":
            integral_module.open_integral_window(
                root,
                "Интеграл 1",
                integral_module.integral_f1,
                integral_module.A1_DEFAULT,
                integral_module.B1_DEFAULT,
                need_domain_check=True,
            )
        else:
            integral_module.open_integral_window(
                root,
                "Интеграл 2",
                integral_module.integral_f2,
                integral_module.A2_DEFAULT,
                integral_module.B2_DEFAULT,
            )
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть интегралы:\n{e}")


# 2 часть: открытие файла "2 часть.py"
def open_nonlinear(root, nonlinear_var):
    try:
        nonlinear_module = load_module("2 часть.py", "nonlinear_part")
        nonlinear_module.open_nonlinear_window(root, nonlinear_var.get())
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть нелинейные уравнения:\n{e}")


# 3 часть: открытие файла "часть 3 (1).py" с интерполяцией
def open_interpolation(root):
    try:
        interp_module = load_module("часть 3.py", "interpolation_part")
        interp_module.open_interpolation_window(root)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть интерполяцию:\n{e}")


# 4 часть: открытие файла "4 часть.py" с МНК
def open_mnk(root):
    try:
        mnk_module = load_module("4 часть.py", "mnk_part")
        mnk_module.mnk(root)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть МНК:\n{e}")


# 5 часть: открытие файла "часть 5.py" с МКР
def open_mkr(root):
    try:
        mkr_module = load_module("часть 5.py", "mkr_part")
        mkr_module.mkr(root)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть МКР:\n{e}")


def create_buttons(root, integral_var, nonlinear_var):
    tk.Button(
        root,
        text="Открыть интеграл",
        command=lambda: open_integral(root, integral_var),
        height=2,
        width=22
    ).place(x=340, y=95)
    tk.Button(
        root,
        text="Открыть уравнение",
        command=lambda: open_nonlinear(root, nonlinear_var),
        height=2,
        width=22
    ).place(x=340, y=345)
    # 3 часть: кнопка интерполяции
    tk.Button(
        root,
        text="Открыть интерполяцию",
        command=lambda: open_interpolation(root),
        height=2,
        width=22
    ).place(x=340, y=445)
    tk.Button(
        root,
        text="Открыть МНК",
        command=lambda: open_mnk(root),
        height=2,
        width=22
    ).place(x=340, y=500)
    tk.Button(
        root,
        text="Открыть МКР",
        command=lambda: open_mkr(root),
        height=2,
        width=22
    ).place(x=340, y=555)
    #Об авторе
    tk.Button(
        root,
        text="Об авторе",
        command=lambda: readme.open_about_window(root),
        height=2,
        width=22
    ).place(x=340, y=610)
    # Кнопка выхода
    tk.Button(
        root,
        text="Выход",
        command=root.destroy,
        height=2,
        width=22
    ).place(x=340, y=665)


def main():
    root = tk.Tk()
    root.title("Курсовая работа")
    root.geometry("960x740")
    root.configure(bg="white")
    root.resizable(False, False)

    # Крокодил: запускаем фон перед созданием кнопок
    create_crocodile_background(root)

    # 1 часть и 2 часть: создаём блоки выбора
    integral_var = create_integral_section(root)
    nonlinear_var = create_nonlinear_section(root)
    # Кнопки открытия окон
    create_buttons(root, integral_var, nonlinear_var)

    root.mainloop()


if __name__ == "__main__":
    main()
