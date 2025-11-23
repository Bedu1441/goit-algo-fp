from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable, Optional, List


@dataclass
class Node:
    """Вузол однозв'язного списку."""
    value: Any
    next: Optional["Node"] = None


class LinkedList:
    """Проста реалізація однозв'язного списку."""

    def __init__(self, values: Iterable[Any] | None = None) -> None:
        """
        Створює порожній список або заповнює його значеннями з ітерабельного об'єкта.
        """
        self.head: Optional[Node] = None
        if values is not None:
            for v in values:
                self.append(v)

    def append(self, value: Any) -> None:
        """Додати елемент у кінець списку."""
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            return
        current = self.head
        while current.next is not None:
            current = current.next
        current.next = new_node

    def to_list(self) -> List[Any]:
        """Повернути всі значення як звичайний список Python."""
        result: List[Any] = []
        current = self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def reverse(self) -> None:
        """Реверсувати список на місці, змінюючи посилання між вузлами."""
        prev: Optional[Node] = None
        current = self.head
        while current is not None:
            nxt = current.next
            current.next = prev
            prev = current
            current = nxt
        self.head = prev

    def sort(self) -> None:
        """Відсортувати список за допомогою merge sort."""
        self.head = merge_sort_list(self.head)

    @staticmethod
    def merge_sorted(first: "LinkedList", second: "LinkedList") -> "LinkedList":
        """
        Об'єднати два ВЖЕ відсортовані списки у новий відсортований.
        Вихідні списки не змінюються (робимо копію вузлів).
        """
        new_head = merge_two_sorted_lists(copy_list(first.head), copy_list(second.head))
        merged = LinkedList()
        merged.head = new_head
        return merged


def copy_list(head: Optional[Node]) -> Optional[Node]:
    """Створити глибоку копію однозв'язного списку, починаючи з head."""
    if head is None:
        return None
    new_head = Node(head.value)
    current_old = head.next
    current_new = new_head
    while current_old is not None:
        current_new.next = Node(current_old.value)
        current_new = current_new.next
        current_old = current_old.next
    return new_head


def merge_two_sorted_lists(l1: Optional[Node], l2: Optional[Node]) -> Optional[Node]:
    """
    Змерджити два відсортовані за неспаданням списки у один відсортований.
    Повертає head нового списку (вузли перевикористовуються).
    """
    dummy = Node(0)
    tail = dummy

    while l1 is not None and l2 is not None:
        if l1.value <= l2.value:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next

    # Додати "хвіст" одного зі списків
    tail.next = l1 if l1 is not None else l2
    return dummy.next


def split_list(head: Optional[Node]) -> tuple[Optional[Node], Optional[Node]]:
    """
    Розділити список на дві половини (для merge sort).
    Повертає кортеж (ліва_половина_head, права_половина_head).
    """
    if head is None or head.next is None:
        return head, None

    slow = head
    fast = head.next

    while fast is not None and fast.next is not None:
        slow = slow.next  # type: ignore[assignment]
        fast = fast.next.next

    middle = slow.next  # type: ignore[assignment]
    slow.next = None  # type: ignore[assignment]

    return head, middle


def merge_sort_list(head: Optional[Node]) -> Optional[Node]:
    """Merge sort для однозв'язного списку; повертає новий head."""
    if head is None or head.next is None:
        return head

    left, right = split_list(head)
    left_sorted = merge_sort_list(left)
    right_sorted = merge_sort_list(right)
    return merge_two_sorted_lists(left_sorted, right_sorted)


def _demo_reverse_and_sort() -> None:
    """Невелика демонстрація реверсу та сортування."""
    print("=== Демонстрація реверсу та сортування ===")
    ll = LinkedList([5, 1, 4, 2, 3])
    print("Початковий список:", ll.to_list())
    ll.reverse()
    print("Після реверсу:", ll.to_list())
    ll.sort()
    print("Після сортування:", ll.to_list())


def _demo_merge() -> None:
    """Невелика демонстрація об'єднання двох відсортованих списків."""
    print("\n=== Демонстрація об'єднання двох відсортованих списків ===")
    l1 = LinkedList([1, 3, 5, 7])
    l2 = LinkedList([2, 2, 4, 6, 8])
    l1.sort()
    l2.sort()
    merged = LinkedList.merge_sorted(l1, l2)
    print("Список 1:", l1.to_list())
    print("Список 2:", l2.to_list())
    print("Об'єднаний:", merged.to_list())


def _run_simple_tests() -> None:
    """Прості внутрішні тести коректності роботи функцій."""
    # Тест реверсу
    ll = LinkedList([1, 2, 3])
    ll.reverse()
    assert ll.to_list() == [3, 2, 1], "Помилка в reverse"

    # Тест сортування
    ll2 = LinkedList([4, 1, 5, 2, 3])
    ll2.sort()
    assert ll2.to_list() == [1, 2, 3, 4, 5], "Помилка в sort"

    # Тест merge двох відсортованих списків
    l1 = LinkedList([1, 3, 5])
    l2 = LinkedList([2, 4, 6])
    merged = LinkedList.merge_sorted(l1, l2)
    assert merged.to_list() == [1, 2, 3, 4, 5, 6], "Помилка в merge_sorted"

    # Перевірка, що вихідні списки не змінені
    assert l1.to_list() == [1, 3, 5], "merge_sorted змінив перший список"
    assert l2.to_list() == [2, 4, 6], "merge_sorted змінив другий список"

    print("\n Всі внутрішні тести пройдено успішно ✅")


if __name__ == "__main__":
    _demo_reverse_and_sort()
    _demo_merge()
    _run_simple_tests()
