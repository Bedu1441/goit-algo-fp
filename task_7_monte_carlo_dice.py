from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List

import matplotlib.pyplot as plt


@dataclass
class ProbabilityTableRow:
    """Одна строка таблиці ймовірностей для певної суми."""
    total: int
    theoretical_prob: float
    empirical_prob: float
    difference: float


# -----------------------------
#   Аналітичні ймовірності
# -----------------------------

def theoretical_probabilities() -> Dict[int, float]:
    """
    Повертає словник {сума: ймовірність} для кидання двох чесних кубиків.
    """
    combinations_count = {
        2: 1,
        3: 2,
        4: 3,
        5: 4,
        6: 5,
        7: 6,
        8: 5,
        9: 4,
        10: 3,
        11: 2,
        12: 1,
    }
    total_outcomes = 36
    return {s: c / total_outcomes for s, c in combinations_count.items()}


# -----------------------------
#   Монте-Карло симуляція
# -----------------------------

def simulate_dice_throws(n_throws: int) -> Counter:
    """
    Імітує n_throws кидків двох кубиків.

    :param n_throws: Кількість кидків.
    :return: Counter, де ключ – сума (2..12), значення – кількість появ цієї суми.
    """
    counter: Counter = Counter()
    for _ in range(n_throws):
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        s = d1 + d2
        counter[s] += 1
    return counter


def empirical_probabilities(counts: Counter, n_throws: int) -> Dict[int, float]:
    """
    Обчислює емпіричні ймовірності на основі підрахунку сум.

    :param counts: Counter із кількістю появ кожної суми.
    :param n_throws: Загальна кількість кидків.
    :return: Словник {сума: емпірична ймовірність}.
    """
    probs: Dict[int, float] = {}
    for total in range(2, 13):
        probs[total] = counts[total] / n_throws
    return probs


# -----------------------------
#   Формування таблиці
# -----------------------------

def build_probability_table(
    theoretical: Dict[int, float],
    empirical: Dict[int, float],
) -> List[ProbabilityTableRow]:
    """
    Формує список рядків таблиці для порівняння теоретичних
    та емпіричних ймовірностей.

    :param theoretical: Теоретичні ймовірності.
    :param empirical: Емпіричні ймовірності.
    :return: Список рядків ProbabilityTableRow.
    """
    table: List[ProbabilityTableRow] = []
    for total in range(2, 13):
        th = theoretical.get(total, 0.0)
        em = empirical.get(total, 0.0)
        diff = em - th
        table.append(ProbabilityTableRow(total, th, em, diff))
    return table


def print_probability_table(table: List[ProbabilityTableRow]) -> None:
    """
    Друкує таблицю ймовірностей у консоль.

    Стовпчики:
        - Сума
        - Теоретична ймовірність
        - Емпірична ймовірність
        - Різниця (Empirical - Theoretical)
    """
    print("\nТаблиця порівняння теоретичних та емпіричних ймовірностей:")
    print("-" * 70)
    print(f"{'Сума':<6} | {'Теоретична':>13} | {'Емпірична':>11} | {'Різниця':>10}")
    print("-" * 70)
    for row in table:
        print(
            f"{row.total:<6} | "
            f"{row.theoretical_prob:>13.4f} | "
            f"{row.empirical_prob:>11.4f} | "
            f"{row.difference:>10.4f}"
        )
    print("-" * 70)

    # Додадкова зведена інформація «понад вимоги»
    avg_abs_diff = sum(abs(r.difference) for r in table) / len(table)
    print(f"Середнє модульне відхилення емпіричних ймовірностей від теоретичних: {avg_abs_diff:.4f}")


# -----------------------------
#   Візуалізація графіком
# -----------------------------

def plot_probabilities(table: List[ProbabilityTableRow]) -> None:
    """
    Будує стовпчиковий графік теоретичних та емпіричних ймовірностей.
    """
    totals = [row.total for row in table]
    th_probs = [row.theoretical_prob for row in table]
    em_probs = [row.empirical_prob for row in table]

    x = range(len(totals))

    width = 0.4

    plt.figure(figsize=(10, 6))
    # Два набори стовпчиків поруч: теоретичні та емпіричні
    plt.bar([i - width / 2 for i in x], th_probs, width=width, label="Теоретична")
    plt.bar([i + width / 2 for i in x], em_probs, width=width, label="Емпірична (Monte Carlo)")

    plt.xticks(list(x), totals)
    plt.xlabel("Сума на двох кубиках")
    plt.ylabel("Ймовірність")
    plt.title("Порівняння теоретичних та емпіричних ймовірностей (Метод Монте-Карло)")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


# -----------------------------
#   Внутрішні тести
# -----------------------------

def _run_simple_tests() -> None:
    """
    Прості тести для перевірки базової коректності.
    """
    print("Запуск внутрішніх тестів для Монте-Карло...")

    th = theoretical_probabilities()
    # Сума теоретичних ймовірностей повинна бути 1
    total_th = sum(th.values())
    assert abs(total_th - 1.0) < 1e-9, "Сума теоретичних ймовірностей повинна дорівнювати 1"

    # Маленька симуляція – емпіричні ймовірності мають бути «близько» до 1 у сумі
    n_test = 1000
    counts_test = simulate_dice_throws(n_test)
    emp_test = empirical_probabilities(counts_test, n_test)
    total_emp = sum(emp_test.values())
    assert abs(total_emp - 1.0) < 1e-9, "Сума емпіричних ймовірностей має бути 1 (з урахуванням усіх сум)"

    print("Усі внутрішні тести пройдено успішно ✅")


# -----------------------------
#   Головна функція
# -----------------------------

def main() -> None:
    """
    Головна функція:
    - зчитує кількість кидків від користувача;
    - проводить симуляцію;
    - порівнює з теоретичними ймовірностями;
    - друкує таблицю;
    - будує графік.
    """
    try:
        user_input = input("Введіть кількість кидків (рекомендовано 10_000 або більше): ")
        n_throws = int(user_input)
        if n_throws <= 0:
            raise ValueError
    except ValueError:
        print("Некоректне значення. Використаємо значення за замовчуванням: 100000.")
        n_throws = 100_000

    print(f"\nЗапускаємо Монте-Карло симуляцію для {n_throws} кидків двох кубиків...")

    counts = simulate_dice_throws(n_throws)
    empirical = empirical_probabilities(counts, n_throws)
    theoretical = theoretical_probabilities()
    table = build_probability_table(theoretical, empirical)

    print_probability_table(table)
    plot_probabilities(table)


if __name__ == "__main__":
    _run_simple_tests()
    main()
