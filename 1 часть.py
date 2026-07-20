import tkinter as tk
from tkinter import ttk

import math
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MultipleLocator

A1_DEFAULT = 0.5
B1_DEFAULT = 1.8
A2_DEFAULT = 0.4
B2_DEFAULT = 1.2
N_DEFAULT = 20

EPS_DEFAULT = 0.001
N_MIN = 2

def parse_float(text):
    text = text.strip().replace(",", ".")

    if text == "":
        raise ValueError("Поле пустое")

    value = float(text)

    if not math.isfinite(value):
        raise ValueError("Некорректное число")

    return value

def validate_integral_interval(a, b, n):
    if a >= b:
        raise ValueError("Нужно чтобы a < b")
    if n < N_MIN:
        raise ValueError(f"Нужно чтобы n >= {N_MIN}")


def validate_integral_f1_domain(a):
    xmin = 1.4 / 6.8
    if a < xmin:
        raise ValueError(f"Для f(x) нужно a >= {xmin:.6f}")


def validate_function_on_interval(f, a, b, samples=200):
    xs = np.linspace(a, b, samples)
    ys = f(xs)
    if not np.all(np.isfinite(ys)):
        raise ValueError("Функция на отрезке даёт NaN/Inf")


def pick_major_step(deleniya: float) -> float:
    if deleniya <= 0:
        return 0.2
    steps = [0.2, 0.5, 1.0]
    return min(steps, key=lambda step: abs(deleniya / step - 8))


def setup_axes(ax, xlim, ylim):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.spines["left"].set_position(("data", 0))
    ax.spines["bottom"].set_position(("data", 0))
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")
    ax.spines["left"].set_linewidth(2)
    ax.spines["bottom"].set_linewidth(2)
    ax.set_aspect("equal", adjustable="box")


def label_axes(ax):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.text(x1 - (x1 - x0) * 0.05, 0, "x", fontsize=12, fontweight="bold", va="bottom")
    ax.text(-0.05 * (x1 - x0), y1 - (y1 - y0) * 0.06, "y", fontsize=12, fontweight="bold", ha="right")


def draw_integral_graph(ax, canvas, f, a, b, title):
    ax.clear()
    ax.set_title(title)
    xs = np.linspace(a, b, max(1500, min(int(1500 + abs(b - a) * 2000), 12000)))
    ys = f(xs)
    major = pick_major_step(max(abs(b - a), 1.0))
    minor = major / 5.0
    half = 5 * major
    center_x = (a + b) / 2.0
    setup_axes(ax, (min(center_x - half, 0.0), max(center_x + half, 0.0)), (min(-half, 0.0), max(half, 0.0)))
    ax.xaxis.set_major_locator(MultipleLocator(major))
    ax.yaxis.set_major_locator(MultipleLocator(major))
    ax.xaxis.set_minor_locator(MultipleLocator(minor))
    ax.yaxis.set_minor_locator(MultipleLocator(minor))
    ax.grid(True, which="major", linewidth=1, alpha=0.85)
    ax.grid(True, which="minor", linewidth=0.4, alpha=0.35)
    ax.plot(xs, ys, linewidth=2)
    label_axes(ax)
    canvas.draw()


def integral_f1(x):
    x = np.asarray(x)
    return np.sqrt(0.7 * x ** 2 + 2.3) / (3.2 + np.sqrt(6.8 * x - 1.4))


def integral_f2(x):
    x = np.asarray(x)
    return np.cos(0.4 * x + 0.6) / (0.8 + (np.sin(x + 0.5) ** 2))


def integrate_left(f, a, b, n):
    h = (b - a) / n
    return sum(float(f(a + i * h)) for i in range(n)) * h


def integrate_right(f, a, b, n):
    h = (b - a) / n
    return sum(float(f(a + i * h)) for i in range(1, n + 1)) * h


def integrate_midpoint(f, a, b, n):
    h = (b - a) / n
    return sum(float(f(a + (i + 0.5) * h)) for i in range(n)) * h


def integrate_trapezoid(f, a, b, n):
    h = (b - a) / n
    s = 0.5 * (float(f(a)) + float(f(b)))
    for i in range(1, n):
        s += float(f(a + i * h))
    return s * h


def integrate_simpson(f, a, b, n):
    if n % 2 != 0:
        raise ValueError("Для метода Симпсона n должно быть чётным")
    h = (b - a) / n
    s = float(f(a)) + float(f(b))
    for i in range(1, n):
        s += (4 if i % 2 else 2) * float(f(a + i * h))
    return s * h / 3


def runge(f, a, b, n, integrate_func, p):
    i_n = integrate_func(f, a, b, n)
    i_2n = integrate_func(f, a, b, 2 * n)
    return i_n, i_2n, abs(i_2n - i_n) / (2 ** p - 1)


def open_integral_window(root, title, f, a0, b0, need_domain_check=False):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("1150x940")
    win.configure(bg="white")
    win.resizable(False, False)

    style = ttk.Style(win)
    style.theme_use("alt")
    style.configure("Nice.TButton", padding=(12, 4), font=("Segoe UI", 11))
    style.configure("Nice.TLabel", background="white", font=("Segoe UI", 11))
    style.configure("Nice.TEntry", font=("Segoe UI", 10))

    left = tk.Frame(win, bg="white", width=360)
    left.grid(row=0, column=0, sticky="nsew")
    left.grid_propagate(False)
    left.grid_rowconfigure(2, weight=1)

    right = tk.Frame(win, bg="white")
    right.grid(row=0, column=1, sticky="nsew")
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(1, weight=1)

    header = tk.Frame(left, bg="white")
    header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
    header.grid_columnconfigure(1, weight=1)

    ttk.Label(header, text="a =", style="Nice.TLabel").grid(row=0, column=0, sticky="w", pady=6)
    ttk.Label(header, text="b =", style="Nice.TLabel").grid(row=1, column=0, sticky="w", pady=6)
    ttk.Label(header, text="n =", style="Nice.TLabel").grid(row=2, column=0, sticky="w", pady=6)

    entry_a = ttk.Entry(header, style="Nice.TEntry")
    entry_b = ttk.Entry(header, style="Nice.TEntry")
    entry_n = ttk.Entry(header, style="Nice.TEntry")

    ttk.Label(header, text="e =", style="Nice.TLabel").grid(row=3, column=0, sticky="w", pady=6)
    entry_eps = ttk.Entry(header, style="Nice.TEntry")
    entry_eps.grid(row=3, column=1, sticky="ew", pady=6, padx=(10, 0))
    entry_eps.insert(0, str(EPS_DEFAULT))

    entry_a.grid(row=0, column=1, sticky="ew", pady=6, padx=(10, 0))
    entry_b.grid(row=1, column=1, sticky="ew", pady=6, padx=(10, 0))
    entry_n.grid(row=2, column=1, sticky="ew", pady=6, padx=(10, 0))
    entry_a.insert(0, str(a0))
    entry_b.insert(0, str(b0))
    entry_n.insert(0, str(N_DEFAULT))

    msg = tk.Label(left, text="", fg="black", justify="left", anchor="nw", height=6, bg="white")
    msg.grid(row=1, column=0, sticky="ew", padx=20, pady=(6, 8))


    def show_message(text, is_error=False):
        msg.config(text=text, fg=("red" if is_error else "black"))

    # ----------------------------------------------
    # Вспомогательные функции для поиска общего n_min
    # ----------------------------------------------
    def compute_n_for_method(integrate_func, p, require_even, eps_val, a_val, b_val):
        """Возвращает минимальное n (>=N_MIN) для одного метода, дающее погрешность Рунге < eps_val."""
        n = N_MIN
        if require_even and n % 2 != 0:
            n += 1
        max_n = 200000
        while n <= max_n:
            try:
                I_n = integrate_func(f, a_val, b_val, n)
                I_2n = integrate_func(f, a_val, b_val, 2*n)
                r = abs(I_2n - I_n) / (2**p - 1)
                if r < eps_val:
                    return n
            except Exception:
                pass
            if require_even:
                n *= 2
            else:
                n += 1
        raise ValueError(f"Не удалось подобрать n до {max_n} для метода {integrate_func.__name__}")

    def compute_common_n_min():
        vals = get_values()
        if vals is None:
            return
        a_val, b_val, _ = vals
        try:
            eps_val = parse_float(entry_eps.get())
            if eps_val <= 0:
                raise ValueError("Точность должна быть положительной")
        except Exception as e:
            show_message(f"Ошибка в точности: {e}", True)
            return

        # Все методы: (функция, порядок, чётность, русское имя)
        methods = [
            (integrate_simpson, 4, True, "Simpson", "Симпсон"),
            (integrate_trapezoid, 2, True, "Trapezoid", "Трапеция"),
            (integrate_midpoint, 2, True, "Midpoint", "Прямоугольники (средние)"),
            (integrate_right, 1, True, "Right", "Правые прямоугольники"),
            (integrate_left,  1, True, "Left", "Левые прямоугольники")
        ]

        # 1. Быстрый старт: находим минимальные n по правилу Рунге
        ns = []
        for meth, p, even, eng_name, rus_name in methods:
            try:
                n_meth = compute_n_for_method(meth, p, even, eps_val, a_val, b_val)
                ns.append(n_meth)
                print(f"{rus_name}: n_min (Рунге) = {n_meth}")
            except Exception as e:
                show_message(f"Ошибка подбора n для {rus_name}: {e}", True)
                return
        common_n = max(ns)
        if common_n % 2 != 0:
            common_n += 1

        # 2. Увеличиваем n, пока int(результат * 1000) не станет одинаков для всех
        max_n = 200000
        while common_n <= max_n:
            values = []
            ok = True
            for meth, _, _, eng_name, rus_name in methods:
                try:
                    val = meth(f, a_val, b_val, common_n)
                    values.append(val)
                except Exception as e:
                    show_message(f"Ошибка вычисления {rus_name} при n={common_n}: {e}", True)
                    ok = False
                    break
            if not ok:
                return

            int_vals = [int(v * 1000) for v in values]
            if all(iv == int_vals[0] for iv in int_vals):
                break
            common_n += 1
            if common_n % 2 != 0:
                common_n += 1
        else:
            show_message(f"Не удалось достичь совпадения целых частей до n={max_n}", True)
            return

        # Устанавливаем найденное n и обновляем график
        set_n(common_n)
        redraw_graph()

        # Выводим результаты всех методов (только значения, без x1000)
        results = []
        for (meth, _, _, eng_name, rus_name), val in zip(methods, values):
            results.append(f"{rus_name}: {val:.10f}")
        msg_text = f"Общее n(min) = {common_n}\n" + "\n".join(results)
        show_message(msg_text)


    fig = Figure(figsize=(7.8, 5.8), dpi=120)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=right)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def get_values():
        try:
            a = parse_float(entry_a.get())
            b = parse_float(entry_b.get())
            n = int(entry_n.get())
            validate_integral_interval(a, b, n)
            if need_domain_check:
                validate_integral_f1_domain(a)
            validate_function_on_interval(f, a, b)
            return a, b, n
        except Exception as e:
            show_message(f"Ошибка: {e}", True)
            return None

    def redraw_graph():
        vals = get_values()
        if vals is None:
            return
        a, b, _ = vals
        draw_integral_graph(ax, canvas, f, a, b, f"График {title}")
        show_message("График обновлён")

    def safe_action(action):
        try:
            action()
        except Exception as e:
            show_message(f"Ошибка: {e}", True)

    def set_n(value):
        entry_n.delete(0, tk.END)
        entry_n.insert(0, str(value))

    def nmin_simpson():
        return 2

    def show_result(calc_func, label):
        vals = get_values()
        if vals is None:
            return
        a, b, n = vals
        show_message(f"{label} = {calc_func(f, a, b, n)}")

    def show_runge(calc_func, p, require_even, label):
        vals = get_values()
        if vals is None:
            return
        a, b, n = vals
        if require_even and n % 2 != 0:
            raise ValueError("n должно быть чётным")
        i_n, i_2n, r = runge(f, a, b, n, calc_func, p)
        show_message(f"{label}\n"
                     f"n={n}\n"
                     f"I(n)={i_n}\n"
                     f"I(2n)={i_2n}\n"
                     f"R≈{r}")

    def autoselect_n(integrate_func, p, require_even, method_name):
        vals = get_values()
        if vals is None:
            return
        a, b, _ = vals
        try:
            eps = parse_float(entry_eps.get())
            if eps <= 0:
                raise ValueError("Точность должна быть положительной")
        except Exception as e:
            show_message(f"Ошибка в точности: {e}", True)
            return

        n = N_MIN
        if require_even and n % 2 != 0:
            n += 1
        max_n = 200000
        while n <= max_n:
            try:
                i_n = integrate_func(f, a, b, n)
                i_2n = integrate_func(f, a, b, 2 * n)
                r = abs(i_2n - i_n) / (2 ** p - 1)
                if r < eps:
                    entry_n.delete(0, tk.END)
                    entry_n.insert(0, str(n))
                    redraw_graph()
                    result = integrate_func(f, a, b, n)
                    show_message(f"{method_name} = {result}")
                    return
                n *= 2
            except Exception as e:
                show_message(f"Ошибка при n={n}: {e}", True)
                return

        show_message(f"{method_name}: не удалось подобрать n до {max_n}", True)

    buttons = tk.Frame(left, bg="white")
    buttons.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
    buttons.grid_columnconfigure(0, weight=1)

    def make_autoselect_callback(integrate_func, p, require_even, method_name):
        return lambda: safe_action(lambda: autoselect_n(integrate_func, p, require_even, method_name))

    def add_button(row, text, callback, nmin_callback):
        ttk.Button(buttons, text=text, style="Nice.TButton", command=lambda: safe_action(callback)).grid(row=row, column=0, sticky="ew", pady=3)
        ttk.Button(buttons, text="n(min)", style="Nice.TButton", command=nmin_callback).grid(row=row, column=1, sticky="e", padx=(10, 0), pady=3)


    add_button(0, "Метод Симпсона",
               lambda: show_result(integrate_simpson, "Метод Симпсона"),
               make_autoselect_callback(integrate_simpson, 4, True, "Симпсон"))

    add_button(1, "Метод трапеции",
               lambda: show_result(integrate_trapezoid, "Метод трапеции"),
               make_autoselect_callback(integrate_trapezoid, 2, False, "трапеции"))

    add_button(2, "Метод прямоугольников",
               lambda: show_result(integrate_midpoint, "Метод прямоугольников"),
               make_autoselect_callback(integrate_midpoint, 2, False, "прямоугольников (средние)"))

    add_button(3, "Через правые прямоугольники",
               lambda: show_result(integrate_right, "Метод правых прямоугольников"),
               make_autoselect_callback(integrate_right, 1, False, "правых прямоугольников"))

    add_button(4, "Через левые прямоугольники",
               lambda: show_result(integrate_left, "Метод левых прямоугольников"),
               make_autoselect_callback(integrate_left, 1, False, "левых прямоугольников"))

    # ----- Новая кнопка для общего n_min -----
    ttk.Button(buttons, text="Общее n(min)", style="Nice.TButton",
               command=lambda: safe_action(compute_common_n_min)).grid(row=5, column=0, columnspan=2, sticky="ew", pady=6)

    ttk.Separator(buttons, orient='horizontal').grid(row=6, column=0, columnspan=2, sticky="ew", pady=12)

    def runge_simpson():
        safe_action(lambda: show_runge(integrate_simpson, 4, True, "Рунге (Симпсон)"))
    def runge_trapezoid():
        safe_action(lambda: show_runge(integrate_trapezoid, 2, False, "Рунге (Трапеции)"))

    def runge_midpoint():
        safe_action(lambda: show_runge(
            integrate_midpoint,
            2,
            False,
            "Рунге (Средние прямоугольники)"
        ))

    def runge_right():
        safe_action(lambda: show_runge(
            integrate_right,
            1,
            False,
            "Рунге (Правые прямоугольники)"
        ))

    def runge_left():
        safe_action(lambda: show_runge(
            integrate_left,
            1,
            False,
            "Рунге (Левые прямоугольники)"
        ))

    ttk.Button(buttons, text="Рунге (Симпсон)", style="Nice.TButton", command=runge_simpson).grid(row=7, column=0, columnspan=2, sticky="ew", pady=6)
    ttk.Button(buttons, text="Рунге (Трапеции)", style="Nice.TButton", command=runge_trapezoid).grid(row=8, column=0, columnspan=2, sticky="ew", pady=6)
    ttk.Button(
        buttons,
        text="Рунге (Средние прямоугольники)",
        style="Nice.TButton",
        command=runge_midpoint
    ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=6)

    ttk.Button(
        buttons,
        text="Рунге (Правые прямоугольники)",
        style="Nice.TButton",
        command=runge_right
    ).grid(row=10, column=0, columnspan=2, sticky="ew", pady=6)

    ttk.Button(
        buttons,
        text="Рунге (Левые прямоугольники)",
        style="Nice.TButton",
        command=runge_left
    ).grid(row=11, column=0, columnspan=2, sticky="ew", pady=6)

    ttk.Separator(buttons, orient='horizontal').grid(row=12, column=0, columnspan=2, sticky="ew", pady=12)

    ttk.Button(buttons, text="Обновить график", style="Nice.TButton", command=lambda: safe_action(redraw_graph)).grid(row=13, column=0, columnspan=2, sticky="ew", pady=6)
    ttk.Button(buttons, text="Закрыть", style="Nice.TButton", command=win.destroy).grid(row=14, column=0, columnspan=2, sticky="ew", pady=6)

    win.after(50, lambda: safe_action(compute_common_n_min))

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_integral_window(root, "Интеграл 1", integral_f1, A1_DEFAULT, B1_DEFAULT, need_domain_check=True)
    root.mainloop()
