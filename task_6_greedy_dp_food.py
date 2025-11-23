from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


# -----------------------
#   Вхідні дані задачі
# -----------------------

items: Dict[str, Dict[str, int]] = {
    "pizza": {"cost": 50, "calories": 300},
    "hamburger": {"cost": 40, "calories": 250},
    "hot-dog": {"cost": 30, "calories": 200},
    "pepsi": {"cost": 10, "calories": 100},
    "cola": {"cost": 15, "calories": 220},
    "potato": {"cost": 25, "calories": 350},
}


@dataclass
class SelectionResult:
    """Результат вибору страв."""
    items: List[str]
    total_cost: int
    total_calories: int


# -----------------------------------------
#   Жадібний алгоритм (greedy_algorithm)
# -----------------------------------------

def greedy_algorithm(
    food_items: Dict[str, Dict[str, int]],
    budget: int,
) -> SelectionResult:
    """
    Жадібний алгоритм вибору страв.
    Ідея: максимізувати співвідношення калорій / вартість.

    1. Рахуємо ratio = calories / cost для кожної страви.
    2. Сортуємо страви за ratio у спадному порядку.
    3. Ідемо по списку, поки дозволяє бюджет.

    :param food_items: Словник страв: назва -> {"cost": int, "calories": int}
    :param budget: Доступний бюджет.
    :return: SelectionResult – список обраних страв, сумарна вартість, сумарна калорійність.
    """
    # Формуємо список (назва, cost, calories, ratio)
    scored: List[Tuple[str, int, int, float]] = []
    for name, data in food_items.items():
        cost = data["cost"]
        calories = data["calories"]
        if cost <= 0:
            # Захист від ділення на нуль/некоректних даних
            continue
        ratio = calories / cost
        scored.append((name, cost, calories, ratio))

    # Сортуємо за ratio (від більшого до меншого)
    scored.sort(key=lambda x: x[3], reverse=True)

    chosen: List[str] = []
    total_cost = 0
    total_calories = 0

    for name, cost, calories, ratio in scored:
        if total_cost + cost <= budget:
            chosen.append(name)
            total_cost += cost
            total_calories += calories

    return SelectionResult(chosen, total_cost, total_calories)


# ----------------------------------------------------
#   Динамічне програмування (dynamic_programming)
#   Задача: "рюкзак 0/1" – кожну страву можна взяти
#   не більше одного разу.
# ----------------------------------------------------

def dynamic_programming(
    food_items: Dict[str, Dict[str, int]],
    budget: int,
) -> SelectionResult:
    """
    Алгоритм динамічного програмування для вибору оптимального набору страв.

    Ми розв'язуємо класичну задачу "рюкзак 0/1":

        - максимізуємо сумарні калорії,
        - кожну страву можна взяти або взяти 1 раз, або не брати,
        - загальна вартість не повинна перевищувати budget.

    Використовуємо 1-вимірний масив dp:
        dp[w] – максимальна калорійність при бюджеті w.

    Додатково зберігаємо інформацію про те, які страви були взяті,
    щоб відновити оптимальний набір.

    :param food_items: Словник страв: назва -> {"cost": int, "calories": int}
    :param budget: Максимальний бюджет.
    :return: SelectionResult – оптимальний набір страв.
    """
    names = list(food_items.keys())
    n = len(names)

    # dp[w] – максимальні калорії при бюджеті w
    dp = [0] * (budget + 1)
    # keep[i][w] – брали ми i-ту страву (по списку names) при бюджеті w чи ні
    keep: List[List[bool]] = [[False] * (budget + 1) for _ in range(n)]

    for i, name in enumerate(names):
        cost = food_items[name]["cost"]
        calories = food_items[name]["calories"]

        # Ітеруємось по бюджету "назад", щоб кожну страву використати не більше одного разу
        for w in range(budget, cost - 1, -1):
            if dp[w - cost] + calories > dp[w]:
                dp[w] = dp[w - cost] + calories
                keep[i][w] = True

    # Відновлюємо набір страв
    chosen: List[str] = []
    w = budget
    for i in range(n - 1, -1, -1):
        if keep[i][w]:
            name = names[i]
            chosen.append(name)
            w -= food_items[name]["cost"]

    chosen.reverse()

    total_cost = sum(food_items[name]["cost"] for name in chosen)
    total_calories = sum(food_items[name]["calories"] for name in chosen)

    return SelectionResult(chosen, total_cost, total_calories)


# -----------------------------
#   Допоміжні функції виводу
# -----------------------------

def print_selection(title: str, result: SelectionResult) -> None:
    """
    Гарно виводить результат вибору страв.
    """
    print(f"\n{title}")
    print("-" * len(title))
    if not result.items:
        print("Нічого не вибрано (ймовірно, бюджет надто малий).")
        return

    print(f"{'Страва':<12} | {'Вартість':>8} | {'Калорії':>9}")
    print("-" * 36)
    for name in result.items:
        cost = items[name]["cost"]
        calories = items[name]["calories"]
        print(f"{name:<12} | {cost:>8} | {calories:>9}")
    print("-" * 36)
    print(f"Сумарна вартість:  {result.total_cost}")
    print(f"Сумарна калорійність: {result.total_calories}")


def demo_for_budget(budget: int) -> None:
    """
    Демонструє роботу обох алгоритмів для заданого бюджету
    і порівнює результати.
    """
    print(f"\n=== Демонстрація для бюджету: {budget} ===")

    greedy_result = greedy_algorithm(items, budget)
    dp_result = dynamic_programming(items, budget)

    print_selection("Жадібний алгоритм", greedy_result)
    print_selection("Динамічне програмування", dp_result)

    # Додаткове порівняння (понад вимоги)
    diff_cal = dp_result.total_calories - greedy_result.total_calories
    if diff_cal > 0:
        print(f"\nДП знайшов набір з на {diff_cal} калорій більше, ніж жадібний алгоритм.")
    elif diff_cal == 0:
        print("\nОбидва алгоритми дали однакову сумарну калорійність.")
    else:
        # Теоретично можливо, якщо жадібний інколи випадково знаходить той самий або кращий варіант
        print(f"\nЖадібний алгоритм дав на {-diff_cal} калорій більше (незвична, але можлива ситуація).")


# -----------------------------
#   Внутрішні прості тести
# -----------------------------

def _run_simple_tests() -> None:
    """
    Невеликий набір тестів для перевірки коректності реалізації.
    Не є вимогою задачі, але показує якість рішення.
    """
    print("Запуск внутрішніх тестів для greedy та DP...")

    # Тест 1: дуже малий бюджет
    budget_small = 5
    g_small = greedy_algorithm(items, budget_small)
    dp_small = dynamic_programming(items, budget_small)
    assert g_small.total_cost == 0 and g_small.total_calories == 0
    assert dp_small.total_cost == 0 and dp_small.total_calories == 0

    # Тест 2: бюджет, що дозволяє взяти кілька позицій
    budget_mid = 60
    g_mid = greedy_algorithm(items, budget_mid)
    dp_mid = dynamic_programming(items, budget_mid)

    # ДП не може бути гіршим за жадібний за калорійністю
    assert dp_mid.total_calories >= g_mid.total_calories

    # Тест 3: дуже великий бюджет – можемо взяти всі страви
    budget_big = 1_000
    g_big = greedy_algorithm(items, budget_big)
    dp_big = dynamic_programming(items, budget_big)

    all_cost = sum(v["cost"] for v in items.values())
    all_cal = sum(v["calories"] for v in items.values())

    assert g_big.total_cost == all_cost and g_big.total_calories == all_cal
    assert dp_big.total_cost == all_cost and dp_big.total_calories == all_cal

    print("Усі внутрішні тести пройдено успішно ✅")


# -----------------------------
#   Точка входу
# -----------------------------

if __name__ == "__main__":
    _run_simple_tests()

    print("\n=== Оптимізація вибору їжі в межах бюджету ===")
    try:
        user_budget_str = input("Введіть бюджет (ціле число, наприклад 60): ")
        user_budget = int(user_budget_str)
        if user_budget < 0:
            raise ValueError
    except ValueError:
        print("Некоректний ввід бюджету. Використаємо значення за замовчуванням: 60.")
        user_budget = 60

    demo_for_budget(user_budget)
