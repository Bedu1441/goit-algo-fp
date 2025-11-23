from __future__ import annotations

import uuid
import random
import heapq
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple, List

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import cm


@dataclass
class Node:
    """
    Вузол бінарного дерева, яке використовується для візуалізації.
    Тут ми зберігаємо:
    - value: значення вузла (елемент купи),
    - index: індекс у масиві купи (для зручності та візуалізації),
    - color: колір вузла,
    - left / right: посилання на дочірні вузли,
    - id: унікальний ідентифікатор для графа (щоб уникнути конфліктів).
    """
    value: int
    index: int
    color: str = "skyblue"
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


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
    :param layer: Номер шару (глибина), використовується для горизонтального рознесення вузлів.
    """
    if node is not None:
        label = f"{node.value}\n[{node.index}]"
        graph.add_node(node.id, color=node.color, label=label)

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
    """
    tree = nx.DiGraph()
    pos: Dict[str, Tuple[float, float]] = {tree_root.id: (0.0, 0.0)}
    tree = add_edges(tree, tree_root, pos)

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


def build_heap_tree(heap: List[int]) -> Optional[Node]:
    """
    Створює дерево з масиву, який інтерпретується як бінарна купа.

    Вважаємо, що heap[i] – значення у вузлі з індексом i.
    Діти вузла i:
      - left = 2 * i + 1
      - right = 2 * i + 2

    :param heap: Список цілих чисел, що представляють купу.
    :return: Кореневий вузол дерева або None, якщо heap порожній.
    """
    if not heap:
        return None

    # Створюємо список вузлів тієї ж довжини.
    nodes: List[Optional[Node]] = [None] * len(heap)

    for i, value in enumerate(heap):
        nodes[i] = Node(value=value, index=i)

    for i in range(len(heap)):
        left_index = 2 * i + 1
        right_index = 2 * i + 2

        if left_index < len(heap):
            nodes[i].left = nodes[left_index]  # type: ignore[index]
        if right_index < len(heap):
            nodes[i].right = nodes[right_index]  # type: ignore[index]

    root = nodes[0]
    assign_colors_by_depth(root)
    return root


def assign_colors_by_depth(root: Optional[Node]) -> None:
    """
    Призначає кольори вузлам залежно від їхньої глибини в дереві:
    корінь темніший, листки – світліші.

    Використовуємо colormap 'Blues' для наочності.
    """
    if root is None:
        return

    # BFS, щоб зібрати вузли по рівнях
    levels: Dict[int, List[Node]] = {}
    queue: List[Tuple[Node, int]] = [(root, 0)]

    max_level = 0
    while queue:
        node, level = queue.pop(0)
        levels.setdefault(level, []).append(node)
        max_level = max(max_level, level)

        if node.left:
            queue.append((node.left, level + 1))
        if node.right:
            queue.append((node.right, level + 1))

    # Призначаємо кольори: чим глибше рівень, тим світліший відтінок
    for level, nodes in levels.items():
        # t від 0 (корінь) до 1 (найнижчий рівень)
        t = level / max_level if max_level > 0 else 0.0
        color_rgba = cm.Blues(0.3 + 0.7 * t)  # трішки зсунутий діапазон, щоб кольори були виразні
        # Перетворюємо RGBA у hex для сумісності з matplotlib/networkx
        hex_color = _rgba_to_hex(color_rgba)
        for node in nodes:
            node.color = hex_color


def _rgba_to_hex(rgba: Tuple[float, float, float, float]) -> str:
    """
    Допоміжна функція: перетворює RGBA в hex рядок виду "#RRGGBB".
    Альфа-канал ігноруємо.
    """
    r, g, b, _ = rgba
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def demo_static_heap() -> None:
    """
    Демонстрація візуалізації фіксованої купи.
    """
    print("=== Демонстрація статичної купи ===")
    heap = [3, 5, 7, 9, 11, 13, 15]
    print("Купа (як масив):", heap)

    root = build_heap_tree(heap)
    if root is not None:
        draw_tree(root, title="Візуалізація бінарної купи (статичний приклад)")


def demo_heapify_process() -> None:
    """
    Демонстрація: беремо випадковий список, показуємо
    його дерево «як є», а потім перетворюємо на купу за допомогою heapq.heapify
    і показуємо дерево вже для купи.

    Це вже явно «понад очікуваннями» – візуалізація процесу побудови купи.
    """
    print("\n=== Демонстрація перетворення списку на купу (heapify) ===")
    data = random.sample(range(1, 50), 7)
    print("Початковий список:", data)

    # Візуалізуємо початковий список як бінарне дерево (не обов'язково купа)
    root_original = build_heap_tree(data)
    if root_original is not None:
        draw_tree(root_original, title="Початкове дерево (це ще не купа)")

    # Перетворюємо список на мін-купу
    heapq.heapify(data)
    print("Після heapq.heapify:", data)

    root_heap = build_heap_tree(data)
    if root_heap is not None:
        draw_tree(root_heap, title="Дерево після heapq.heapify (мін-купа)")


def _run_simple_tests() -> None:
    """
    Невеликий набір перевірок, що дерево будується правильно для базового випадку.
    """
    print("\nЗапуск внутрішніх тестів для побудови дерева з купи...")
    heap = [10, 20, 30, 40, 50, 60, 70]
    root = build_heap_tree(heap)
    assert root is not None, "Корінь не повинен бути None для непорожньої купи"
    assert root.value == 10, "Неправильне значення в корені"
    assert root.left is not None and root.left.value == 20, "Неправильний лівий дочірній вузол кореня"
    assert root.right is not None and root.right.value == 30, "Неправильний правий дочірній вузол кореня"

    # Перевіряємо листки
    assert root.left.left is not None and root.left.left.value == 40
    assert root.left.right is not None and root.left.right.value == 50
    assert root.right.left is not None and root.right.left.value == 60
    assert root.right.right is not None and root.right.right.value == 70

    print("Усі внутрішні тести для побудови дерева з купи пройдено успішно ✅")


if __name__ == "__main__":
    _run_simple_tests()
    demo_static_heap()
    demo_heapify_process()
