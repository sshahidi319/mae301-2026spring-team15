from __future__ import annotations

import argparse

from engine import (
    load_pantry,
    load_recipes,
    normalize_item,
    pantry_insights,
    parse_pantry_text,
    recommend_recipes,
    save_pantry,
    shopping_list_for_recipe,
    nutrition_summary,
)


def prompt_number(label: str) -> float | None:
    raw = input(f"{label} (press Enter to skip):\n> ").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        print("Please enter a number.")
        return prompt_number(label)


def prompt_yes_no(label: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    raw = input(f"{label} [{suffix}]:\n> ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes"}


def print_pantry(pantry: list[str]) -> None:
    print("\nCurrent pantry")
    print("-" * 50)
    if not pantry:
        print("Pantry is empty.")
        return
    print(", ".join(pantry))


def print_results(results: list[dict]) -> None:
    if not results:
        print("\nNo recipes matched those settings.")
        return

    print("\nTop recommendations")
    print("=" * 72)
    for index, result in enumerate(results, start=1):
        coverage = int(result["coverage"] * 100)
        print(f"\n{index}. {result['title']}")
        print(f"   Fit score: {result['score']:.1f} | Pantry coverage: {coverage}%")
        print(f"   Macros: {nutrition_summary(result)}")
        if result["why"]:
            print(f"   Why it was picked: {', '.join(result['why'])}")
        print(
            f"   Pantry items used: "
            f"{', '.join(result['matched_pantry']) if result['matched_pantry'] else 'none'}"
        )
        print(
            f"   Missing ingredients: "
            f"{', '.join(result['missing'][:5]) if result['missing'] else 'none'}"
        )


def print_insights(results: list[dict]) -> None:
    insights = pantry_insights(results)
    if insights["common_missing"]:
        print("\nPantry insight")
        print("-" * 50)
        common = ", ".join(f"{name} ({count})" for name, count in insights["common_missing"])
        print(f"Most common missing ingredients across the top matches: {common}")


def show_recipe_details(results: list[dict]) -> None:
    if not results:
        return
    choice = input("\nEnter a recipe number for full details, or press Enter to go back:\n> ").strip()
    if not choice:
        return
    if not choice.isdigit():
        print("Please enter a valid recipe number.")
        return
    index = int(choice) - 1
    if index < 0 or index >= len(results):
        print("That recipe number is out of range.")
        return

    selected = results[index]
    print(f"\n{selected['title']}")
    print("=" * len(selected["title"]))
    print(f"Macros: {nutrition_summary(selected)}")
    if selected["categories"]:
        print(f"Tags: {', '.join(selected['categories'])}")
    print(f"Shopping list: {', '.join(shopping_list_for_recipe(selected)) or 'nothing needed'}")
    print("\nIngredients")
    for line in selected["ingredients"]:
        print(f"- {line}")
    print("\nDirections")
    for step in selected["directions"]:
        print(f"- {step}")


def add_items(pantry: list[str]) -> list[str]:
    raw = input("Enter items to add, separated by commas:\n> ").strip()
    additions = parse_pantry_text(raw)
    merged = sorted(set(pantry) | set(additions))
    save_pantry(merged)
    print(f"Saved {len(additions)} item(s) to pantry.")
    return merged


def remove_items(pantry: list[str]) -> list[str]:
    if not pantry:
        print("Pantry is already empty.")
        return pantry
    raw = input("Enter items to remove, separated by commas:\n> ").strip()
    removals = {normalize_item(item) for item in raw.split(",") if normalize_item(item)}
    updated = sorted(item for item in pantry if item not in removals)
    save_pantry(updated)
    print(f"Removed {len(set(pantry) - set(updated))} item(s).")
    return updated


def pantry_flow(pantry: list[str]) -> list[str]:
    while True:
        print("\nPantry manager")
        print("-" * 50)
        print_pantry(pantry)
        print("\n1. Add pantry items")
        print("2. Remove pantry items")
        print("3. Back to main menu")

        choice = input("> ").strip()
        if choice == "1":
            pantry = add_items(pantry)
        elif choice == "2":
            pantry = remove_items(pantry)
        elif choice == "3":
            return pantry
        else:
            print("Choose a number from 1 to 3.")


def recommend_flow(recipes: list, pantry: list[str]) -> None:
    if not pantry:
        print("Add a few pantry items first so the recommendations are meaningful.")
        return
    max_calories = prompt_number("Max calories per serving")
    min_protein = prompt_number("Minimum protein (grams)")
    max_sodium = prompt_number("Maximum sodium (mg)")
    category = input("Category keyword, such as Soup, Dinner, Chicken, Vegetarian (optional):\n> ").strip()
    strict = prompt_yes_no("Use strict filtering so recipes outside your targets are hidden?", default=False)
    limit_value = prompt_number("How many recommendations would you like to see")
    limit = int(limit_value) if limit_value else 5

    results = recommend_recipes(
        recipes,
        pantry,
        max_calories=max_calories,
        min_protein=min_protein,
        max_sodium=max_sodium,
        category=category or None,
        strict=strict,
        limit=limit,
    )
    print_results(results)
    print_insights(results)
    show_recipe_details(results)


def run_demo(recipes: list, pantry: list[str]) -> None:
    demo_pantry = pantry if len(pantry) >= 3 else parse_pantry_text(
        "chicken, rice, spinach, onion, garlic, olive oil, eggs"
    )
    results = recommend_recipes(
        recipes,
        demo_pantry,
        max_calories=650,
        min_protein=30,
        max_sodium=900,
        strict=True,
        limit=5,
    )
    print("ShelfAware Phase 3 Demo")
    print("-" * 72)
    print(f"Using pantry: {', '.join(demo_pantry)}")
    print_results(results)
    print_insights(results)


def interactive_app() -> None:
    recipes = load_recipes()
    pantry = load_pantry()

    while True:
        print("\nShelfAware MVP")
        print("=" * 50)
        print(f"Recipes loaded: {len(recipes)}")
        print(f"Pantry items saved: {len(pantry)}")
        print("1. View / Edit pantry")
        print("2. Time to Cook (find recipes)")
        print("3. Run quick demo")
        print("4. Save and exit")

        choice = input("> ").strip()
        if choice == "1":
            pantry = pantry_flow(pantry)
        elif choice == "2":
            recommend_flow(recipes, pantry)
        elif choice == "3":
            run_demo(recipes, pantry)
        elif choice == "4":
            save_pantry(pantry)
            print("Pantry saved. Goodbye.")
            return
        else:
            print("Choose a number from 1 to 4.")


def main() -> None:
    parser = argparse.ArgumentParser(description="ShelfAware MVP demo")
    parser.add_argument("--demo", action="store_true", help="run a scripted non-interactive demo")
    args = parser.parse_args()

    recipes = load_recipes()
    if args.demo:
        pantry = load_pantry()
        run_demo(recipes, pantry)
        return
    interactive_app()


if __name__ == "__main__":
    main()
