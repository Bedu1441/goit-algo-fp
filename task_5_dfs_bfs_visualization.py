from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, List, Iterable

from collections import deque

import networkx as nx
import matplotlib.pyplot as plt


# ==========================
#  Структура даних "Вузол"
# ==========================

@dataclass
class Node:
    """
    Вузол бінарного дерева.

    value  – значення, яке відображається в дереві;
    left   – лівий нащадок;
    right  – правий нащадок;
    color  – колір вузла у форматі '#RRGGBB' (за замовчуванням – сине небо);
    id     – унікальний ідентифікатор для побудови графа (networkx).
    """
    value: int
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    color: str = "#87CEEB"  # skyblue
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


# =====================================
#  Побудова дерева з масиву значень
# =====================================

def build_complete_binary_tree(values: Iterable[int]) -> Optional[Node]:
    """
    Будує повне бінарне дерево з ітерабельної колекції значень.
    Значення заповнюються рівнями зліва направо.

    :param values: Ітерабельна послідовність цілих чисел.
    :return: Корінь дерева або None, якщо values порожній.
    """
    vals = list(values)
    if not vals:
        return None

    nodes: List[Optional[Node]] = [Node(v) for v in vals]

    for i in range(len(nodes)):
        left_index = 2 * i + 1
        right_index = 2 * i + 2
        if left_index < len(nodes):
            nodes[i].left = nodes[left_index]
        if right_index < len(nodes):
            nodes[i].right = nodes[right_index]

    return nodes[0]


# =====================================
#  Побудова та відображення графа
# =====================================

def add_edges(
    graph: nx.DiGraph,
    node: Optional[Node],
    pos: Dict[str, Tuple[float, float]],
    x: float = 0.0,
    y: float = 0.0,
    layer: int = 1,
) -> nx.DiGraph:
    """
    Рекурсивно додає вузли та ребра до графа для подальшої візуалізації.

    :param graph: Орієнтований граф networkx.
    :param node: Поточний вузол дерева.
    :param pos: Словник позицій для кожного вузла (id -> (x, y)).
    :param x: Поточна x-координата.
    :param y: Поточна y-координата.
    :param layer: Глибина (шар) – використовується для горизонтального рознесення.
    """
    if node is not None:
        graph.add_node(node.id, color=node.color, label=str(node.value))

        if node.left:
            graph.add_edge(node.id, node.left.id)
            left_x = x - 1 / 2**layer
            pos[node.left.id] = (left_x, y - 1)
            add_edges(graph, node.left, pos, x=left_x, y=y - 1, layer=layer + 1)

        if node.right:
            graph.add_edge(node.id, node.right.id)
            right_x = x + 1 / 2**layer
            pos[node.right.id] = (right_x, y - 1)
            add_edges(graph, node.right, pos, x=right_x, y=y - 1, layer=layer + 1)

    return graph


def draw_tree(tree_root: Node, title: str = "") -> None:
    """
    Відображає дерево, коренем якого є tree_root, за допомогою networkx + matplotlib.
    Використовує кольори, які вже записані у node.color.
    """
    tree = nx.DiGraph()
    pos: Dict[str, Tuple[float, float]] = {tree_root.id: (0.0, 0.0)}
    add_edges(tree, tree_root, pos)

    colors = [node_data["color"] for _, node_data in tree.nodes(data=True)]
    labels = {node_id: node_data["label"] for node_id, node_data in tree.nodes(data=True)}

    plt.figure(figsize=(10, 6))
    nx.draw(
        tree,
        pos=pos,
        labels=labels,
        arrows=False,
        node_size=2500,
        node_color=colors,
        font_size=9,
    )
    if title:
        plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# =====================================
#  Генерація кольорового градієнта
# =====================================

def generate_color_gradient_hex(n: int, start_color: str = "#002147", end_color: str = "#99CCFF") -> List[str]:
    """
    Генерує список з n кольорів у форматі '#RRGGBB',
    плавно змінюючись від start_color (темніший) до end_color (світліший).

    :param n: Кількість кольорів.
    :param start_color: Початковий колір у hex.
    :param end_color: Кінцевий колір у hex.
    """
    if n <= 0:
        return []

    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)

    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        r, g, b = rgb
        return "#{:02X}{:02X}{:02X}".format(r, g, b)

    start_r, start_g, start_b = hex_to_rgb(start_color)
    end_r, end_g, end_b = hex_to_rgb(end_color)

    colors: List[str] = []
    for i in range(n):
        t = i / max(1, n - 1)  # від 0 до 1
        r = int(start_r + (end_r - start_r) * t)
        g = int(start_g + (end_g - start_g) * t)
        b = int(start_b + (end_b - start_b) * t)
        colors.append(rgb_to_hex((r, g, b)))
    return colors


# =====================================
#  Обходи DFS та BFS (без рекурсії)
# =====================================

def traverse_dfs(root: Optional[Node]) -> List[Node]:
    """
    Ітеративний обхід в глибину (DFS) з використанням стеку.

    :param root: Корінь дерева.
    :return: Список вузлів у порядку відвідування.
    """
    if root is None:
        return []

    order: List[Node] = []
    stack: List[Node] = [root]

    while stack:
        node = stack.pop()
        order.append(node)
        # Спочатку додаємо правого, потім лівого, щоб лівий оброблявся першим
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)

    return order


def traverse_bfs(root: Optional[Node]) -> List[Node]:
    """
    Обхід в ширину (BFS) з використанням черги.

    :param root: Корінь дерева.
    :return: Список вузлів у порядку відвідування.
    """
    if root is None:
        return []

    order: List[Node] = []
    queue: deque[Node] = deque([root])

    while queue:
        node = queue.popleft()
        order.append(node)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return order


def apply_colors(order: List[Node]) -> None:
    """
    Призначає кожному вузлу унікальний колір згідно з його
    порядком відвідування в обході (DFS або BFS).
    Кольори змінюються від темних до світлих відтінків.
    """
    n = len(order)
    colors = generate_color_gradient_hex(n, start_color="#002147", end_color="#99CCFF")
    for node, color in zip(order, colors):
        node.color = color


# =====================================
#  Демонстрації
# =====================================

def create_sample_tree() -> Optional[Node]:
    """
    Створює приклад бінарного дерева з фіксованими значеннями,
    щоб обходи були наочними.
    """
    # Дерево вигляду:
    #          10
    #        /    \
    #       5      15
    #      / \    /  \
    #     3   7  13  18
    values = [10, 5, 15, 3, 7, 13, 18]
    return build_complete_binary_tree(values)


def demo_traversal(traversal_type: str, step_by_step: bool = False) -> None:
    """
    Демонстрація обходу дерева (DFS або BFS) з візуалізацією.

    :param traversal_type: "dfs" або "bfs".
    :param step_by_step: Якщо True – показуємо покроково зміну кольорів для кожного кроку.
    """
    root = create_sample_tree()
    if root is None:
        print("Неможливо створити дерево. Завершення.")
        return

    traversal_type = traversal_type.lower()

    if traversal_type == "dfs":
        order = traverse_dfs(root)
        title_base = "DFS (обхід у глибину)"
    elif traversal_type == "bfs":
        order = traverse_bfs(root)
        title_base = "BFS (обхід у ширину)"
    else:
        print("Невідомий тип обходу. Використовуйте 'dfs' або 'bfs'.")
        return

    print(f"\nПорядок відвідування вузлів для {title_base}:")
    print(" -> ".join(str(node.value) for node in order))

    if step_by_step:
        # Покрокова візуалізація: на кожному кроці фарбуємо
        # всі вже відвідані вузли, показуємо дерево, чекаємо Enter.
        print("\nРежим покрокової візуалізації. Натискайте Enter для переходу до наступного кроку.")
        colors = generate_color_gradient_hex(len(order), "#002147", "#99CCFF")
        for i, node in enumerate(order):
            # Фарбуємо всі вузли до поточного включно
            for j in range(i + 1):
                order[j].color = colors[j]
            step_title = f"{title_base}: крок {i + 1} / {len(order)} (відвідано вузол {node.value})"
            draw_tree(root, title=step_title)
            if i < len(order) - 1:
                input("Натисніть Enter для наступного кроку...")
    else:
        # Одноразова візуалізація: фарбуємо вузли згідно з порядком
        apply_colors(order)
        draw_tree(root, title=f"{title_base}: кольори за порядком відвідування")


def _run_simple_tests() -> None:
    """
    Невеликий набір тестів для перевірки коректності DFS і BFS.
    """
    print("Запуск внутрішніх тестів для DFS/BFS...")

    root = create_sample_tree()
    assert root is not None

    dfs_order = [node.value for node in traverse_dfs(root)]
    bfs_order = [node.value for node in traverse_bfs(root)]

    # Очікувані порядки для нашого sample-дерева:
    # DFS (pre-order): 10, 5, 3, 7, 15, 13, 18
    # BFS (level-order): 10, 5, 15, 3, 7, 13, 18
    assert dfs_order == [10, 5, 3, 7, 15, 13, 18], f"Неочікуваний порядок DFS: {dfs_order}"
    assert bfs_order == [10, 5, 15, 3, 7, 13, 18], f"Неочікуваний порядок BFS: {bfs_order}"

    # Перевіримо, що generate_color_gradient_hex повертає коректну кількість і валідні hex-рядки
    colors = generate_color_gradient_hex(5)
    assert len(colors) == 5
    for c in colors:
        assert isinstance(c, str) and c.startswith("#") and len(c) == 7

    print("Усі внутрішні тести DFS/BFS пройдено успішно ✅\n")


if __name__ == "__main__":
    _run_simple_tests()

    print("=== Візуалізація обходу бінарного дерева (DFS/BFS) ===")
    choice = input("Оберіть тип обходу ('dfs' або 'bfs'): ").strip().lower()
    step = input("Увімкнути покрокову візуалізацію? (y/n): ").strip().lower()
    step_by_step = step == "y"

    demo_traversal(choice, step_by_step=step_by_step)
