import math
from decimal import Decimal, ROUND_HALF_UP

import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator, FuncFormatter


MAX_ITER = 500000
DEFAULT_INTERVALS = {
    "eq1": ("0", "1"),
    "eq2": ("1", "2"),
    "eq3": ("1", "2"),
    "eq4": ("1", "2"),
}


def parse_float(text):
    text = text.strip().replace(",", ".")

    if text == "":
        raise ValueError("Поле пустое")

    value = float(text)

    if not math.isfinite(value):
        raise ValueError("Некорректное число")

    return value


def safe_value(val):
    return not (math.isnan(val) or math.isinf(val))


def method_error(message):
    return {"error": message}


def calc_round(value, digits=10):
    q = Decimal("1." + "0" * digits)
    return float(Decimal(str(value)).quantize(q, rounding=ROUND_HALF_UP))


def roundup(x):
    return math.ceil(x) if x >= 0 else math.floor(x)


def roundup_tens(x):
    return math.ceil(x / 10) * 10 if x >= 0 else math.floor(x / 10) * 10


def choose_M_for_iterations(max_abs_df):
    m = roundup(max_abs_df) if max_abs_df < 10 else roundup_tens(max_abs_df)
    return abs(m or 1)


def eq1_func(x):
    return 3 * x ** 4 + 8 * x ** 3 + 6 * x ** 2 - 10


def eq1_df(x):
    return 12 * x ** 3 + 24 * x ** 2 + 12 * x


def eq1_d2f(x):
    return 36 * x ** 2 + 48 * x + 12


def eq2_func(x):
    return 3 ** x - 2 * x - 5


def eq2_df(x):
    return 3 ** x * math.log(3) - 2


def eq2_d2f(x):
    return 3 ** x * (math.log(3) ** 2)


def eq3_func(x):
    return 2 * x ** 2 - (0.5 ** x) - 3


def eq3_df(x):
    return 4 * x + math.log(2) * (0.5 ** x)


def eq3_d2f(x):
    return 4 - (math.log(2) ** 2) * (0.5 ** x)


def eq4_func(x):
    if x <= -1:
        return float("nan")
    return x * math.log(x + 1) - 1


def eq4_df(x):
    if x <= -1:
        return float("nan")
    return math.log(x + 1) + x / (x + 1)


def eq4_d2f(x):
    if x <= -1:
        return float("nan")
    return (x + 2) / ((x + 1) ** 2)


def get_equation_data(eq_key):
    mapping = {
        "eq1": (eq1_func, eq1_df, eq1_d2f, 1, "Уравнение: 3x⁴ + 8x³ + 6x² - 10 = 0"),
        "eq2": (eq2_func, eq2_df, eq2_d2f, 2, "Уравнение: 3ˣ - 2x - 5 = 0"),
        "eq3": (eq3_func, eq3_df, eq3_d2f, 3, "Уравнение: 2x² - 0.5ˣ - 3 = 0"),
        "eq4": (eq4_func, eq4_df, eq4_d2f, 4, "Уравнение: x·log(x + 1) = 1"),
    }
    return mapping.get(eq_key, mapping["eq1"])


def check_domain_on_interval(f, a, b):
    return all(safe_value(f(x)) for x in np.linspace(a, b, 200))


def nonlinear_grid_step(diapazon):
    if diapazon <= 0:
        return 0.1
    variants = [0.1, 0.2, 0.5, 1, 2, 5]
    return min(variants, key=lambda step: abs(diapazon / step - 8))


def format_tick(x, pos):
    if abs(x) < 1e-10:
        x = 0
    return f"{int(round(x))}" if abs(x - round(x)) < 1e-10 else f"{x:.1f}"


def format_axes(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")


def label_axes(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    dx = x1 - x0
    dy = y1 - y0
    ax.text(x1 - 0.035 * dx, 0 + 0.03 * dy, "x", fontsize=12)
    ax.text(0 + 0.02 * dx, y1 - 0.04 * dy, "y", fontsize=12)


def pick_bounds(xs, ys, equation_number):
    x_min_real = min(xs.min(), 0)
    x_max_real = max(xs.max(), 0)
    y_min_real = min(ys.min(), 0)
    y_max_real = max(ys.max(), 0)

    if abs(x_max_real - x_min_real) < 1e-12:
        x_min_real -= 1
        x_max_real += 1

    if abs(y_max_real - y_min_real) < 1e-12:
        y_min_real -= 1
        y_max_real += 1

    common = max(x_max_real - x_min_real, y_max_real - y_min_real) * 1.08
    if not safe_value(common):
        common = 10
    major = nonlinear_grid_step(common)
    half_range = max(6, min(10, math.ceil(common / major))) * major / 2

    x_center = (x_min_real + x_max_real) / 2
    y_center = (y_min_real + y_max_real) / 2

    x_min = x_center - half_range
    x_max = x_center + half_range
    y_min = y_center - half_range
    y_max = y_center + half_range

    if equation_number == 4 and x_min <= -1:
        x_min = -0.999
        x_max = x_min + 2 * half_range

    return x_min, x_max, y_min, y_max, major


def dichotomy_method(f, a, b, eps, max_iter=MAX_ITER):
    fa = f(a)
    fb = f(b)

    if not safe_value(fa) or not safe_value(fb):
        return method_error("f(a) или f(b) не определено"), None
    if fa == 0:
        return a, 0
    if fb == 0:
        return b, 0
    if fa * fb > 0:
        return method_error("на [a;b] нет смены знака"), None

    for i in range(1, max_iter + 1):
        c = (a + b) / 2
        fc = f(c)

        if not safe_value(fc):
            return method_error("f(c) не определено"), None

        if abs(b - a) / 2 < eps or abs(fc) < eps:
            return c, i

        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

    return method_error("превышено число итераций"), None


def newton_method(f, df, a, b, eps, max_iter=MAX_ITER):
    x_prev = (a + b) / 2

    for i in range(1, max_iter + 1):
        fx = f(x_prev)
        dfx = df(x_prev)

        if not safe_value(fx):
            return method_error("f(x) не определено"), None
        if not safe_value(dfx) or abs(dfx) < 1e-14:
            return method_error("f'(x) недопустимо"), None

        dx = fx / dfx
        x_new = x_prev - dx
        if not safe_value(x_new):
            return method_error("x вышел за допустимую область"), None

        if abs(f(x_new)) < eps:

            if x_new < a or x_new > b:
                return method_error("корень вышел за пределы интервала"), None

            return x_new, i
        x_prev = x_new

    return method_error("превышено число итераций"), None


def chord_method(f, d2f, a, b, eps, max_iter=MAX_ITER):
    fa = f(a)
    fb = f(b)

    if not safe_value(fa) or not safe_value(fb):
        return method_error("f(a) или f(b) не определено"), None
    if fa == 0:
        return a, 0
    if fb == 0:
        return b, 0
    if fa * fb > 0:
        return method_error("на [a;b] нет смены знака"), None

    d2a = d2f(a)
    d2b = d2f(b)

    if fa * d2a > 0:
        fixed, x_prev = a, b
    elif fb * d2b > 0:
        fixed, x_prev = b, a
    else:
        return method_error("не удалось выбрать неподвижную точку"), None

    f_fixed = f(fixed)

    for i in range(1, max_iter + 1):
        fx = f(x_prev)
        denom = fx - f_fixed

        if not safe_value(fx) or abs(denom) < 1e-10:
            return method_error("ошибка в методе хорд"), None

        x_new = x_prev - fx * (x_prev - fixed) / denom

        if abs(x_new - x_prev) < eps:
            return x_new, i

        x_prev = x_new

    return method_error("превышено число итераций"), None


def combined_method(f, df, d2f, a, b, eps, max_iter=MAX_ITER):
    fa = f(a)
    fb = f(b)

    if not safe_value(fa) or not safe_value(fb):
        return method_error("f(a) или f(b) не определено"), None

    if fa == 0:
        return a, 0
    if fb == 0:
        return b, 0

    if fa * fb > 0:
        return method_error("на [a;b] нет смены знака"), None

    d2a = d2f(a)
    d2b = d2f(b)

    if not safe_value(d2a) or not safe_value(d2b):
        return method_error("f''(x) не определено"), None

    if fa * d2a > 0:
        x_newton, x_chord, fixed = a, b, a
    elif fb * d2b > 0:
        x_newton, x_chord, fixed = b, a, b
    else:
        return method_error("не удалось выбрать сторону"), None

    f_fixed = f(fixed)

    for i in range(1, max_iter + 1):
        fx = f(x_newton)
        dfx = df(x_newton)
        fx_chord = f(x_chord)
        denom = fx_chord - f_fixed

        if not safe_value(fx) or not safe_value(dfx) or abs(dfx) < 1e-14:
            return method_error("ошибка в части касательных"), None

        if not safe_value(fx_chord) or abs(denom) < 1e-10:
            return method_error("ошибка в части хорд"), None

        x_newton_new = x_newton - fx / dfx
        x_chord_new = x_chord - fx_chord * (x_chord - fixed) / denom

        x_mid = (x_newton_new + x_chord_new) / 2
        if x_mid < a or x_mid > b:
            return method_error("корень вышел за пределы интервала"), None

        if abs(f(x_mid)) < eps:
            return x_mid, i

        x_newton, x_chord = x_newton_new, x_chord_new

    return method_error("превышено число итераций"), None

def iteration_method(f, df, a, b, eps, max_iter=MAX_ITER):
    fa = f(a)
    fb = f(b)
    if not safe_value(fa) or not safe_value(fb):
        return method_error("f(a) или f(b) не определено"), None
    if fa * fb > 0:
        return method_error("на [a;b] нет смены знака, метод итераций неприменим"), None
    try:
        xs = np.linspace(a, b, 400)
        df_vals = np.array([df(x) for x in xs], dtype=float)

        if not np.all(np.isfinite(df_vals)):
            return method_error("производная не определена"), None

        min_df = np.min(df_vals)
        max_df = np.max(df_vals)
        max_abs_df = max(abs(min_df), abs(max_df))

        if max_abs_df < 1e-12:
            return method_error("производная всюду близка к нулю"), None

        m = choose_M_for_iterations(max_abs_df)

        # Проверка условия сходимости
        q_values = np.abs(1 - df_vals / m)
        if np.max(q_values) >= 1:
            return method_error("условие сходимости нарушено"), None

        x_prev = (a + b) / 2

        for i in range(1, max_iter + 1):
            fx = f(x_prev)
            if not safe_value(fx):
                return method_error("f(x) не определено"), None
            x_new = x_prev - fx / m
            if x_new < a or x_new > b:
                return method_error("корень вышел за пределы интервала"), None
            if not safe_value(x_new):
                return method_error("x вышел за допустимую область"), None

            if x_new <= -1 and f == eq4_func:
                return method_error("x вышел за область определения"), None
            if abs(x_new - x_prev) < eps or abs(f(x_new)) < eps:
                return x_new, i
            x_prev = x_new

        return method_error("превышено число итераций"), None



    except Exception as e:
        return method_error(f"внутренняя ошибка: {e}"), None

def open_nonlinear_window(root, default_eq="eq1"):
    f, df, d2f, equation_number, equation_title = get_equation_data(default_eq)
    default_a, default_b = DEFAULT_INTERVALS.get(default_eq, DEFAULT_INTERVALS["eq1"])

    win = tk.Toplevel(root)
    win.title("Нелинейные уравнения")
    win.geometry("780x960")
    win.minsize(780, 960)
    win.configure(bg="#f4f6f8")

    style = ttk.Style(win)
    style.theme_use("clam")
    style.configure("MainNU.TFrame", background="#f4f6f8")
    style.configure("CardNU.TLabelframe", background="#ffffff", borderwidth=1)
    style.configure(
        "CardNU.TLabelframe.Label",
        font=("Segoe UI", 10, "bold"),
        foreground="#1f2937",
        background="#ffffff",
    )
    style.configure("TitleNU.TLabel", font=("Segoe UI", 18, "bold"), background="#f4f6f8", foreground="#111827")
    style.configure("TextNU.TLabel", font=("Segoe UI", 10), background="#ffffff", foreground="#111827")
    style.configure("HintNU.TLabel", font=("Segoe UI", 9), background="#ffffff", foreground="#6b7280")
    style.configure("ResultNameNU.TLabel", font=("Segoe UI", 10, "bold"), background="#ffffff", foreground="#111827")
    style.configure("ResultHeadNU.TLabel", font=("Segoe UI", 10, "bold"), background="#ffffff", foreground="#374151")
    style.configure("ResultValueNU.TLabel", font=("Segoe UI", 10), background="#ffffff", foreground="#1d4ed8")
    style.configure("AccentNU.TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("DangerNU.TButton", font=("Segoe UI", 10, "bold"), padding=8)

    main = ttk.Frame(win, style="MainNU.TFrame", padding=12)
    main.pack(fill="both", expand=True)
    main.columnconfigure(0, weight=0, minsize=250)
    main.columnconfigure(1, weight=1, minsize=480)
    main.rowconfigure(2, weight=1)
    main.rowconfigure(3, weight=1)

    ttk.Label(main, text="Нелинейные уравнения", style="TitleNU.TLabel").grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
    )

    input_frame = ttk.LabelFrame(main, text="Параметры", style="CardNU.TLabelframe", padding=12)
    input_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
    input_frame.columnconfigure(1, weight=1)

    ttk.Label(input_frame, text="a", style="TextNU.TLabel").grid(row=0, column=0, sticky="w", pady=6)
    a_entry = ttk.Entry(input_frame, width=14)
    a_entry.grid(row=0, column=1, sticky="ew", pady=6)
    a_entry.insert(0, default_a)

    ttk.Label(input_frame, text="b", style="TextNU.TLabel").grid(row=1, column=0, sticky="w", pady=6)
    b_entry = ttk.Entry(input_frame, width=14)
    b_entry.grid(row=1, column=1, sticky="ew", pady=6)
    b_entry.insert(0, default_b)

    ttk.Label(input_frame, text="e", style="TextNU.TLabel").grid(row=2, column=0, sticky="w", pady=6)
    e_entry = ttk.Entry(input_frame, width=14)
    e_entry.grid(row=2, column=1, sticky="ew", pady=6)
    e_entry.insert(0, "0.0001")

    hint_var = tk.StringVar(value="")
    ttk.Label(
        input_frame,
        textvariable=hint_var,
        style="HintNU.TLabel",
        wraplength=210,
        justify="left",
    ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

    equation_info = ttk.LabelFrame(main, text="Выбранное уравнение", style="CardNU.TLabelframe", padding=12)
    equation_info.grid(row=2, column=0, sticky="new", padx=(0, 10), pady=(0, 10))
    ttk.Label(
        equation_info,
        text=equation_title,
        style="TextNU.TLabel",
        wraplength=220,
        justify="left",
    ).grid(row=0, column=0, sticky="w")

    button_frame = ttk.LabelFrame(main, text="Управление", style="CardNU.TLabelframe", padding=12)
    button_frame.grid(row=3, column=0, sticky="ew", padx=(0, 10))
    button_frame.columnconfigure(0, weight=1)

    results_frame = ttk.LabelFrame(main, text="Значения корней по методам", style="CardNU.TLabelframe", padding=12)
    results_frame.grid(row=1, column=1, sticky="ew", pady=(0, 10))
    results_frame.columnconfigure(1, weight=1)
    results_frame.columnconfigure(2, weight=0)

    ttk.Label(results_frame, text="", style="ResultHeadNU.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 12))
    ttk.Label(results_frame, text="Ответ", style="ResultHeadNU.TLabel").grid(row=0, column=1, sticky="w", padx=(0, 20))
    ttk.Label(results_frame, text="К-во итераций", style="ResultHeadNU.TLabel").grid(row=0, column=2, sticky="w")

    answer_labels = {}
    iter_labels = {}
    methods = [
        ("Дихотомия:", "dichotomy_val"),
        ("Хорд:", "chord_val"),
        ("Касательные:", "newton_val"),
        ("Комбинированный:", "combined_val"),
        ("Итерационный:", "iteration_val"),
    ]

    for i, (method_text, key) in enumerate(methods, start=1):
        ttk.Label(results_frame, text=method_text, style="ResultNameNU.TLabel").grid(
            row=i, column=0, sticky="w", pady=6, padx=(0, 12)
        )
        answer_labels[key] = ttk.Label(
            results_frame,
            text="",
            style="ResultValueNU.TLabel",
            wraplength=260,
            justify="left",
        )
        answer_labels[key].grid(row=i, column=1, sticky="w", pady=6, padx=(0, 20))

        iter_labels[key] = ttk.Label(results_frame, text="", style="ResultValueNU.TLabel")
        iter_labels[key].grid(row=i, column=2, sticky="w", pady=6)

    graph_frame = ttk.LabelFrame(main, text="График функции", style="CardNU.TLabelframe", padding=6)
    graph_frame.grid(row=2, column=1, rowspan=2, sticky="nsew")
    graph_frame.rowconfigure(0, weight=1)
    graph_frame.columnconfigure(0, weight=1)

    plot_container = ttk.Frame(graph_frame)
    plot_container.grid(row=0, column=0, sticky="nsew")

    def plot_function():
        for widget in plot_container.winfo_children():
            widget.destroy()

        try:
            a = parse_float(a_entry.get())
            b = parse_float(b_entry.get())
        except Exception:
            a, b = float(default_a), float(default_b)

        if a == b:
            a -= 1
            b += 1

        padding = max((b - a) * 0.22, 0.35)
        x_min = max(a - padding, -0.99) if equation_number == 4 else a - padding
        x_max = b + padding

        fig = Figure(figsize=(7.2, 7.2), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=plot_container)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        if equation_number == 4:
            xs = np.linspace(max(x_min, -0.999999), x_max, max(2500, min(int(2500 + abs(x_max - x_min) * 2500), 18000)))
        else:
            xs = np.linspace(x_min, x_max, max(2500, min(int(2500 + abs(x_max - x_min) * 2500), 18000)))

        ys = np.array([f(x) for x in xs], dtype=float)
        mask = np.isfinite(ys)
        xs = xs[mask]
        ys = ys[mask]

        if len(xs) == 0:
            canvas.draw()
            return

        x0, x1, y0, y1, major = pick_bounds(xs, ys, equation_number)
        minor = major / 5

        format_axes(ax, (x0, x1), (y0, y1))
        ax.xaxis.set_major_locator(MultipleLocator(major))
        ax.yaxis.set_major_locator(MultipleLocator(major))
        ax.xaxis.set_minor_locator(MultipleLocator(minor))
        ax.yaxis.set_minor_locator(MultipleLocator(minor))
        ax.xaxis.set_major_formatter(FuncFormatter(format_tick))
        ax.yaxis.set_major_formatter(FuncFormatter(format_tick))
        ax.grid(True, which="major", alpha=0.6)
        ax.grid(True, which="minor", alpha=0.25)
        ax.set_aspect("equal", adjustable="box")

        titles = {
            1: "y = 3x⁴ + 8x³ + 6x² - 10",
            2: "y = 3ˣ - 2x - 5",
            3: "y = 2x² - 0.5ˣ - 3",
            4: "y = x·log(x + 1) - 1",
        }
        ax.set_title(titles[equation_number], fontsize=13, pad=10)
        ax.plot(xs, ys, linewidth=2)

        if equation_number == 4:
            ax.axvline(x=-1, linestyle="--", alpha=0.8)

        label_axes(ax)
        ax.tick_params(axis="x", labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        canvas.draw()

    def calculate_all_methods():
        try:
            a = parse_float(a_entry.get())
            b = parse_float(b_entry.get())
            eps = parse_float(e_entry.get())

            def clear_results():
                for key in answer_labels:
                    answer_labels[key].config(text="")
                    iter_labels[key].config(text="")

            if a >= b:
                messagebox.showerror("Ошибка", "a должно быть меньше b", parent=win)
                clear_results()
                return
            if eps <= 0:
                messagebox.showerror("Ошибка", "Точность должна быть положительной", parent=win)
                clear_results()
                return
            if eps >= (b - a):
                messagebox.showerror(
                    "Ошибка",
                    f"Точность eps ({eps}) должна быть строго меньше длины интервала (b-a = {b - a:.6f})",
                    parent=win
                )
                clear_results()
                return
            if not check_domain_on_interval(f, a, b):
                messagebox.showerror(
                    "Ошибка",
                    "Функция не определена на всём интервале",
                    parent=win
                )
                clear_results()
                return

            # основной расчёт (без изменений)
            results = {
                "dichotomy_val": dichotomy_method(f, a, b, eps),
                "newton_val": newton_method(f, df, a, b, eps),
                "chord_val": chord_method(f, d2f, a, b, eps),
                "combined_val": combined_method(f, df, d2f, a, b, eps),
                "iteration_val": iteration_method(f, df, a, b, eps),
            }

            for key, (value, iters) in results.items():
                if isinstance(value, dict):
                    answer_labels[key].config(text=value["error"])
                    iter_labels[key].config(text="-")
                else:
                    answer_labels[key].config(text=f"{calc_round(value, 8):.8f}")
                    iter_labels[key].config(text=str(iters))

            plot_function()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}", parent=win)
            clear_results()  # также очищаем при неожиданной ошибке

    def auto_adjust():
        nonlocal f, equation_number
        try:
            current_a = parse_float(a_entry.get())
            current_b = parse_float(b_entry.get())
            center = (current_a + current_b) / 2
            eps_val = parse_float(e_entry.get())

            # Диапазоны поиска
            if equation_number == 4:
                search_ranges = [(-0.9999, 10.0), (-0.9999, 20.0), (-0.9999, 30.0)]
                points = [10000, 20000, 30000]
            else:
                search_ranges = [(-10.0, 10.0), (-20.0, 20.0), (-50.0, 50.0)]
                points = [10000, 20000, 30000]

            candidates = []  # (расстояние до центра, a, b)

            for (x_min, x_max), n_points in zip(search_ranges, points):
                xs = np.linspace(x_min, x_max, n_points)
                if equation_number == 4:
                    xs = xs[xs > -1]
                    if len(xs) < 2:
                        continue

                for i in range(len(xs) - 1):
                    x1, x2 = xs[i], xs[i+1]
                    f1, f2 = f(x1), f(x2)
                    mid = (x1 + x2) / 2
                    fm = f(mid)
                    if not (safe_value(f1) and safe_value(f2)):
                        continue
                    if (
                            f1 * f2 < 0
                            or abs(f1) < eps_val
                            or abs(f2) < eps_val
                            or abs(fm) < eps_val
                    ):
                        mid = (x1 + x2) / 2
                        dist = abs(mid - center)
                        candidates.append((dist, x1, x2))
                if candidates:
                    break

            if candidates:
                # Выбираем интервал, ближайший к текущему центру
                candidates.sort(key=lambda item: item[0])
                _, best_a, best_b = candidates[0]
                # Расширяем узкий интервал
                if best_b - best_a < 0.05:
                    best_a = best_a - 0.1
                    best_b = best_b + 0.1
                    if equation_number == 4 and best_a <= -1:
                        best_a = -0.9999
                hint_var.set(f"Найден интервал [{best_a:.4f}; {best_b:.4f}]")
            else:
                # Запасные интервалы (без диалога)
                default_intervals = {1: (0.0, 1.0), 2: (1.0, 2.0), 3: (1.0, 2.0), 4: (1.0, 2.0)}
                best_a, best_b = default_intervals.get(equation_number, (-1.0, 1.0))
                hint_var.set(f"Интервал по умолчанию [{best_a:.3f}; {best_b:.3f}]")

            best_a = calc_round(best_a, 4)
            best_b = calc_round(best_b, 4)

            a_entry.delete(0, tk.END)
            a_entry.insert(0, f"{best_a:.4f}")
            b_entry.delete(0, tk.END)
            b_entry.insert(0, f"{best_b:.4f}")

            plot_function()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка автоподбора: {e}", parent=win)

    def clear_all():
        a_entry.delete(0, tk.END)
        a_entry.insert(0, default_a)
        b_entry.delete(0, tk.END)
        b_entry.insert(0, default_b)
        e_entry.delete(0, tk.END)
        e_entry.insert(0, "0.0001")

        for key in answer_labels:
            answer_labels[key].config(text="")
            iter_labels[key].config(text="")

        hint_var.set("")
        plot_function()

    def show_hint(text):
        hint_var.set(text)

    def clear_hint(event=None):
        hint_var.set("")

    ttk.Button(button_frame, text="Вычислить все методы", style="AccentNU.TButton", command=calculate_all_methods).grid(
        row=0, column=0, sticky="ew", pady=4
    )
    ttk.Button(button_frame, text="Автоподбор интервала", command=auto_adjust).grid(
        row=1, column=0, sticky="ew", pady=4
    )
    ttk.Button(button_frame, text="Очистить всё", command=clear_all).grid(
        row=2, column=0, sticky="ew", pady=4
    )
    ttk.Button(button_frame, text="Закрыть окно", style="DangerNU.TButton", command=win.destroy).grid(
        row=3, column=0, sticky="ew", pady=4
    )

    a_entry.bind("<Enter>", lambda e: show_hint("Введите нижнюю границу интервала"))
    b_entry.bind("<Enter>", lambda e: show_hint("Введите верхнюю границу интервала"))
    e_entry.bind("<Enter>", lambda e: show_hint("Введите точность вычислений"))
    a_entry.bind("<Leave>", clear_hint)
    b_entry.bind("<Leave>", clear_hint)
    e_entry.bind("<Leave>", clear_hint)

    plot_function()



    return win

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_nonlinear_window(root, "eq1")
    root.mainloop()
