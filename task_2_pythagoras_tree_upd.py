from __future__ import annotations

import sys
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

COLOR = "#8B0000"  # темно-червоний колір ліній, як у прикладі


def draw_branch(
    ax: plt.Axes,
    x: float,
    y: float,
    length: float,
    angle: float,
    level: int,
) -> None:
    """
    Рекурсивно малює дерево Піфагора у вигляді ліній.

    x, y    – початок гілки;
    length  – довжина поточної гілки;
    angle   – кут (у радіанах) від осі OX (π/2 – вертикально вгору);
    level   – рівень рекурсії (0 – більше гілок немає).

    На кожному кроці:
    - малюємо відрізок поточної гілки;
    - створюємо дві дочірні гілки довжиною length * sqrt(2) / 2;
    - повертаємо їх на ±45° відносно поточної гілки.
    """
    if level == 0:
        return

    # Кінець поточної гілки
    x2 = x + length * np.cos(angle)
    y2 = y + length * np.sin(angle)

    # Малюємо саму гілку
    ax.plot([x, x2], [y, y2], color=COLOR, linewidth=1.0)

    # Нова довжина відповідно до класичного дерева Піфагора
    new_length = length * np.sqrt(2) / 2

    # Дві нові гілки під кутами ±45°
    left_angle = angle + np.pi / 4
    right_angle = angle - np.pi / 4

    draw_branch(ax, x2, y2, new_length, left_angle, level - 1)
    draw_branch(ax, x2, y2, new_length, right_angle, level - 1)


def build_and_show_tree(level: int) -> None:
    """
    Створює фігуру, малює стовбур та дерево Піфагора і показує результат.
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    # Починаємо з нижньої точки стовбура.
    # Стовбур включений у першу гілку (кут 90°).
    start_x = 0.0
    start_y = -1.0      # трохи нижче центра, щоб дерево не упиралося в край
    trunk_length = 1.0  # довжина стовбура

    draw_branch(ax, start_x, start_y, trunk_length, np.pi / 2, level)

    ax.set_aspect("equal", "box")
    ax.axis("off")
    plt.tight_layout()
    plt.show()


def _parse_level_from_args() -> Optional[int]:
    """
    Читає рівень рекурсії з аргументів командного рядка, якщо він є.
    """
    if len(sys.argv) < 2:
        return None
    try:
        value = int(sys.argv[1])
        if value < 0:
            raise ValueError
        return value
    except ValueError:
        return None


if __name__ == "__main__":
    # 1. Пробуємо взяти рівень рекурсії з аргументів:
    #    python task_2_pythagoras_tree_upd.py 8
    lvl = _parse_level_from_args()

    # 2. Якщо не задано – запитуємо користувача
    while lvl is None:
        user_input = input("Вкажіть рівень рекурсії (рекомендовано 7–10): ")
        try:
            v = int(user_input)
            if v < 0:
                print("Рівень має бути невід’ємним цілим числом. Спробуйте ще раз.")
                continue
            lvl = v
        except ValueError:
            print("Будь ласка, введіть ціле число.")

    build_and_show_tree(lvl)
