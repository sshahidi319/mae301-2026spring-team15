from __future__ import annotations

import argparse

from recommendation_engine import (
    add_log_entry,
    daily_totals,
    estimate_protein_target,
    get_watch_macro_config,
    load_daily_log,
    load_pantry,
    load_profile,
    load_recipes,
    normalize_item,
    pantry_insights,
    parse_pantry_text,
    profile_summary,
    recommend_recipes,
    save_daily_log,
    save_pantry,
    save_profile,
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


def print_insights(results: list[dict]) -> None:
    insights = pantry_insights(results)
    if insights["common_missing"]:
        print("\nQuick next step")
        print("-" * 50)
        top_items = [name for name, _count in insights["common_missing"][:3]]
        print(
            "Add one or two of these ingredients to unlock more recipe options: "
            f"{', '.join(top_items)}"
        )
def maybe_log_recipe(selected: dict, daily_log: dict) -> dict:
    if selected.get("protein") is None and selected.get("calories") is None:
        return daily_log
    if not prompt_yes_no("Add this recipe to today's food tracker?", default=False):
        return daily_log
    updated_log = add_log_entry(
        daily_log,
        selected["title"],
        selected.get("calories"),
        selected.get("protein"),
    )
    save_daily_log(updated_log)
    totals = daily_totals(updated_log)
    print(
        f"Tracked. Today's total: {totals['protein']} g protein, "
        f"{totals['calories']} kcal across {totals['count']} meals."
    )
    return updated_log


def show_recipe_details(results: list[dict], daily_log: dict) -> dict:
    if not results:
        return daily_log
    choice = input("\nEnter a recipe number for full details, or press Enter to go back:\n> ").strip()
    if not choice:
        return daily_log
    if not choice.isdigit():
        print("Please enter a valid recipe number.")
        return daily_log
    index = int(choice) - 1
    if index < 0 or index >= len(results):
        print("That recipe number is out of range.")
        return daily_log

    selected = results[index]
    print(f"\n{selected['title']}")
    print("=" * len(selected["title"]))
    print(f"Macros: {nutrition_summary(selected)}")
    if selected["categories"]:
        print(f"Tags: {', '.join(selected['categories'])}")
    if selected["why"]:
        print(f"Why it was picked: {', '.join(selected['why'])}")
    print(
        f"Pantry items used: "
        f"{', '.join(selected['matched_pantry']) if selected['matched_pantry'] else 'none'}"
    )
    print(
        f"Missing ingredients: "
        f"{', '.join(selected['missing'][:8]) if selected['missing'] else 'none'}"
    )
    print(f"Shopping list: {', '.join(shopping_list_for_recipe(selected)) or 'nothing needed'}")
    print("\nIngredients")
    for line in selected["ingredients"]:
        print(f"- {line}")
    print("\nDirections")
    for step in selected["directions"]:
        print(f"- {step}")
    return maybe_log_recipe(selected, daily_log)


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


def print_goal_status(profile: dict, daily_log: dict) -> None:
    protein_target = profile.get("protein_target")
    if not protein_target:
        return
    totals = daily_totals(daily_log)
    remaining = max(0, int(protein_target - totals["protein"]))
    print("\nProtein goal")
    print("-" * 50)
    print(
        f"Today's progress: {totals['protein']} / {int(protein_target)} g protein"
        f" | Remaining: {remaining} g"
    )


def recommend_flow(recipes: list, pantry: list[str], profile: dict, daily_log: dict) -> dict:
    if not pantry:
        print("Add a few pantry items first so the recommendations are meaningful.")
        return daily_log
    max_calories = prompt_number("Max calories per serving")
    suggested_protein = profile.get("protein_target")
    if suggested_protein:
        print(f"Suggested daily protein target from your profile: {int(suggested_protein)} g")
    min_protein = prompt_number("Minimum protein (grams)")
    watch_macro = input("Any other macros to watch? (optional: sodium or fat)\n> ").strip().lower()
    watch_config = get_watch_macro_config(watch_macro)
    max_sodium = None
    if watch_config:
        _field_name, prompt_label, _unit_label, _prefer_lower = watch_config
        watch_value = prompt_number(prompt_label)
    else:
        watch_value = None
    limit_value = prompt_number("How many recommendations would you like to see")
    limit = int(limit_value) if limit_value else 5

    extra_filters = {}
    if watch_config and watch_value is not None:
        field_name, _prompt_label, _unit_label, _prefer_lower = watch_config
        extra_filters[field_name] = watch_value

    results = recommend_recipes(
        recipes,
        pantry,
        max_calories=max_calories,
        min_protein=min_protein,
        max_sodium=extra_filters.get("sodium"),
        strict=False,
        limit=limit,
    )
    if watch_config and extra_filters.get("fat") is not None:
        max_fat = extra_filters["fat"]
        results = [
            result for result in results
            if result.get("fat") is None or result.get("fat") <= max_fat
        ]
    print_results(results)
    print_insights(results)
    print_goal_status(profile, daily_log)
    return show_recipe_details(results, daily_log)


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


def configure_profile(profile: dict) -> dict:
    print("\nBody goals")
    print("-" * 50)
    current_name = profile.get("name") or "not set"
    print(f"Current profile: {current_name}")
    print(profile_summary(profile))
    name = input("Name (optional):\n> ").strip()
    weight = prompt_number("Weight in pounds")
    height_inches = prompt_number("Enter height in inches")
    goal_choice = input("Goal: cut, maintain, or build muscle [maintain]:\n> ").strip().lower() or "maintain"

    updated = {
        "name": name or profile.get("name", ""),
        "weight": weight,
        "weight_unit": "lb",
        "height_inches": height_inches,
        "goal": goal_choice,
    }
    updated["protein_target"] = estimate_protein_target(
        updated["weight"], updated["weight_unit"], updated["goal"]
    )
    save_profile(updated)
    print("Profile saved.")
    print(profile_summary(updated))
    return updated


def print_tracker(profile: dict, daily_log: dict) -> None:
    totals = daily_totals(daily_log)
    print("\nToday's tracker")
    print("-" * 50)
    print(f"Date: {daily_log['date']}")
    print(f"Meals tracked: {totals['count']}")
    print(f"Protein: {totals['protein']} g")
    print(f"Calories: {totals['calories']} kcal")
    protein_target = profile.get("protein_target")
    if protein_target:
        remaining = max(0, int(protein_target - totals["protein"]))
        print(f"Protein target: {int(protein_target)} g | Remaining: {remaining} g")
    entries = daily_log.get("entries", [])
    if not entries:
        print("No meals tracked yet today.")
        return
    print("\nMeals")
    for index, entry in enumerate(entries, start=1):
        protein = entry.get("protein")
        calories = entry.get("calories")
        protein_text = f"{int(protein)} g protein" if protein is not None else "protein N/A"
        calorie_text = f"{int(calories)} kcal" if calories is not None else "calories N/A"
        print(f"{index}. {entry['title']} | {protein_text} | {calorie_text}")


def add_manual_meal(daily_log: dict) -> dict:
    title = input("Meal name:\n> ").strip()
    if not title:
        print("Meal name is required.")
        return daily_log
    calories = prompt_number("Calories")
    protein = prompt_number("Protein (grams)")
    updated_log = add_log_entry(daily_log, title, calories, protein)
    save_daily_log(updated_log)
    print("Meal added to today's tracker.")
    return updated_log


def tracker_flow(profile: dict, daily_log: dict) -> tuple[dict, dict]:
    while True:
        print("\nBody goals and tracker")
        print("=" * 50)
        print(profile_summary(profile))
        totals = daily_totals(daily_log)
        print(f"Today's protein: {totals['protein']} g | Today's calories: {totals['calories']} kcal")
        print("1. Set body goals")
        print("2. View today's tracker")
        print("3. Add a meal manually")
        print("4. Back to main menu")

        choice = input("> ").strip()
        if choice == "1":
            profile = configure_profile(profile)
        elif choice == "2":
            print_tracker(profile, daily_log)
        elif choice == "3":
            daily_log = add_manual_meal(daily_log)
        elif choice == "4":
            return profile, daily_log
        else:
            print("Choose a number from 1 to 4.")


def interactive_app() -> None:
    recipes = load_recipes()
    pantry = load_pantry()
    profile = load_profile()
    daily_log = load_daily_log()

    while True:
        print("\nShelfAware MVP")
        print("=" * 50)
        print(f"Recipes loaded: {len(recipes)}")
        print(f"Pantry items saved: {len(pantry)}")
        target = profile.get("protein_target")
        if target:
            totals = daily_totals(daily_log)
            print(f"Protein progress today: {totals['protein']} / {int(target)} g")
        print("1. View / edit pantry")
        print("2. Time to cook (find recipes)")
        print("3. Body goals / food tracker")
        print("4. Run quick demo")
        print("5. Save and exit")

        choice = input("> ").strip()
        if choice == "1":
            pantry = pantry_flow(pantry)
        elif choice == "2":
            daily_log = recommend_flow(recipes, pantry, profile, daily_log)
        elif choice == "3":
            profile, daily_log = tracker_flow(profile, daily_log)
        elif choice == "4":
            run_demo(recipes, pantry)
        elif choice == "5":
            save_pantry(pantry)
            save_profile(profile)
            save_daily_log(daily_log)
            print("Pantry saved. Goodbye.")
            return
        else:
            print("Choose a number from 1 to 5.")


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
