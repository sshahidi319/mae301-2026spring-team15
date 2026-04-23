
from __future__ import annotations

import argparse
from datetime import date

from engine import (
    add_tracker_entry,
    day_totals,
    estimate_calorie_target,
    estimate_protein_target,
    format_metric,
    format_pantry_item,
    format_servings,
    get_watch_macro_config,
    load_pantry,
    load_profile,
    load_recipes,
    load_tracker_history,
    month_totals,
    pantry_insights,
    pantry_name_list,
    parse_inventory_input,
    profile_summary,
    recommend_recipes,
    remove_pantry_items_by_name,
    save_pantry,
    save_profile,
    save_tracker_history,
    scale_ingredient_line,
    shopping_list_for_recipe,
    subtract_recipe_from_pantry,
)


def prompt_number(label: str, default: float | None = None) -> float | None:
    suffix = f" [default {int(default)}]" if default is not None and float(default).is_integer() else (
        f" [default {default}]" if default is not None else ""
    )
    raw = input(f"{label}{suffix}:\n> ").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        print("Please enter a number.")
        return prompt_number(label, default)


def prompt_yes_no(label: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    raw = input(f"{label} [{suffix}]:\n> ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes"}


def prompt_servings(default: float = 1.0) -> float:
    raw = input(f"How many servings? [default {format_servings(default)}]:\n> ").strip()
    if not raw:
        return default
    try:
        value = float(raw)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print("Please enter a positive number.")
        return prompt_servings(default)


def print_pantry(pantry: list[dict]) -> None:
    print("\nCurrent pantry")
    print("-" * 60)
    if not pantry:
        print("Pantry is empty.")
        return
    for item in pantry:
        print(f"- {format_pantry_item(item)}")


def add_items(pantry: list[dict]) -> list[dict]:
    print("\nEnter pantry items, one per line. Examples:")
    print("4 lb flour")
    print("12 eggs")
    print("1 gallon milk")
    print("2 cups rice")
    print("Press Enter on a blank line when finished.\n")

    lines = []
    while True:
        line = input("> ").strip()
        if not line:
            break
        lines.append(line)

    additions = parse_inventory_input("\n".join(lines))
    if not additions:
        print("No valid pantry items were added.")
        return pantry

    updated = pantry + additions
    save_pantry(updated)
    updated = load_pantry()
    print(f"Saved {len(additions)} item(s) to pantry.")
    return updated


def remove_items(pantry: list[dict]) -> list[dict]:
    if not pantry:
        print("Pantry is already empty.")
        return pantry
    raw = input("Enter item names to remove, separated by commas:\n> ").strip()
    updated = remove_pantry_items_by_name(pantry, raw)
    save_pantry(updated)
    print("Pantry updated.")
    return updated


def pantry_flow(pantry: list[dict]) -> list[dict]:
    while True:
        print("\nPantry manager")
        print("=" * 60)
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

def get_serving_hint(recipe_result: dict) -> float:
    return (
        recipe_result.get("recommended_servings")
        or recipe_result.get("suggested_servings")
        or 1.0
    )

def print_results(results: list[dict]) -> None:
    if not results:
        print("\nNo recipes matched those settings.")
        return

    print("\nTop recipe suggestions")
    print("=" * 60)

    for i, r in enumerate(results, start=1):
        servings = get_serving_hint(r)

        print(f"\n{i}. {r['title']}")
        print(
            f"   Per serving: "
            f"{int(r['calories']) if r.get('calories') is not None else 'N/A'} kcal | "
            f"{int(r['protein']) if r.get('protein') is not None else 'N/A'} g protein"
        )
        print(f"   Suggested amount: {format_servings(servings)} servings")
        print(
            f"   At that amount: "
            f"{int(r['scaled_calories']) if r.get('scaled_calories') is not None else 'N/A'} kcal | "
            f"{int(r['scaled_protein']) if r.get('scaled_protein') is not None else 'N/A'} g protein"
        )
        print(f"   Pantry match: {r['matched_count']}/{r['total_ingredients']}")
        print(f"   Fits requested goals: {r.get('fits_goals', False)}")
        print(
            "   Missing ingredients: "
            + (", ".join(r["missing_detailed"][:6]) if r.get("missing_detailed") else "none")
        )

def print_insights(results: list[dict]) -> None:
    insights = pantry_insights(results)
    common_missing = insights.get("common_missing", [])
    if not common_missing:
        return
    print("\nPantry insight")
    print("-" * 60)
    top_items = ", ".join(f"{name} ({count})" for name, count in common_missing[:5])
    print(f"Most common missing ingredients across the top matches: {top_items}")


def print_tracker_day(profile: dict, history: dict, day: str | None = None) -> None:
    totals = day_totals(history, day)
    print(f"\nTracker for {totals['date']}")
    print("-" * 60)
    print(f"Meals tracked: {totals['count']}")
    print(f"Protein: {totals['protein']} g")
    print(f"Calories: {totals['calories']} kcal")

    protein_target = profile.get("protein_target")
    calorie_target = profile.get("calorie_target")

    if protein_target:
        protein_remaining = max(0, int(protein_target - totals["protein"]))
        print(f"Protein target: {int(protein_target)} g | Remaining: {protein_remaining} g")

    if calorie_target:
        calorie_remaining = max(0, int(calorie_target - totals["calories"]))
        print(f"Calorie target: {int(calorie_target)} kcal | Remaining: {calorie_remaining} kcal")

    if not totals["entries"]:
        print("No meals tracked for this day.")
        return

    print("\nMeals")
    for idx, entry in enumerate(totals["entries"], start=1):
        protein = entry.get("protein")
        calories = entry.get("calories")
        servings = entry.get("servings")
        if servings is None:
            servings = 1.0

        protein_text = f"{int(protein)} g protein" if protein is not None else "protein N/A"
        calorie_text = f"{int(calories)} kcal" if calories is not None else "calories N/A"
        servings_text = f"{format_servings(servings)} servings"
        print(f"{idx}. {entry['title']} | {servings_text} | {protein_text} | {calorie_text}")


def print_month_stats(history: dict) -> None:
    month = input("Enter month as YYYY-MM (press Enter for current month):\n> ").strip() or None
    stats = month_totals(history, month)
    print(f"\nMonthly statistics for {stats['month']}")
    print("-" * 60)
    print(f"Days logged: {stats['days_logged']}")
    print(f"Meals tracked: {stats['meals']}")
    print(f"Total calories: {stats['calories']} kcal")
    print(f"Total protein: {stats['protein']} g")
    print(f"Average calories per logged day: {stats['avg_calories_per_logged_day']} kcal")
    print(f"Average protein per logged day: {stats['avg_protein_per_logged_day']} g")


def add_manual_meal(history: dict) -> dict:
    title = input("Meal name:\n> ").strip()
    if not title:
        print("Meal name is required.")
        return history
    entry_date = input("Date (YYYY-MM-DD) [press Enter for today]:\n> ").strip() or str(date.today())
    servings = prompt_servings(1.0)
    calories = prompt_number("Calories")
    protein = prompt_number("Protein (grams)")
    history = add_tracker_entry(history, title, calories, protein, servings, entry_date)
    save_tracker_history(history)
    print("Meal added to tracker history.")
    return history


def tracker_flow(profile: dict, history: dict) -> dict:
    while True:
        today = day_totals(history)
        print("\nFood tracker / history")
        print("=" * 60)
        print(f"Today's protein: {today['protein']} g | Today's calories: {today['calories']} kcal")
        print("1. View today's tracker")
        print("2. View a specific date")
        print("3. Add a meal manually")
        print("4. View monthly statistics")
        print("5. Back to main menu")
        choice = input("> ").strip()

        if choice == "1":
            print_tracker_day(profile, history)
        elif choice == "2":
            chosen_day = input("Enter date as YYYY-MM-DD:\n> ").strip()
            print_tracker_day(profile, history, chosen_day)
        elif choice == "3":
            history = add_manual_meal(history)
        elif choice == "4":
            print_month_stats(history)
        elif choice == "5":
            return history
        else:
            print("Choose a number from 1 to 5.")


def configure_profile(profile: dict) -> dict:
    print("\nPersonalized nutrition goals")
    print("=" * 60)
    print(profile_summary(profile))

    name = input("Name (optional):\n> ").strip() or profile.get("name", "")
    weight = prompt_number("Weight in pounds", profile.get("weight"))
    height_inches = prompt_number("Height in inches", profile.get("height_inches"))

    goal = (
        input("Goal: cut, maintain, or muscle building [maintain]:\n> ").strip().lower()
        or profile.get("goal", "maintain")
    )

    if goal == "bulk":
        goal = "muscle building"

    updated = {
        "name": name,
        "weight": weight,
        "weight_unit": "lb",
        "height_inches": height_inches,
        "goal": goal,
        "protein_target": estimate_protein_target(weight, "lb", goal),
        "calorie_target": estimate_calorie_target(weight, "lb", goal),
    }

    save_profile(updated)
    print("Nutrition profile saved.")
    print(profile_summary(updated))
    return updated


def body_goals_flow(profile: dict) -> dict:
    while True:
        print("\nPersonalized nutrition goals")
        print("=" * 60)
        print(profile_summary(profile))
        print("1. Update nutrition goals")
        print("2. Back to main menu")

        choice = input("> ").strip()
        if choice == "1":
            profile = configure_profile(profile)
        elif choice == "2":
            return profile
        else:
            print("Choose a number from 1 to 2.")


def maybe_log_recipe_to_tracker(selected: dict, history: dict) -> dict:
    if not prompt_yes_no("Add this recipe to the tracker?", default=False):
        return history
    default_servings = get_serving_hint(selected) 
    servings = prompt_servings(default_servings)
    calories = (selected.get("calories") or 0) * servings if selected.get("calories") is not None else None
    protein = (selected.get("protein") or 0) * servings if selected.get("protein") is not None else None
    history = add_tracker_entry(
        history,
        selected["title"],
        calories,
        protein,
        servings,
        str(date.today()),
    )
    save_tracker_history(history)
    print("Recipe added to today's tracker.")
    return history


def maybe_update_pantry(selected: dict, pantry: list[dict]) -> list[dict]:
    if not prompt_yes_no("Update pantry based on this recipe?", default=False):
        return pantry

    default_servings = get_serving_hint(selected)
    servings = prompt_servings(default_servings)
    updated, summary = subtract_recipe_from_pantry(pantry, selected, servings)
    save_pantry(updated)

    print("\nPantry update summary")
    print("-" * 60)
    if summary["changes"]:
        print("Updated items:")
        for change in summary["changes"]:
            print(f"- Used {change['used']} -> {change['remaining']}")
    if summary["skipped"]:
        print("\nSkipped items:")
        for item in summary["skipped"][:12]:
            print(f"- {item}")
    if not summary["changes"] and not summary["skipped"]:
        print("No pantry changes were made.")

    return updated


def show_recipe_details(results: list[dict], pantry: list[dict], history: dict) -> tuple[list[dict], dict]:
    if not results:
        return pantry, history

    choice = input("\nEnter a recipe number for full details, or press Enter to go back:\n> ").strip()
    if not choice:
        return pantry, history
    if not choice.isdigit():
        print("Please enter a valid recipe number.")
        return pantry, history

    index = int(choice) - 1
    if index < 0 or index >= len(results):
        print("That recipe number is out of range.")
        return pantry, history

    selected = results[index]
    print(f"\n{selected['title']}")
    print("=" * len(selected["title"]))
    if selected.get("url"):
        print(f"Recipe link: {selected['url']}")
    print(f"Per serving calories: {int(selected['calories']) if selected.get('calories') is not None else 'N/A'} kcal")
    print(f"Per serving protein: {int(selected['protein']) if selected.get('protein') is not None else 'N/A'} g")
    print(f"Per serving carbs: {int(selected['carbs']) if selected.get('carbs') is not None else 'N/A'} g")
    print(f"Per serving fat: {int(selected['fat']) if selected.get('fat') is not None else 'N/A'} g")
    print(f"Suggested amount for your goal: {format_servings(get_serving_hint(selected))} servings")
    print(f"At that amount: "
          f"{int(selected['scaled_calories']) if selected.get('scaled_calories') is not None else 'N/A'} kcal, "
          f"{int(selected['scaled_protein']) if selected.get('scaled_protein') is not None else 'N/A'} g protein")
    if selected["categories"]:
        print(f"Tags: {', '.join(selected['categories'])}")
    if selected.get("why"):
        print(f"Why it was picked: {', '.join(selected['why'])}")
    print(
        "Pantry items used: "
        + (", ".join(selected["matched_pantry"]) if selected["matched_pantry"] else "none")
    )
    print(
        "Missing ingredients: "
        + (", ".join(selected["missing_detailed"][:10]) if selected.get("missing_detailed") else "none")
    )
    shopping_list = shopping_list_for_recipe(selected)
    print("Shopping list: " + (", ".join(shopping_list) if shopping_list else "nothing needed"))

    print("\nIngredients")
    for line in selected["ingredients"]:
        print(f"- {line}")

    if get_serving_hint(selected) and abs(get_serving_hint(selected) - 1.0) > 1e-6:
        print("\nScaled ingredients for your target")
        for line in selected["ingredients"]:
            print(f"- {scale_ingredient_line(line, get_serving_hint(selected))}")

    history = maybe_log_recipe_to_tracker(selected, history)
    pantry = maybe_update_pantry(selected, pantry)
    return pantry, history


def recommend_flow(recipes: list, pantry: list[dict], profile: dict, history: dict) -> tuple[list[dict], dict]:
    if not pantry:
        print("Add a few pantry items first so the recommendations are meaningful.")
        return pantry, history

    daily_calories = profile.get("calorie_target")
    daily_protein = profile.get("protein_target")

    if daily_calories:
        print(f"Estimated daily calorie target from your profile: {int(daily_calories)} kcal/day")
    if daily_protein:
        print(f"Estimated daily protein target from your profile: {int(daily_protein)} g/day")

    max_calories = prompt_number("Enter max calories for this meal", 600)
    min_protein = prompt_number("Enter minimum protein in grams for this meal", 20)

    watch_macro = input("Optional extra macro to limit (sodium or fat, press Enter to skip):\n> ").strip().lower()
    max_sodium = None
    max_fat = None
    config = get_watch_macro_config(watch_macro)
    if config:
        field_name, prompt_label, _unit_label, _prefer_lower = config
        extra_limit = prompt_number(prompt_label)
        if field_name == "sodium":
            max_sodium = extra_limit
        elif field_name == "fat":
            max_fat = extra_limit

    limit_value = prompt_number("How many recommendations would you like to see", 4)
    limit = int(limit_value) if limit_value else 4

    used_fallback = False

    results = recommend_recipes(
        recipes,
        pantry,
        max_calories=max_calories,
        min_protein=min_protein,
        max_sodium=max_sodium,
        max_fat=max_fat,
        strict=True,
        limit=limit,
    )

    if not results:
        results = recommend_recipes(
            recipes,
            pantry,
            max_calories=max_calories,
            min_protein=min_protein,
            max_sodium=max_sodium,
            max_fat=max_fat,
            strict=False,
            limit=limit,
        )
        used_fallback = bool(results)

    if not results and min_protein is not None:
        relaxed_protein = max(0, min_protein * 0.75)
        results = recommend_recipes(
            recipes,
            pantry,
            max_calories=max_calories,
            min_protein=relaxed_protein,
            max_sodium=max_sodium,
            max_fat=max_fat,
            strict=False,
            limit=limit,
        )
        used_fallback = bool(results)

    if used_fallback:
        print("\nNo recipes met all goals exactly.")
        print("Showing closest matches instead.")

    if not results:
        print("\nNo recipes matched those settings, even after relaxing the search.")
        return pantry, history

    print_pantry(pantry)
    print_results(results)
    print_insights(results)
    pantry, history = show_recipe_details(results, pantry, history)
    return pantry, history


def run_demo(recipes: list, pantry: list[dict]) -> None:
    if not pantry:
        pantry = parse_inventory_input("1 lb chicken\n2 cups rice\n6 eggs\n2 tbsp olive oil\n2 cups spinach")
    results = recommend_recipes(
        recipes,
        pantry,
        max_calories=650,
        min_protein=20,
        strict=True,
        limit=4,
    )
    print("ShelfAware Demo")
    print("-" * 60)
    print_pantry(pantry)
    print_results(results)
    print_insights(results)


def interactive_app() -> None:
    recipes = load_recipes()
    pantry = load_pantry()
    profile = load_profile()
    history = load_tracker_history()

    while True:
        print("\nShelfAware MVP")
        print("=" * 60)
        print(f"Recipes loaded: {len(recipes)}")
        print(f"Pantry items saved: {len(pantry_name_list(pantry))}")
        target = profile.get("protein_target")
        today = day_totals(history)
        protein_target = profile.get("protein_target")
        calorie_target = profile.get("calorie_target")

        if protein_target:
            print(f"Protein progress today: {today['protein']} / {int(protein_target)} g")
        if calorie_target:
            print(f"Calorie progress today: {today['calories']} / {int(calorie_target)} kcal")

        print("1. View / edit pantry")
        print("2. Recipe generator")
        print("3. Personalized nutrition goals")
        print("4. Food tracker / history")
        print("5. Run quick demo")
        print("6. Save and exit")

        choice = input("> ").strip()
        if choice == "1":
            pantry = pantry_flow(pantry)
        elif choice == "2":
            pantry, history = recommend_flow(recipes, pantry, profile, history)
        elif choice == "3":
            profile = body_goals_flow(profile)
        elif choice == "4":
            history = tracker_flow(profile, history)
        elif choice == "5":
            run_demo(recipes, pantry)
        elif choice == "6":
            save_pantry(pantry)
            save_profile(profile)
            save_tracker_history(history)
            print("Saved. Goodbye.")
            return
        else:
            print("Choose a number from 1 to 6.")


def main() -> None:
    parser = argparse.ArgumentParser(description="ShelfAware medium-version MVP")
    parser.add_argument("--demo", action="store_true", help="run a built-in demo")
    args = parser.parse_args()

    recipes = load_recipes()
    if args.demo:
        pantry = load_pantry()
        run_demo(recipes, pantry)
        return
    interactive_app()


if __name__ == "__main__":
    main()
