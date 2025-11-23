from __future__ import annotations

import math
import sys
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import cm


def draw_square(ax: plt.Axes, p0: complex, p1: complex, color: tuple[float, float, float, float]) -> None:
    """
    Намалювати квадрат, заданий двома точками основи p0 та p1 (комплексні числа).
    Квадрат будується як:
        p0 -> p1 -> p2 -> p3 -> p0
    де p2 та p3 отримуються поворотом вектора (p1 - p0) на 90 градусів.
    """
    v = p1 - p0  # вектор основи
    # поворот на +90 градусів (множення на 1j у комплексній площині)
    p2 = p1 + v * 1j
    p3 = p0 + v * 1j

    polygon = patches.Polygon(
        [
            (p0.real, p0.imag),
            (p1.real, p1.imag),
            (p2.real, p2.imag),
            (p3.real, p3.imag),
        ],
        closed=True,
        facecolor=color,
        edgecolor="black",
        linewidth=0.5,
    )
    ax.add_patch(polygon)


def draw_pythagoras_tree(
    ax: plt.Axes,
    p0: complex,
    p1: complex,
    level: int,
    max_level: int,
) -> None:
    """
    Рекурсивно малює фрактал «дерево Піфагора».

    :param ax: Вісь matplotlib для малювання.
    :param p0: Ліва нижня точка поточного квадрата (комплексне число).
    :param p1: Права нижня точка поточного квадрата (комплексне число).
    :param level: Поточний рівень рекурсії (0 для кореня).
    :param max_level: Максимальний рівень рекурсії.
    """
    # Нормалізований параметр для градієнта кольорів по глибині рекурсії
    t = level / max_level if max_level > 0 else 0.0
    # Використовуємо colormap viridis для «красоти» :)
    color = cm.viridis(1.0 - t)  # ближче до кореня темніше, вище – світліше

    # Намалювати поточний квадрат
    draw_square(ax, p0, p1, color)

    if level >= max_level:
        return

    v = p1 - p0
    # Верхні точки квадрата
    p2 = p1 + v * 1j
    p3 = p0 + v * 1j
    top = p3 - p2  # вектор верхньої сторони

    # Для класичного дерева Піфагора (рівнобедрений прямокутний трикутник):
    # Обчислюємо вершину трикутника (apex) над верхньою стороною.
    # Формула: apex = p2 + top/2 + (top * 1j) / 2
    # Це дає симетричний варіант, де обидва дочірні квадрати однакового розміру.
    apex = p2 + top / 2 + (top * 1j) / 2

    # Лівий дочірній квадрат базується на відрізку [p2, apex]
    left_p0 = p2
    left_p1 = apex

    # Правий дочірній квадрат базується на відрізку [apex, p3]
    right_p0 = apex
    right_p1 = p3

    # Рекурсивні виклики для двох дочірніх квадратів
    draw_pythagoras_tree(ax, left_p0, left_p1, level + 1, max_level)
    draw_pythagoras_tree(ax, right_p0, right_p1, level + 1, max_level)


def build_and_show_tree(recursion_level: int, save_path: Optional[str] = None) -> None:
    """
    Створює фігуру, будує дерево Піфагора і відображає його.
    Додатково може зберегти результат у файл.

    :param recursion_level: Максимальний рівень рекурсії (рекомендовано 5–10).
    :param save_path: Якщо задано – шлях до файлу, куди зберегти картинку (png, jpg, тощо).
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Початкова база квадрата – горизонтальний відрізок внизу
    base_length = 1.0
    p0 = 0 + 0j
    p1 = base_length + 0j

    draw_pythagoras_tree(ax, p0, p1, level=0, max_level=recursion_level)

    ax.set_aspect("equal", "box")
    ax.axis("off")

    # Трошки запасу по межах, щоб дерево не обрізалося
    margin = 0.2
    ax.set_xlim(-margin, base_length + margin)
    # Висоту оцінимо грубо – з кожним рівнем дерево росте вгору
    max_height = base_length * (1.5 ** (recursion_level / 2))
    ax.set_ylim(-margin, max_height + margin)

    if save_path is not None:
        plt.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Зображення збережено у файл: {save_path}")

    plt.show()


def _parse_recursion_level_from_args() -> Optional[int]:
    """
    Спроба прочитати рівень рекурсії з аргументів командного рядка.
    Повертає int або None, якщо аргумента немає або він некоректний.
    """
    if len(sys.argv) < 2:
        return None
    try:
        value = int(sys.argv[1])
        if value < 0:
            raise ValueError
        return value
    except ValueError:
        print("Аргумент рівня рекурсії має бути невідʼємним цілим числом.")
        return None


if __name__ == "__main__":
    # 1) Спробуємо взяти рівень рекурсії з командного рядка:
    #    python task_2_pythagoras_tree.py 8
    level = _parse_recursion_level_from_args()

    # 2) Якщо не вдалося – запитаємо в користувача.
    while level is None:
        user_input = input("Вкажіть рівень рекурсії для дерева Піфагора (рекомендовано 5–10): ")
        try:
            value = int(user_input)
            if value < 0:
                print("Рівень має бути невідʼємним цілим числом. Спробуйте ще раз.")
                continue
            level = value
        except ValueError:
            print("Будь ласка, введіть ціле число.")

    # 3) Опційно спитаємо, чи зберегти картинку у файл.
    save_choice = input("Бажаєте зберегти зображення у файл? (y/n): ").strip().lower()
    save_file: Optional[str] = None
    if save_choice == "y":
        default_name = f"pythagoras_tree_level_{level}.png"
        user_path = input(f"Введіть імʼя файлу (або натисніть Enter для значення за замовчуванням: {default_name}): ").strip()
        save_file = user_path or default_name

    build_and_show_tree(recursion_level=level, save_path=save_file)
