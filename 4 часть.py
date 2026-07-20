import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math


def parse_float(text):
    text = text.strip().replace(",", ".")

    if text == "":
        raise ValueError("Поле пустое")

    value = float(text)

    if not math.isfinite(value):
        raise ValueError("Некорректное число")

    return value


def mnk(root=None):
    mnk_window = tk.Toplevel(root) if root else tk.Tk()
    mnk_window.title("Метод наименьших квадратов - вариант 14")
    mnk_window.geometry("1200x740")
    mnk_window.minsize(1100, 680)
    mnk_window.configure(bg="#f4f6f8")

    def_x = [1.01, 1.02, 1.12, 1.23, 1.34, 1.46, 1.55, 1.6, 1.77, 1.87, 1.95, 2.0]
    def_y = [1.2, 3.2, 4.19, 4.39, 4.58, 5.73, 6.83, 5.93, 5.51, 4.81, 2.94, 1.12]

    points_x = def_x.copy()
    points_y = def_y.copy()

    # Переменные для коэффициентов

    linear_vars = {'a': tk.StringVar(master=mnk_window, value=""), 'b': tk.StringVar(master=mnk_window, value=""), 'S': tk.StringVar(master=mnk_window, value="")}
    quad_vars = {'a': tk.StringVar(master=mnk_window, value=""), 'b': tk.StringVar(master=mnk_window, value=""),
                 'c': tk.StringVar(master=mnk_window, value=""), 'S': tk.StringVar(master=mnk_window, value="")}
    custom_vars = {'c': tk.StringVar(master=mnk_window, value=""), 'b': tk.StringVar(master=mnk_window, value=""),
                   'a': tk.StringVar(master=mnk_window, value=""), 'S': tk.StringVar(master=mnk_window, value="")}

    metod_slau = tk.StringVar(value="gauss")


    def linear_approximation(x, y):
        n = len(x)
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        a = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n)) / sum((x[i] - x_mean) ** 2 for i in range(n))
        b = y_mean - a * x_mean
        y_pred = [a * x[i] + b for i in range(n)]
        S = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        return a, b, S

    def quadratic_approximation(x, y):
        n = len(x)
        # Решаем систему методом наименьших квадратов
        sum_x = sum(x)
        sum_x2 = sum(xi ** 2 for xi in x)
        sum_x3 = sum(xi ** 3 for xi in x)
        sum_x4 = sum(xi ** 4 for xi in x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2y = sum(x[i] ** 2 * y[i] for i in range(n))

        # Матрица системы
        A = [[sum_x4, sum_x3, sum_x2],
             [sum_x3, sum_x2, sum_x],
             [sum_x2, sum_x, n]]

        B = [sum_x2y, sum_xy, sum_y]

        method = metod_slau.get()
        if method == "gauss":
            coef = gauss_solve(A, B)
        elif method == "cramer":
            coef = cramer_solve(A, B)
        else:  # inverse
            coef = inverse_solve(A, B)
        if coef is None:
            return None, None, None, None

        if coef:
            a, b, c = coef
            y_pred = [a * x[i] ** 2 + b * x[i] + c for i in range(n)]
            S = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
            return a, b, c, S
        return 0, 0, 0, 0

    def custom_approximation(x, y):
        n = len(x)
        sum_x_1 = sum(1 / xi for xi in x)
        sum_x_2 = sum(1 / (xi ** 2) for xi in x)
        sum_x_3 = sum(1 / (xi ** 3) for xi in x)
        sum_x_4 = sum(1 / (xi ** 4) for xi in x)
        sum_x_6 = sum(1 / (xi ** 6) for xi in x)
        sum_y = sum(y)
        sum_y_x = sum(y[i] / x[i] for i in range(n))
        sum_y_x3 = sum(y[i] / (x[i] ** 3) for i in range(n))

        # Матрица для коэффициентов [a, b, c] модели y = c + b/x + a/x^3
        A = [[sum_x_6, sum_x_4, sum_x_3],
             [sum_x_4, sum_x_2, sum_x_1],
             [sum_x_3, sum_x_1, n]]
        B = [sum_y_x3, sum_y_x, sum_y]

        method = metod_slau.get()
        if method == "gauss":
            coef = gauss_solve(A, B)
        elif method == "cramer":
            coef = cramer_solve(A, B)
        else:  # inverse
            coef = inverse_solve(A, B)
        if coef is None:
            return None, None, None, None

        if coef:
            a, b, c = coef
            y_pred = [c + b / x[i] + a / (x[i] ** 3) for i in range(n)]
            S = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
            return a, b, c, S
        return 0, 0, 0, 0

    def gauss_solve(A, B):
        n = len(A)
        A = [row[:] for row in A]
        B = B[:]

        for i in range(n):
            max_row = i
            for k in range(i + 1, n):
                if abs(A[k][i]) > abs(A[max_row][i]):
                    max_row = k
            A[i], A[max_row] = A[max_row], A[i]
            B[i], B[max_row] = B[max_row], B[i]

            if abs(A[i][i]) < 1e-12:
                return None

            for k in range(i + 1, n):
                factor = A[k][i] / A[i][i]
                for j in range(i, n):
                    A[k][j] -= factor * A[i][j]

                B[k] -= factor * B[i]

        X = [0] * n
        for i in range(n - 1, -1, -1):
            if abs(A[i][i]) < 1e-12:
                return None
            X[i] = B[i] / A[i][i]
            for k in range(i - 1, -1, -1):
                B[k] -= A[k][i] * X[i]
        return X

    def determinant(matrix):
        n = len(matrix)
        a = [row[:] for row in matrix]
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

    def inverse_solve(A, B):
        n = len(A)
        aug = [A[i][:] + [1.0 if j == i else 0.0 for j in range(n)] for i in range(n)]

        # Прямой ход (приведение к верхнетреугольному виду)
        for i in range(n):
            # Поиск главного элемента
            max_row = i
            for k in range(i + 1, n):
                if abs(aug[k][i]) > abs(aug[max_row][i]):
                    max_row = k
            if max_row != i:
                aug[i], aug[max_row] = aug[max_row], aug[i]

            if abs(aug[i][i]) < 1e-12:
                return None

            # Нормировка строки i
            div = aug[i][i]
            for j in range(2 * n):
                aug[i][j] /= div

            # Обнуление остальных строк
            for k in range(n):
                if k != i and abs(aug[k][i]) > 1e-12:
                    factor = aug[k][i]
                    for j in range(2 * n):
                        aug[k][j] -= factor * aug[i][j]

        # Обратная матрица в правой половине
        inv = [aug[i][n:] for i in range(n)]

        # Умножение обратной матрицы на B
        X = [sum(inv[i][j] * B[j] for j in range(n)) for i in range(n)]
        return X


    def update_listbox_display():
        """Обновление отображения точек в Listbox"""
        points_listbox.delete(0, tk.END)
        for i, (x, y) in enumerate(zip(points_x, points_y), 1):
            points_listbox.insert(tk.END, f"{i:>2}. {x:>10.4f} {y:>10.4f}")

    def update_calculations():
        """Обновление всех расчётов МНК"""
        if len(points_x) < 2:
            for var in linear_vars.values():
                var.set("")
            for var in quad_vars.values():
                var.set("")
            for var in custom_vars.values():
                var.set("")
            update_graph()
            return

        # Линейная
        a_lin, b_lin, S_lin = linear_approximation(points_x, points_y)
        linear_vars['a'].set(f"{a_lin:.6f}")
        linear_vars['b'].set(f"{b_lin:.6f}")
        linear_vars['S'].set(f"{S_lin:.6f}")

        # Квадратичная
        if len(points_x) >= 3:
            res_quad = quadratic_approximation(points_x, points_y)
            if res_quad is None or any(v is None for v in res_quad):
                for var in quad_vars.values():
                    var.set("Ошибка решения СЛАУ")
            else:
                a_quad, b_quad, c_quad, S_quad = res_quad
                quad_vars['a'].set(f"{a_quad:.6f}")
                quad_vars['b'].set(f"{b_quad:.6f}")
                quad_vars['c'].set(f"{c_quad:.6f}")
                quad_vars['S'].set(f"{S_quad:.6f}")
        else:
            for var in quad_vars.values():
                var.set("Недостаточно точек")

        # Пользовательская
        if len(points_x) >= 3:
            res_cust = custom_approximation(points_x, points_y)
            if res_cust is None or any(v is None for v in res_cust):
                for var in custom_vars.values():
                    var.set("Ошибка решения СЛАУ")
            else:
                a_cust, b_cust, c_cust, S_cust = res_cust
                custom_vars['a'].set(f"{a_cust:.6f}")
                custom_vars['b'].set(f"{b_cust:.6f}")
                custom_vars['c'].set(f"{c_cust:.6f}")
                custom_vars['S'].set(f"{S_cust:.6f}")
        else:
            for var in custom_vars.values():
                var.set("Недостаточно точек")

        update_graph()

    def update_graph():
        """Обновление графика"""
        ax.clear()

        if len(points_x) >= 2:
            # Экспериментальные точки
            ax.scatter(points_x, points_y, color='red', s=50, zorder=5, label='Экспериментальные точки')

            x_min, x_max = min(points_x), max(points_x)
            x_smooth = np.linspace(x_min, x_max, 200)

            # Линейная
            if linear_vars['a'].get() and linear_vars['b'].get():
                try:
                    a_lin = float(linear_vars['a'].get())
                    b_lin = float(linear_vars['b'].get())
                    y_lin = a_lin * x_smooth + b_lin
                    ax.plot(x_smooth, y_lin, 'b-', label='Линейная', linewidth=2)
                except:
                    pass

            # Квадратичная
            if quad_vars['a'].get() and quad_vars['b'].get() and quad_vars['c'].get():
                try:
                    a_quad = float(quad_vars['a'].get())
                    b_quad = float(quad_vars['b'].get())
                    c_quad = float(quad_vars['c'].get())
                    y_quad = a_quad * x_smooth ** 2 + b_quad * x_smooth + c_quad
                    ax.plot(x_smooth, y_quad, 'g-', label='Квадратичная', linewidth=2)
                except:
                    pass

            # Пользовательская
            if custom_vars['a'].get() and custom_vars['b'].get() and custom_vars['c'].get():
                try:
                    a_cust = float(custom_vars['a'].get())
                    b_cust = float(custom_vars['b'].get())
                    c_cust = float(custom_vars['c'].get())
                    y_cust = c_cust + b_cust / x_smooth + a_cust / (x_smooth ** 3)
                    ax.plot(x_smooth, y_cust, 'm-', label='Пользовательская', linewidth=2)
                except:
                    pass

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend()
        ax.grid(True, alpha=0.3)
        canvas.draw()

    #ФУНКЦИИ УПРАВЛЕНИЯ ТОЧКАМИ


    def add_point():
        try:
            x = parse_float(entry_x.get())
            y = parse_float(entry_y.get())

            # НОВАЯ ПРОВЕРКА НА НОЛЬ
            if abs(x) < 1e-12:
                messagebox.showerror("Ошибка", "x не может быть равен 0 (деление на ноль)",
                                     parent=mnk_window)
                return

            # Запрет на одинаковые x
            for px in points_x:
                if abs(px - x) < 1e-12:
                    messagebox.showerror("Ошибка", "Точка с таким x уже существует", parent=mnk_window)
                    return

            # Запрет на полное совпадение точки
            for px, py in zip(points_x, points_y):
                if abs(px - x) < 1e-12 and abs(py - y) < 1e-12:
                    messagebox.showerror("Ошибка", "Такая точка уже есть", parent=mnk_window)
                    return

            points_x.append(x)
            points_y.append(y)

            # Сортировка по x
            paired = sorted(zip(points_x, points_y), key=lambda pair: pair[0])
            points_x.clear()
            points_y.clear()
            for px, py in paired:
                points_x.append(px)
                points_y.append(py)

            entry_x.delete(0, tk.END)
            entry_y.delete(0, tk.END)
            update_listbox_display()
            update_calculations()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные числа", parent=mnk_window)



    def fill_condition():
        points_x.clear()
        points_y.clear()
        points_x.extend(def_x.copy())
        points_y.extend(def_y.copy())
        update_listbox_display()
        update_calculations()

    def delete_selected():
        selection = points_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(points_x):
                points_x.pop(index)
                points_y.pop(index)
                update_listbox_display()
                update_calculations()
        else:
            messagebox.showwarning("Предупреждение", "Выберите точку для удаления", parent=mnk_window)

    def cancel_all():
        points_x.clear()
        points_y.clear()
        update_listbox_display()
        update_calculations()

    # РАЗМЕЩЕНИЕ ВСЕХ ВИДЖЕТОВ

    style = ttk.Style(mnk_window)
    style.theme_use("alt")

    main = ttk.Frame(mnk_window, padding=12)
    main.pack(fill="both", expand=True)
    main.columnconfigure(0, weight=0, minsize=260)
    main.columnconfigure(1, weight=0, minsize=300)
    main.columnconfigure(2, weight=1)
    main.rowconfigure(1, weight=1)

    ttk.Label(main, text="Метод наименьших квадратов. Вариант 14").grid(
        row=0, column=0, columnspan=3, sticky="w", pady=10
    )

    left = ttk.Frame(main)
    left.grid(row=1, column=0, sticky="ns", padx=(0, 10))

    add_frame = ttk.LabelFrame(left, text="Добавление точки", padding=10)
    add_frame.pack(fill="x", pady=5)
    add_frame.columnconfigure(1, weight=1)

    ttk.Label(add_frame, text="x").grid(row=0, column=0, sticky="w", pady=5)
    entry_x = ttk.Entry(add_frame)
    entry_x.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

    ttk.Label(add_frame, text="y").grid(row=1, column=0, sticky="w", pady=5)
    entry_y = ttk.Entry(add_frame)
    entry_y.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)

    ttk.Button(add_frame, text="Добавить точку", command=add_point).grid(
        row=2, column=0, columnspan=2, sticky="ew", pady=5
    )

    control_frame = ttk.LabelFrame(left, text="Управление", padding=10)
    control_frame.pack(fill="x", pady=5)
    control_frame.columnconfigure(0, weight=1)

    for row, (text, command) in enumerate(
        (
            ("Заполнить по условию", fill_condition),
            ("Удалить выбранную", delete_selected),
            ("Очистить всё", cancel_all),
            ("Закрыть окно", mnk_window.destroy),
        )
    ):
        ttk.Button(control_frame, text=text, command=command).grid(row=row, column=0, sticky="ew", pady=3)

    slau_frame_left = ttk.LabelFrame(left, text="Метод решения", padding=10)
    slau_frame_left.pack(fill="x", pady=5)
    ttk.Radiobutton(slau_frame_left, text="Гаусс", variable=metod_slau, value="gauss",
                    command=update_calculations).pack(anchor="w", pady=2)
    ttk.Radiobutton(slau_frame_left, text="Крамер", variable=metod_slau, value="cramer",
                    command=update_calculations).pack(anchor="w", pady=2)
    ttk.Radiobutton(slau_frame_left, text="Матричный (обратная матрица)", variable=metod_slau, value="inverse",
                    command=update_calculations).pack(anchor="w", pady=2)

    legend_frame = ttk.LabelFrame(left, text="Пояснение", padding=10)
    legend_frame.pack(fill="x", pady=5)
    ttk.Label(
        legend_frame,
        text="a, b, c — коэффициенты модели\nS — сумма квадратов отклонений (ошибка)",
        wraplength=250,
        justify="left"
    ).pack(anchor="w")
    table_frame = ttk.LabelFrame(main, text="Экспериментальные данные", padding=10)
    table_frame.grid(row=1, column=1, sticky="ns", padx=5)

    header = ttk.Frame(table_frame)
    header.pack(fill="x", pady=(0, 6))
    ttk.Label(header, text="№").pack(side="left")
    ttk.Label(header, text="x").pack(side="left", expand=True)
    ttk.Label(header, text="y").pack(side="right", expand=True)

    points_listbox = tk.Listbox(
        table_frame,
        font=("Courier New", 10),
        bg="white",
        fg="black",
        borderwidth=1,
        relief="solid",
        highlightthickness=0,
        selectbackground="#dbeafe",
        selectforeground="black",
    )
    points_listbox.pack(fill="both", expand=True)

    right = ttk.Frame(main)
    right.grid(row=1, column=2, sticky="nsew", padx=5)
    right.rowconfigure(0, weight=1)
    right.columnconfigure(0, weight=1)

    graph_frame = ttk.LabelFrame(right, text="График аппроксимаций")
    graph_frame.grid(row=0, column=0, sticky="nsew", pady=5)
    graph_frame.rowconfigure(0, weight=1)
    graph_frame.columnconfigure(0, weight=1)

    fig = Figure(figsize=(6.8, 4.5), dpi=100)
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    calc_frame = ttk.LabelFrame(right, text="Результаты МНК", padding=10)
    calc_frame.grid(row=1, column=0, sticky="ew", pady=5)

    def add_result_block(column, title, formula, values):
        base_column = column * 3
        calc_frame.columnconfigure(base_column + 2, minsize=24)

        ttk.Label(calc_frame, text=title).grid(row=0, column=base_column, columnspan=2, sticky="w")
        ttk.Label(calc_frame, text=formula).grid(
            row=1, column=base_column, columnspan=2, sticky="w", pady=(0, 6)
        )

        for row, (label, var) in enumerate(values, start=2):
            ttk.Label(calc_frame, text=f"{label} =").grid(row=row, column=base_column, sticky="w", pady=2)
            ttk.Label(calc_frame, textvariable=var, width=14).grid(
                row=row, column=base_column + 1, sticky="w", padx=(8, 0), pady=2
            )


    add_result_block(
        0,
        "Линейная",
        "y = ax + b",
        (("a", linear_vars["a"]), ("b", linear_vars["b"]), ("S", linear_vars["S"])),
    )
    add_result_block(
        1,
        "Квадратичная",
        "y = ax² + bx + c",
        (("a", quad_vars["a"]), ("b", quad_vars["b"]), ("c", quad_vars["c"]), ("S", quad_vars["S"])),
    )
    add_result_block(
        2,
        "Пользовательская",
        "y = c + b/x + a/x³",
        (("c", custom_vars["c"]), ("b", custom_vars["b"]), ("a", custom_vars["a"]), ("S", custom_vars["S"])),
    )

    # ИНИЦИАЛИЗАЦИЯ
    update_listbox_display()
    update_calculations()
    return mnk_window


if __name__ == "__main__":
    app = mnk()
    app.mainloop()
