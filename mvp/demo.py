import re

RECIPES = [
    {
        "title": "Chicken Spinach Rice Bowl",
        "ingredients": ["chicken", "spinach", "rice", "olive oil", "garlic"],
        "calories": 540,
        "protein": 58,
        "carbs": 42,
        "fat": 14,
    },
    {
        "title": "High Protein Egg Fried Rice",
        "ingredients": ["eggs", "rice", "spinach", "soy sauce", "olive oil"],
        "calories": 510,
        "protein": 30,
        "carbs": 46,
        "fat": 20,
    },
    {
        "title": "Garlic Chicken Skillet",
        "ingredients": ["chicken", "garlic", "olive oil", "onion", "spinach"],
        "calories": 430,
        "protein": 52,
        "carbs": 10,
        "fat": 18,
    },
    {
        "title": "Peanut Butter Banana Toast",
        "ingredients": ["bread", "peanut butter", "banana", "honey"],
        "calories": 390,
        "protein": 13,
        "carbs": 45,
        "fat": 18,
    },
    {
        "title": "Garden Salad with Eggs",
        "ingredients": ["eggs", "mixed greens", "cucumber", "onion", "vinaigrette"],
        "calories": 280,
        "protein": 16,
        "carbs": 12,
        "fat": 18,
    },
    {
        "title": "Chicken Rice Stir Fry",
        "ingredients": ["chicken", "rice", "soy sauce", "garlic", "onion"],
        "calories": 560,
        "protein": 50,
        "carbs": 48,
        "fat": 15,
    },
]

ALIASES = {
    "chicken breast": "chicken",
    "brown rice": "rice",
    "white rice": "rice",
    "baby spinach": "spinach",
    "egg": "eggs",
    "garlic cloves": "garlic",
    "whole wheat bread": "bread",
    "salad greens": "mixed greens",
}

def normalize_item(item: str) -> str:
    item = item.lower().strip()
    item = re.sub(r"[^a-z\s]", "", item)
    item = re.sub(r"\s+", " ", item).strip()
    return ALIASES.get(item, item)

def parse_manual_pantry(text: str):
    raw_items = text.split(",")
    cleaned = [normalize_item(x) for x in raw_items if x.strip()]
    return sorted(set(cleaned))

def score_recipe(recipe, pantry, max_calories, min_protein):
    pantry_set = set(pantry)
    recipe_items = set(recipe["ingredients"])
    matched = len(recipe_items & pantry_set)
    missing = sorted(recipe_items - pantry_set)

    calorie_ok = recipe["calories"] <= max_calories
    protein_ok = recipe["protein"] >= min_protein

    score = matched * 10
    if calorie_ok:
        score += 5
    else:
        score -= 8

    if protein_ok:
        score += 5
    else:
        score -= 8

    return {
        "title": recipe["title"],
        "matched_count": matched,
        "total_ingredients": len(recipe_items),
        "missing": missing,
        "calories": recipe["calories"],
        "protein": recipe["protein"],
        "carbs": recipe["carbs"],
        "fat": recipe["fat"],
        "score": score,
        "calorie_ok": calorie_ok,
        "protein_ok": protein_ok,
    }

def suggest_recipes(pantry, max_calories, min_protein, top_k=4):
    scored = [
        score_recipe(recipe, pantry, max_calories, min_protein)
        for recipe in RECIPES
    ]
    scored.sort(key=lambda x: (x["score"], x["matched_count"], x["protein"]), reverse=True)
    return scored[:top_k]

def print_results(results):
    print("\nTop recipe suggestions")
    print("=" * 50)
    for i, r in enumerate(results, start=1):
        print(f"\n{i}. {r['title']}")
        print(f"   Calories: {r['calories']} kcal")
        print(f"   Protein:  {r['protein']} g")
        print(f"   Carbs:    {r['carbs']} g")
        print(f"   Fat:      {r['fat']} g")
        print(f"   Pantry match: {r['matched_count']}/{r['total_ingredients']}")
        print(f"   Meets calorie target: {r['calorie_ok']}")
        print(f"   Meets protein target: {r['protein_ok']}")
        if r["missing"]:
            print(f"   Missing ingredients: {', '.join(r['missing'])}")
        else:
            print("   Missing ingredients: none")

def main():
    print("ShelfAware Phase 2 Demo")
    print("-" * 50)
    print("Press Enter to use the built-in demo example.")
    pantry_input = input(
        "Enter pantry ingredients separated by commas\n"
        "(example: chicken, eggs, spinach, rice, olive oil):\n> "
    ).strip()

    if not pantry_input:
        pantry_input = "chicken, eggs, spinach, rice, olive oil"

    max_calories_input = input("Enter max calories per serving [default 600]:\n> ").strip()
    min_protein_input = input("Enter minimum protein in grams [default 40]:\n> ").strip()

    max_calories = int(max_calories_input) if max_calories_input else 600
    min_protein = int(min_protein_input) if min_protein_input else 40

    pantry = parse_manual_pantry(pantry_input)

    print("\nNormalized pantry:")
    print(", ".join(pantry))

    results = suggest_recipes(pantry, max_calories, min_protein, top_k=4)
    print_results(results)

if __name__ == "__main__":
    main()
