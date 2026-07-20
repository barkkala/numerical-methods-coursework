import tkinter as tk
from tkinter import ttk

def open_about_window(parent):
    win = tk.Toplevel(parent)
    win.title("Об авторе и инструкция")
    win.geometry("780x680")
    win.configure(bg="#2b2b2b")
    win.resizable(False, False)

    # Прокручиваемая область
    main_canvas = tk.Canvas(win, bg="#2b2b2b", highlightthickness=0)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=main_canvas.yview)
    scrollable_frame = tk.Frame(main_canvas, bg="#2b2b2b")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)

    main_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Заголовок
    tk.Label(scrollable_frame, text="Курсовая работа", font=("Helvetica", 18, "bold"),
             bg="#2b2b2b", fg="white").pack(pady=(15, 5))
    tk.Label(scrollable_frame, text="Автор: Нестеров Артём Аркадьевич", font=("Helvetica", 11),
             bg="#2b2b2b", fg="white").pack()
    tk.Label(scrollable_frame, text="Группа: 1-ПМИ6-1", font=("Helvetica", 11),
             bg="#2b2b2b", fg="white").pack()
    tk.Label(scrollable_frame, text="Вариант: 14", font=("Helvetica", 11),
             bg="#2b2b2b", fg="white").pack(pady=(0, 15))

    ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', padx=20, pady=5)

    # Инструкция
    instr_frame = tk.LabelFrame(scrollable_frame, text="Инструкция по использованию",
                                bg="#2b2b2b", fg="white", font=("Helvetica", 10, "bold"))
    instr_frame.pack(fill="x", padx=20, pady=10)

    # Область с текстом инструкции
    text_container = tk.Frame(instr_frame, bg="#3c3c3c")   # светлее фона
    text_container.pack(fill="both", expand=True, padx=5, pady=5)

    instr_text = tk.Text(text_container, wrap=tk.WORD, font=("Helvetica", 10),
                         bg="#3c3c3c", fg="white", height=12, relief="flat")
    scroll_text = tk.Scrollbar(text_container, orient="vertical", command=instr_text.yview,
                               bg="#3c3c3c", troughcolor="#3c3c3c")
    instr_text.configure(yscrollcommand=scroll_text.set)

    instr_text.pack(side="left", fill="both", expand=True)
    scroll_text.pack(side="right", fill="y")

    instruction = """1. ВЫБОР РАЗДЕЛА В ГЛАВНОМ ОКНЕ
   • Интегралы – численное интегрирование.
   • Нелинейные уравнения – поиск корней.
   • Интерполяция – построение полиномов.
   • МНК – аппроксимация данных.
   • МКР – решение краевой задачи.

2. РАБОТА С КАЖДЫМ РАЗДЕЛОМ
   • Введите параметры (границы, точность, количество узлов).
   • Нажмите кнопку вычисления.
   • График обновляется автоматически.
   • Для интегралов: кнопка "n(min)" подбирает шаг автоматически.
   • Для нелинейных: "Автоподбор интервала" находит подходящий отрезок.

3. ОСОБЕННОСТИ ВВОДА
   • Можно использовать запятую или точку (например, 1,5 или 1.5).
   • Все ошибки выводятся в специальное поле (красным текстом).

4. ДОПОЛНИТЕЛЬНО
   • В главном окне за курсором мыши движется анимированный крокодил.
   • В разделах "Интерполяция", "МНК", "МКР" можно выбрать метод решения СЛАУ: Гаусс или Крамер.
"""
    instr_text.insert("1.0", instruction)
    instr_text.config(state=tk.DISABLED)

    # Особенности реализации (рамка)
    features_frame = tk.LabelFrame(scrollable_frame, text="⚙    Особенности реализации",
                                   bg="#2b2b2b", fg="white", font=("Helvetica", 10, "bold"))
    features_frame.pack(fill="x", padx=20, pady=10)

    features = [
        "• Библиотеки: tkinter, numpy, matplotlib.",
        "• Интегралы: методы левых/правых/средних прямоугольников, трапеций, Симпсона; оценка погрешности по Рунге; автоподбор шага.",
        "• Нелинейные уравнения: дихотомия, хорды, касательные (Ньютон), комбинированный, итерационный; проверка сходимости; автоподбор интервала.",
        "• Интерполяция: полиномы Лагранжа, Ньютона (равномерная сетка), канонический через СЛАУ.",
        "• МНК: три модели (линейная, квадратичная, y = c + b/x + a/x³); выбор метода решения СЛАУ.",
        "• МКР: метод прогонки и матричный метод; решение СЛАУ Гауссом или Крамером.",
        "• Главное окно: анимированный крокодил, следующий за курсором."
    ]

    for f in features:
        tk.Label(features_frame, text=f, wraplength=700, justify="left",
                 bg="#2b2b2b", fg="white", font=("Helvetica", 10)).pack(anchor="w", pady=2)

    ttk.Button(scrollable_frame, text="Закрыть", command=win.destroy, width=20).pack(pady=20)

    main_canvas.yview_moveto(0)