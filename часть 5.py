import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
import math
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.figure import Figure


def mkr(roditel=None):
    okno_mkr = Toplevel(roditel) if roditel else tk.Tk()
    okno_mkr.title('Метод конечных разностей - часть 5')
    okno_mkr.geometry("1280x740")
    okno_mkr.minsize(1100, 680)
    okno_mkr.configure(bg="#f4f6f8")

    # ПАРАМЕТРЫ ЗАДАЧИ

    def funkciya_p(x):
        return -x / (x + 1)

    def funkciya_q(x):
        return 2 * x

    def funkciya_f(x):
        return math.log(x)

    x_nachalo = 1.0
    y_nachalo = 0.2
    x_konec = 2.5
    y_konec = 1.0
    kolichestvo_intervalov = 7

    x_nachalo_var = tk.StringVar(value="1.0")
    y_nachalo_var = tk.StringVar(value="0.2")
    x_konec_var = tk.StringVar(value="2.5")
    y_konec_var = tk.StringVar(value="1.0")

    uzly_x = []
    reshenie_y = []

    # ВЫЧИСЛЕНИЯ

    def gauss(matrica, pravaya_chast):
        razmer_matricy = len(matrica)
        kopiya_matricy = [stroka[:] for stroka in matrica]
        kopiya_pravoy_chasti = pravaya_chast[:]

        for i in range(razmer_matricy):
            glavnaya_stroka = i
            for k in range(i + 1, razmer_matricy):
                if abs(kopiya_matricy[k][i]) > abs(kopiya_matricy[glavnaya_stroka][i]):
                    glavnaya_stroka = k

            kopiya_matricy[i], kopiya_matricy[glavnaya_stroka] = (
                kopiya_matricy[glavnaya_stroka],
                kopiya_matricy[i],
            )
            kopiya_pravoy_chasti[i], kopiya_pravoy_chasti[glavnaya_stroka] = (
                kopiya_pravoy_chasti[glavnaya_stroka],
                kopiya_pravoy_chasti[i],
            )

            if abs(kopiya_matricy[i][i]) < 1e-12:
                return None

            for k in range(i + 1, razmer_matricy):
                mnozhitel = kopiya_matricy[k][i] / kopiya_matricy[i][i]
                for j in range(i, razmer_matricy):
                    kopiya_matricy[k][j] -= mnozhitel * kopiya_matricy[i][j]
                kopiya_pravoy_chasti[k] -= mnozhitel * kopiya_pravoy_chasti[i]

        otvet = [0.0] * razmer_matricy
        for i in range(razmer_matricy - 1, -1, -1):
            if abs(kopiya_matricy[i][i]) < 1e-12:
                otvet[i] = 0
            else:
                otvet[i] = kopiya_pravoy_chasti[i] / kopiya_matricy[i][i]
                for k in range(i - 1, -1, -1):
                    kopiya_pravoy_chasti[k] -= kopiya_matricy[k][i] * otvet[i]

        return otvet

    def determinant(matrica):
        n = len(matrica)
        a = [row[:] for row in matrica]
        det = 1.0
        for i in range(n):
            max_row = i
            for k in range(i + 1, n):
                if abs(a[k][i]) > abs(a[max_row][i]):
                    max_row = k
            if max_row != i:
                a[i], a[max_row] = a[max_row], a[i]
                det *= -1
            if abs(a[i][i]) < 1e-12:
                return 0.0
            det *= a[i][i]
            for k in range(i + 1, n):
                factor = a[k][i] / a[i][i]
                for j in range(i + 1, n):
                    a[k][j] -= factor * a[i][j]
        return det

    def cramer(A, b):
        n = len(A)
        det_A = determinant(A)
        if abs(det_A) < 1e-12:
            return None
        x = []
        for i in range(n):
            Ai = [row[:] for row in A]
            for j in range(n):
                Ai[j][i] = b[j]
            det_i = determinant(Ai)
            x.append(det_i / det_A)
        return x

    def reshit_obratnoy_matricoy(A, b):
        """Решение СЛАУ через обратную матрицу (numpy)"""
        try:
            A_np = np.array(A, dtype=float)
            b_np = np.array(b, dtype=float)
            x = np.linalg.solve(A_np, b_np)
            return x.tolist()
        except np.linalg.LinAlgError:
            return None

    def raschet_progonkoy():
        nonlocal uzly_x, reshenie_y

        shag = (x_konec - x_nachalo) / kolichestvo_intervalov
        if shag < 1e-8:
            raise ValueError("Слишком маленький шаг сетки")
        uzly_x = [x_nachalo + i * shag for i in range(kolichestvo_intervalov + 1)]

        koeff_a = [0.0] * (kolichestvo_intervalov + 1)
        koeff_b = [0.0] * (kolichestvo_intervalov + 1)
        koeff_c = [0.0] * (kolichestvo_intervalov + 1)
        svobodnye_chleny = [0.0] * (kolichestvo_intervalov + 1)

        for i in range(1, kolichestvo_intervalov):
            x_i = uzly_x[i]
            p_i = funkciya_p(x_i)
            q_i = funkciya_q(x_i)
            f_i = funkciya_f(x_i)

            koeff_a[i] = 1.0 / shag ** 2 - p_i / (2.0 * shag)
            koeff_b[i] = -2.0 / shag ** 2 + q_i
            koeff_c[i] = 1.0 / shag ** 2 + p_i / (2.0 * shag)
            svobodnye_chleny[i] = f_i

            #if abs(koeff_b[i]) < abs(koeff_a[i]) + abs(koeff_c[i]):
            #    messagebox.showwarning(
            #        "Предупреждение",
            #        f"В строке {i} нет диагонального преобладания.\n"
            #       "Метод прогонки может быть неустойчив."
            #   )

        koeff_a[0] = 0.0
        koeff_b[0] = 1.0
        koeff_c[0] = 0.0
        svobodnye_chleny[0] = y_nachalo

        koeff_a[kolichestvo_intervalov] = 0.0
        koeff_b[kolichestvo_intervalov] = 1.0
        koeff_c[kolichestvo_intervalov] = 0.0
        svobodnye_chleny[kolichestvo_intervalov] = y_konec

        progonka_p = [0.0] * (kolichestvo_intervalov + 1)
        progonka_q = [0.0] * (kolichestvo_intervalov + 1)

        if abs(koeff_b[0]) > 1e-15:
            progonka_p[0] = -koeff_c[0] / koeff_b[0]
            progonka_q[0] = svobodnye_chleny[0] / koeff_b[0]

        for i in range(1, kolichestvo_intervalov + 1):
            znamenatel = koeff_b[i] + koeff_a[i] * progonka_p[i - 1]
            if abs(znamenatel) < 1e-15:
                raise ValueError(f"Нулевой знаменатель в прогонке на шаге {i}")
            progonka_p[i] = -koeff_c[i] / znamenatel
            progonka_q[i] = (svobodnye_chleny[i] - koeff_a[i] * progonka_q[i - 1]) / znamenatel

        reshenie_y = [0.0] * (kolichestvo_intervalov + 1)
        reshenie_y[kolichestvo_intervalov] = progonka_q[kolichestvo_intervalov]

        for i in range(kolichestvo_intervalov - 1, -1, -1):
            reshenie_y[i] = progonka_p[i] * reshenie_y[i + 1] + progonka_q[i]

    def raschet_matricoy(metod):
        nonlocal uzly_x, reshenie_y

        shag = (x_konec - x_nachalo) / kolichestvo_intervalov

        uzly_x = [x_nachalo + i * shag for i in range(kolichestvo_intervalov + 1)]

        razmer = kolichestvo_intervalov + 1
        matrica = [[0.0] * razmer for _ in range(razmer)]
        pravaya_chast = [0.0] * razmer

        for i in range(1, kolichestvo_intervalov):
            x_i = uzly_x[i]
            p_i = funkciya_p(x_i)
            q_i = funkciya_q(x_i)
            f_i = funkciya_f(x_i)

            matrica[i][i - 1] = 1.0 / shag ** 2 - p_i / (2.0 * shag)
            matrica[i][i] = -2.0 / shag ** 2 + q_i
            matrica[i][i + 1] = 1.0 / shag ** 2 + p_i / (2.0 * shag)
            pravaya_chast[i] = f_i

        matrica[0][0] = 1.0
        pravaya_chast[0] = y_nachalo
        matrica[kolichestvo_intervalov][kolichestvo_intervalov] = 1.0
        pravaya_chast[kolichestvo_intervalov] = y_konec

        if metod == "gauss":
            reshenie_y = gauss(matrica, pravaya_chast)
        elif metod == "cramer":
            if razmer > 12:
                messagebox.showwarning(
                    "Предупреждение",
                    "Метод Крамера может работать очень медленно "
                    "и быть неустойчивым при больших n"
                )
            reshenie_y = cramer(matrica, pravaya_chast)
        elif metod == "inverse":
            reshenie_y = reshit_obratnoy_matricoy(matrica, pravaya_chast)
        else:
            raise ValueError("Неизвестный матричный метод")

        if reshenie_y is None:
            raise ValueError("Метод не применим (вырожденная матрица)")

    def poluchit_interpolyacionnyy_polinom():
        if len(uzly_x) < 2:
            return "нет данных"
        stepen = len(uzly_x)
        if stepen > 25:
            messagebox.showwarning(
                "Предупреждение",
                "Полином высокой степени может быть численно неустойчив"
            )
        n = stepen - 1
        matrica = [[uzly_x[i] ** j for j in range(stepen)] for i in range(stepen)]
        koeff = gauss(matrica, reshenie_y)

        if koeff is None:
            return "P(x) = не удалось построить полином (вырожденная матрица)"

        slagaemye = []
        for i in range(0, n + 1):
            c = koeff[i]
            if i == 0:
                slagaemye.append(str(c))
            elif i == 1:
                slagaemye.append(f"{c}*x")
            else:
                slagaemye.append(f"{c}*x^{i}")

        result = " + ".join(slagaemye)
        return "P(x) = " + result

    # ОБНОВЛЕНИЯ

    def obnovit_tablicu():
        spisok_rezultatov.delete(0, END)
        for i, (x, y) in enumerate(zip(uzly_x, reshenie_y), 1):
            spisok_rezultatov.insert(
                END,
                f"{i:>2}. {x:>10.6f} {y:>10.6f}"
            )

    def obnovit_formulu():
        formula_var.set(poluchit_interpolyacionnyy_polinom())

    def obnovit_grafik():
        ax.clear()

        if len(uzly_x) > 0:
            ax.scatter(
                uzly_x,
                reshenie_y,
                color='red',
                s=50,
                zorder=5,
                label='Узлы сетки'
            )

            gladkie_x = np.linspace(min(uzly_x), max(uzly_x), 500)
            znacheniya = []

            for x_tekushiy in gladkie_x:
                y_tekushiy = 0
                for i in range(len(uzly_x)):
                    slagaemoe = reshenie_y[i]
                    for j in range(len(uzly_x)):
                        if j != i:
                            slagaemoe *= (
                                (x_tekushiy - uzly_x[j]) /
                                (uzly_x[i] - uzly_x[j])
                            )
                    y_tekushiy += slagaemoe
                znacheniya.append(y_tekushiy)

            ax.plot(
                gladkie_x,
                znacheniya,
                'b-',
                linewidth=2,
                label='Полином'
            )

        ax.set_xlabel('x')
        ax.set_ylabel('y')

        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend()

        ax.grid(True, alpha=0.3)
        canvas.draw()

    def vypolnit_raschet():
        try:
            nonlocal kolichestvo_intervalov, x_nachalo, y_nachalo, x_konec, y_konec

            # Считываем граничные условия
            try:
                x_nachalo = float(x_nachalo_var.get())
                y_nachalo = float(y_nachalo_var.get())
                x_konec = float(x_konec_var.get())
                y_konec = float(y_konec_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат граничных условий", parent=okno_mkr)
                return

            # Считываем количество интервалов
            try:
                n = int(pole_n.get())
                if n >= 1:
                    kolichestvo_intervalov = n
            except:
                pass

            # Проверки
            if x_nachalo >= x_konec:
                messagebox.showerror("Ошибка", "Начальное x должно быть меньше конечного", parent=okno_mkr)
                return
            if x_nachalo <= 0 or x_konec <= 0:
                messagebox.showerror("Ошибка", "x должен быть > 0 (логарифм)", parent=okno_mkr)
                return

            # Выбор метода
            method = peremennaya_metoda.get()
            if method == "progonka":
                raschet_progonkoy()
            elif method == "gauss":
                raschet_matricoy("gauss")
            elif method == "cramer":
                raschet_matricoy("cramer")
            elif method == "inverse":
                raschet_matricoy("inverse")
            else:
                raise ValueError("Неизвестный метод")

            obnovit_tablicu()
            obnovit_formulu()
            obnovit_grafik()

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Ошибка при вычислении:\n{str(e)}",
                parent=okno_mkr,
            )

    def zapolnit_uslovie():
        pole_n.delete(0, END)
        pole_n.insert(0, "7")
        x_nachalo_var.set("1.0")
        y_nachalo_var.set("0.2")
        x_konec_var.set("2.5")
        y_konec_var.set("1.0")
        vypolnit_raschet()

    # ИНТЕРФЕЙС

    style = ttk.Style(okno_mkr)
    style.theme_use("alt")

    main = ttk.Frame(okno_mkr, padding=12)
    main.pack(fill="both", expand=True)

    main.columnconfigure(0, weight=0, minsize=260)
    main.columnconfigure(1, weight=0, minsize=280)
    main.columnconfigure(2, weight=1)

    main.rowconfigure(1, weight=1)

    ttk.Label(
        main,
        text="Метод конечных разностей - часть 5"
    ).grid(
        row=0,
        column=0,
        columnspan=3,
        sticky="w",
        pady=10,
    )

    # ===== LEFT =====

    left = ttk.Frame(main)
    left.grid(row=1, column=0, sticky="ns", padx=(0, 10))

    condition_frame = ttk.LabelFrame(
        left,
        text="Условие задачи",
        padding=10,
    )
    condition_frame.pack(fill="x", pady=5)

    ttk.Label(
        condition_frame,
        text="y'' - (x/(x+1))y' + 2xy = ln(x)"
    ).pack(anchor="w", pady=3)

    # Поля для ввода граничных условий
    frame_bc = ttk.Frame(condition_frame)
    frame_bc.pack(anchor="w", fill="x", pady=5)
    ttk.Label(frame_bc, text="y(").pack(side="left")
    entry_x0 = ttk.Entry(frame_bc, width=6, textvariable=x_nachalo_var)
    entry_x0.pack(side="left")
    ttk.Label(frame_bc, text=") = ").pack(side="left")
    entry_y0 = ttk.Entry(frame_bc, width=6, textvariable=y_nachalo_var)
    entry_y0.pack(side="left")

    frame_bc2 = ttk.Frame(condition_frame)
    frame_bc2.pack(anchor="w", fill="x", pady=5)
    ttk.Label(frame_bc2, text="y(").pack(side="left")
    entry_x1 = ttk.Entry(frame_bc2, width=6, textvariable=x_konec_var)
    entry_x1.pack(side="left")
    ttk.Label(frame_bc2, text=") = ").pack(side="left")
    entry_y1 = ttk.Entry(frame_bc2, width=6, textvariable=y_konec_var)
    entry_y1.pack(side="left")

    ttk.Label(
        condition_frame,
        text="Количество интервалов"
    ).pack(anchor="w", pady=(10, 2))

    pole_n = ttk.Entry(condition_frame)
    pole_n.pack(fill="x")
    pole_n.insert(0, "7")

    # Блок выбора метода (4 радиокнопки)
    method_frame = ttk.LabelFrame(
        left,
        text="Метод решения",
        padding=10,
    )
    method_frame.pack(fill="x", pady=5)

    peremennaya_metoda = StringVar(master=okno_mkr, value="progonka")

    ttk.Radiobutton(
        method_frame,
        text="Метод прогонки",
        variable=peremennaya_metoda,
        value="progonka",
    ).pack(anchor="w", pady=3)

    ttk.Radiobutton(
        method_frame,
        text="Матричный метод (обратная матрица)",
        variable=peremennaya_metoda,
        value="inverse",
    ).pack(anchor="w", pady=3)

    ttk.Radiobutton(
        method_frame,
        text="Метод Гаусса",
        variable=peremennaya_metoda,
        value="gauss",
    ).pack(anchor="w", pady=3)

    ttk.Radiobutton(
        method_frame,
        text="Метод Крамера",
        variable=peremennaya_metoda,
        value="cramer",
    ).pack(anchor="w", pady=3)

    control_frame = ttk.LabelFrame(
        left,
        text="Управление",
        padding=10,
    )
    control_frame.pack(fill="x", pady=5)

    ttk.Button(
        control_frame,
        text="Заполнить по условию",
        command=zapolnit_uslovie,
    ).pack(fill="x", pady=3)

    ttk.Button(
        control_frame,
        text="Пересчитать",
        command=vypolnit_raschet,
    ).pack(fill="x", pady=3)

    ttk.Button(
        control_frame,
        text="Закрыть окно",
        command=okno_mkr.destroy,
    ).pack(fill="x", pady=3)

    # ===== TABLE =====

    table_frame = ttk.LabelFrame(
        main,
        text="Результаты в узлах",
        padding=10,
    )
    table_frame.grid(row=1, column=1, sticky="ns", padx=5)

    spisok_rezultatov = tk.Listbox(
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
    spisok_rezultatov.pack(fill="both", expand=True)

    # ===== RIGHT =====

    right = ttk.Frame(main)
    right.grid(row=1, column=2, sticky="nsew", padx=5)
    right.rowconfigure(0, weight=1)
    right.columnconfigure(0, weight=1)

    graph_frame = ttk.LabelFrame(right, text="График решения")
    graph_frame.grid(row=0, column=0, sticky="nsew", pady=5)
    graph_frame.rowconfigure(0, weight=1)
    graph_frame.columnconfigure(0, weight=1)

    figura = Figure(figsize=(6.8, 4.5), dpi=100)
    ax = figura.add_subplot(111)

    canvas = FigureCanvasTkAgg(figura, master=graph_frame)
    canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

    formula_frame = ttk.LabelFrame(
        right,
        text="Интерполяционный полином",
        padding=10,
    )
    formula_frame.grid(row=1, column=0, sticky="ew", pady=5)

    formula_var = tk.StringVar(master=okno_mkr, value="")
    ttk.Label(
        formula_frame,
        textvariable=formula_var,
        wraplength=650,
        justify="left",
    ).pack(anchor="w")

    # ===== СТАРТ =====
    vypolnit_raschet()
    return okno_mkr


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = mkr(root)
    app.mainloop()