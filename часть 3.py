import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import math

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


DEF_X = [-0.2, 0.0, 0.2, 0.4, 0.6, 0.8]
DEF_Y = [0.0, -0.2, 0.4, 2.0, 4.0, 4.8]


def to_float(text):
    text = text.strip().replace(",", ".")

    if text == "":
        raise ValueError("Поле пустое")

    value = float(text)

    if not math.isfinite(value):
        raise ValueError("Некорректное число")

    return value


def nice(number, digits=6):
    if abs(number) < 1e-12:
        number = 0.0
    text = f"{number:.{digits}f}".rstrip("0").rstrip(".")
    if text == "":
        return "0"
    return text


def sort_points(xs, ys):
    if len(xs) != len(ys):
        raise ValueError("Количество x и y должно совпадать")

    points = list(zip(xs, ys))
    points.sort(key=lambda item: item[0])

    for i in range(1, len(points)):
        if abs(points[i][0] - points[i - 1][0]) < 1e-8:
            raise ValueError("Одинаковые x вводить нельзя")

    new_x = []
    new_y = []
    for x, y in points:
        new_x.append(x)
        new_y.append(y)

    return new_x, new_y


def lagrange(x, xs, ys):
    n = len(xs)
    result = 0.0

    for i in range(n):
        term = ys[i]
        for j in range(n):
            if j != i:
                term = term * (x - xs[j]) / (xs[i] - xs[j])
        result += term

    return result

def newton(x, xs, ys):
    n = len(xs)
    if n < 2:
        raise ValueError("Недостаточно узлов для интерполяции")

    h = xs[1] - xs[0]
    for i in range(2, n):
        if abs((xs[i] - xs[i-1]) - h) > 1e-10:
            raise ValueError("Метод Ньютона требует равномерного шага между узлами")

    diff = [list(ys)]
    for order in range(1, n):
        prev = diff[-1]
        cur = [prev[i+1] - prev[i] for i in range(len(prev)-1)]
        diff.append(cur)

    # Коэффициенты – первые элементы каждой разности
    coef = [diff[k][0] for k in range(n)]

    if x <= xs[n//2]:
        t = (x - xs[0]) / h
        res = coef[0]
        term = 1.0
        for k in range(1, n):
            term *= (t - (k - 1)) / k
            res += coef[k] * term
    else:
        t = (x - xs[-1]) / h
        res = coef[0]
        coef_back = [diff[k][-1] for k in range(n)]
        res = coef_back[0]
        term = 1.0
        for k in range(1, n):
            term *= (t + (k - 1)) / k
            res += coef_back[k] * term

    return res

def gauss(a, b):
    n = len(a)
    a = [row[:] for row in a]
    b = b[:]

    for i in range(n):
        max_row = i
        for k in range(i + 1, n):
            if abs(a[k][i]) > abs(a[max_row][i]):
                max_row = k

        a[i], a[max_row] = a[max_row], a[i]
        b[i], b[max_row] = b[max_row], b[i]

        if abs(a[i][i]) < 1e-12:
            raise ValueError("Не получается построить полином")

        for k in range(i + 1, n):
            factor = a[k][i] / a[i][i]
            for j in range(i, n):
                a[k][j] = a[k][j] - factor * a[i][j]
            b[k] = b[k] - factor * b[i]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = b[i]
        for j in range(i + 1, n):
            x[i] = x[i] - a[i][j] * x[j]
        x[i] = x[i] / a[i][i]

    return x

def determinant(matrica):
    n = len(matrica)
    a = [row[:] for row in matrica]
    det = 1.0
    for i in range(n):
        max_row = i
        for k in range(i+1, n):
            if abs(a[k][i]) > abs(a[max_row][i]):
                max_row = k
        if max_row != i:
            a[i], a[max_row] = a[max_row], a[i]
            det *= -1
        if abs(a[i][i]) < 1e-12:
            return 0.0
        det *= a[i][i]
        for k in range(i+1, n):
            factor = a[k][i] / a[i][i]
            for j in range(i+1, n):
                a[k][j] -= factor * a[i][j]
    return det

def cramer_solve(A, B):
    n = len(A)
    det_A = determinant(A)
    if abs(det_A) < 1e-12:
        return None
    x = []
    for i in range(n):
        Ai = [row[:] for row in A]
        for j in range(n):
            Ai[j][i] = B[j]
        det_i = determinant(Ai)
        x.append(det_i / det_A)
    return x

def canon_coefs(xs, ys, method="gauss"):
    n = len(xs)
    a = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(xs[i] ** j)
        a.append(row)
    if abs(determinant(a)) < 1e-10 and len(a) > 2:
        raise ValueError("Матрица близка к вырожденной")

    if method == "gauss":
        return gauss(a, ys)
    else:
        coef = cramer_solve(a, ys)
        if coef is None:
            raise ValueError("Матрица вырождена, метод Крамера не применим")
        return coef

def canon(x, xs, ys, method="gauss"):
    coef = canon_coefs(xs, ys, method)
    coef = coef[::-1]

    result = 0.0

    for c in coef:
        result = result * x + c

    return result

def canon_text(xs, ys, method="gauss"):
    coef = canon_coefs(xs, ys, method)
    parts = []
    for i in range(len(coef)):
        c = round(coef[i], 6)
        if abs(c) < 1e-10:
            continue
        if i == 0:
            parts.append(str(c))
        elif i == 1:
            if c == 1:
                parts.append("x")
            elif c == -1:
                parts.append("-x")
            else:
                parts.append(f"{c}*x")
        else:
            if c == 1:
                parts.append(f"x^{i}")
            elif c == -1:
                parts.append(f"-x^{i}")
            else:
                parts.append(f"{c}*x^{i}")
    if not parts:
        return "P(x) = 0"
    text = parts[0]
    for part in parts[1:]:
        if part.startswith("-"):
            text += " - " + part[1:]
        else:
            text += " + " + part
    return "P(x) = " + text

def calculate_values(xs, ys, x, method="gauss"):
    xs, ys = sort_points(xs, ys)
    if len(xs) < 2:
        raise ValueError("Нужно минимум 2 точки")

    lag = lagrange(x, xs, ys)
    try:
        new = newton(x, xs, ys)
    except Exception as e:
        new = str(e)

    can = canon(x, xs, ys, method)
    formula = canon_text(xs, ys, method)

    return xs, ys, lag, new, can, formula


def open_interpolation_window(root=None):
    win = tk.Toplevel(root) if root else tk.Tk()
    win.title("Интерполяция")
    win.geometry("1200x740")
    win.configure(bg="#f4f6f8")

    style = ttk.Style(win)
    style.theme_use("alt")

    main = ttk.Frame(win, padding=12)
    main.pack(fill="both", expand=True)

    main.columnconfigure(0, weight=0, minsize=260)
    main.columnconfigure(1, weight=0, minsize=300)
    main.columnconfigure(2, weight=1)

    ttk.Label(main, text="Интерполяция",).grid(row=0, column=0, columnspan=3, sticky="w", pady=10)

    #ДАННЫЕ
    pts_x = DEF_X.copy()
    pts_y = DEF_Y.copy()
    current_x = 0.1
    current_y = None

    #ЛЕВО
    left = ttk.Frame(main)
    left.grid(row=1, column=0, sticky="ns", padx=(0, 10))

    frame_calc = ttk.LabelFrame(left, text="Точка для интерполяции (x*)",  padding=10)
    frame_calc.pack(fill="x", pady=5)

    entry_calc = ttk.Entry(frame_calc)
    entry_calc.pack(fill="x")
    entry_calc.insert(0, "0.1")

    frame_add = ttk.LabelFrame(left, text="Добавление узлов", padding=10)
    frame_add.pack(fill="x", pady=5)

    entry_x = ttk.Entry(frame_add)
    entry_y = ttk.Entry(frame_add)
    entry_x.pack(fill="x", pady=2)
    entry_y.pack(fill="x", pady=2)

    btn_add = ttk.Button(frame_add, text="Добавить точку")
    btn_add.pack(fill="x", pady=5)

    frame_buttons = ttk.LabelFrame(left, text="Управление",   padding=10)
    frame_buttons.pack(fill="x", pady=5)

    btn_fill = ttk.Button(frame_buttons, text="Заполнить по условию")
    btn_del = ttk.Button(frame_buttons, text="Удалить выбранную")
    btn_clear = ttk.Button(frame_buttons, text="Очистить всё")
    btn_calc = ttk.Button(frame_buttons, text="Рассчитать")



    for b in (btn_fill, btn_del, btn_clear, btn_calc):
        b.pack(fill="x", pady=3)

    # Выбор метода решения СЛАУ для канонического полинома
    slau_frame = ttk.LabelFrame(left, text="Метод решения СЛАУ", padding=5)
    slau_frame.pack(fill="x", pady=5)
    metod_slau = tk.StringVar(value="gauss")
    ttk.Radiobutton(slau_frame, text="Гаусс", variable=metod_slau, value="gauss").pack(anchor="w")
    ttk.Radiobutton(slau_frame, text="Крамер", variable=metod_slau, value="cramer").pack(anchor="w")

    #ЦЕНТР
    center = ttk.LabelFrame(main, text="Табличные данные",   padding=10)
    center.grid(row=1, column=1, sticky="ns", padx=5)

    header = ttk.Frame(center)
    header.pack(fill="x")

    ttk.Label(header, text="X" ).pack(side="left", expand=True)
    ttk.Label(header, text="Y" ).pack(side="right", expand=True)

    listbox = tk.Listbox(center)
    listbox.pack(fill="both", expand=True)

    btn_exit = ttk.Button(left, text="Выход", command=win.destroy)
    btn_exit.pack(fill="x", pady=10)

    #ПРАВО
    right = ttk.Frame(main)
    right.grid(row=1, column=2, sticky="nsew", padx=5)
    right.rowconfigure(1, weight=1)

    frame_result = ttk.LabelFrame(right, text="Значение полинома",   padding=10)
    frame_result.grid(row=0, column=0, sticky="ew", pady=5)

    var_lag = tk.StringVar()
    var_new = tk.StringVar()
    var_can = tk.StringVar()
    formula_var = tk.StringVar(value="P(x) =")

    ttk.Label(frame_result, text="Лагранж:" ).grid(row=0, column=0, sticky="w")
    ttk.Label(frame_result, textvariable=var_lag,  ).grid(row=0, column=1)

    ttk.Label(frame_result, text="Ньютон:" ).grid(row=1, column=0, sticky="w")
    ttk.Label(frame_result, textvariable=var_new,  ).grid(row=1, column=1)

    ttk.Label(frame_result, text="Канонический:" ).grid(row=2, column=0, sticky="w")
    ttk.Label(frame_result, textvariable=var_can,  ).grid(row=2, column=1)

    frame_graph = ttk.LabelFrame(right, text="График",   )
    frame_graph.grid(row=1, column=0, sticky="nsew", pady=5)

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    frame_formula = ttk.LabelFrame(right, text="Формула",   padding=10)
    frame_formula.grid(row=2, column=0, sticky="ew", pady=5)

    ttk.Label(frame_formula, textvariable=formula_var, wraplength=500).pack()


    #ЛОГИКА
    def show_points():
        listbox.delete(0, tk.END)
        for x, y in zip(pts_x, pts_y):
            listbox.insert(tk.END, f"{nice(x, 3):>10} {nice(y, 3):>10}")

    def draw():
        ax.clear()
        if len(pts_x) < 2:
            canvas.draw()
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            return

        xs, ys = sort_points(pts_x, pts_y)
        x_plot = np.linspace(min(xs), max(xs), 500)
        try:
            y_plot = [canon(x, xs, ys, metod_slau.get()) for x in x_plot]
        except:
            y_plot = [lagrange(x, xs, ys) for x in x_plot]

        ax.plot(xs, ys, "ko", label="Узлы")
        ax.plot(x_plot, y_plot, label="Полином")
        ax.legend()
        ax.grid(True)

        if current_y is not None:
            ax.plot(current_x, current_y, "ro", markersize=8)

        canvas.draw()

    def calculate():
        nonlocal current_x, current_y
        try:
            x = to_float(entry_calc.get())
            if len(pts_x) >= 2:
                if x < min(pts_x) or x > max(pts_x):
                    messagebox.showwarning(
                        "Предупреждение",
                        "Выполняется экстраполяция.\nТочность может быть низкой.",
                        parent=win
                    )
            xs, ys, lag, new, can, formula = calculate_values(pts_x, pts_y, x, metod_slau.get())

            # ub ratb pozhe
            print(f"Используется метод: {metod_slau.get()}")
            # ub ratb pozhe

            current_x = x
            current_y = lag

            var_lag.set(nice(lag))
            if isinstance(new, str):
                var_new.set(new)
            else:
                var_new.set(nice(new))
            var_can.set(nice(can))
            formula_var.set(formula)

            show_points()
            draw()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=win)

    def add_point():
        nonlocal pts_x, pts_y, current_y  # сбрасываем старую точку при изменении узлов
        try:
            x = to_float(entry_x.get())
            y = to_float(entry_y.get())
            pts_x.append(x)
            pts_y.append(y)
            pts_x, pts_y = sort_points(pts_x, pts_y)
            current_y = None
            show_points()
            draw()
            calculate()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=win)

    def delete_selected():
        nonlocal pts_x, pts_y, current_y
        sel = listbox.curselection()
        if sel:
            i = sel[0]
            pts_x.pop(i)
            pts_y.pop(i)
            pts_x, pts_y = sort_points(pts_x, pts_y)
            current_y = None  # сбрасываем старую точку
            show_points()
            draw()
            if len(pts_x) >= 2:
                calculate()  # пересчитываем, если есть что считать

    def clear_all():
        nonlocal pts_x, pts_y, current_y
        pts_x.clear()
        pts_y.clear()
        current_y = None  # сбрасываем точку
        show_points()
        draw()
        var_lag.set("")
        var_new.set("")
        var_can.set("")
        formula_var.set("P(x) =")

    def fill_default():
        nonlocal pts_x, pts_y, current_y
        pts_x[:] = DEF_X.copy()
        pts_y[:] = DEF_Y.copy()
        pts_x, pts_y = sort_points(pts_x, pts_y)
        current_y = None  # сбрасываем точку
        show_points()
        draw()


    btn_add.config(command=add_point)
    btn_calc.config(command=calculate)
    btn_clear.config(command=clear_all)
    btn_del.config(command=delete_selected)
    btn_fill.config(command=fill_default)

    show_points()
    draw()

    return win

def main():
    win = open_interpolation_window()
    win.mainloop()


if __name__ == "__main__":
    main()