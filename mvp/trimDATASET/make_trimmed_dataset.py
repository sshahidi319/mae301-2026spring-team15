import ast
import json
import math
import sys
from pathlib import Path

import pandas as pd


def clean_text(value):
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    if text.lower() in {"nan", "none", "null", "na"}:
        return ""
    return text


def parse_number(value):
    text = clean_text(value)
    if not text:
        return None
    try:
        x = float(text)
        if math.isnan(x):
            return None
        return x
    except Exception:
        return None


def parse_literal(value):
    """
    Parse stringified Python/JSON-like objects such as:
    - "['a', 'b']"
    - '{"PROCNT": {...}}'
    """
    text = clean_text(value)
    if not text:
        return None
    try:
        return ast.literal_eval(text)
    except Exception:
        return None


def parse_list_field(value):
    text = clean_text(value)
    if not text:
        return []

    parsed = parse_literal(text)
    if isinstance(parsed, list):
        items = []
        for item in parsed:
            item_text = clean_text(item)
            if item_text:
                items.append(item_text)
        return items

    if "\n" in text:
        return [clean_text(x) for x in text.splitlines() if clean_text(x)]

    return [text]


def parse_dict_field(value):
    text = clean_text(value)
    if not text:
        return {}

    parsed = parse_literal(text)
    if isinstance(parsed, dict):
        return parsed

    return {}


def dedupe_keep_order(items):
    seen = set()
    output = []
    for item in items:
        key = item.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def safe_divide(value, servings):
    if value is None:
        return None
    if servings is None or servings <= 0:
        return value
    return value / servings


def extract_nutrient(total_nutrients, key):
    """
    Expected format:
    {
        "PROCNT": {"unit": "g", "label": "Protein", "quantity": 19.5},
        ...
    }
    """
    if not isinstance(total_nutrients, dict):
        return None
    nutrient = total_nutrients.get(key)
    if not isinstance(nutrient, dict):
        return None
    return parse_number(nutrient.get("quantity"))


def first_existing_column(df, candidates):
    lowered = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    return None


def build_categories(row, cols):
    categories = []
    for col in cols:
        if col not in row:
            continue
        value = row.get(col)

        parsed = parse_literal(value)
        if isinstance(parsed, list):
            for item in parsed:
                item_text = clean_text(item)
                if item_text:
                    categories.append(item_text)
        else:
            text = clean_text(value)
            if text:
                categories.append(text)

    return dedupe_keep_order(categories)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 make_trimmed_dataset.py <input.csv> [limit]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    limit = 2000
    if len(sys.argv) >= 3:
        try:
            limit = int(sys.argv[2])
        except ValueError:
            print("Limit must be an integer.")
            sys.exit(1)

    output_path = Path("full_format_recipes.json")

    print("Reading CSV...")
    df = pd.read_csv(input_path, low_memory=False)
    print(f"Loaded rows: {len(df)}")
    print("Columns found:")
    print(df.columns.tolist())

    title_col = first_existing_column(df, ["recipe_name", "title", "name"])
    url_col = first_existing_column(df, ["url", "link"])
    servings_col = first_existing_column(df, ["servings"])
    calories_col = first_existing_column(df, ["calories"])
    ingredient_lines_col = first_existing_column(df, ["ingredient_lines"])
    total_nutrients_col = first_existing_column(df, ["total_nutrients"])

    category_cols = []
    for candidate in ["source", "cuisine_type", "meal_type", "dish_type", "diet_labels", "health_labels"]:
        col = first_existing_column(df, [candidate])
        if col:
            category_cols.append(col)

    print("\nDetected columns:")
    print("title:", title_col)
    print("servings:", servings_col)
    print("calories:", calories_col)
    print("ingredient_lines:", ingredient_lines_col)
    print("total_nutrients:", total_nutrients_col)
    print("categories:", category_cols)
    print("url:", url_col)

    if not title_col or not ingredient_lines_col:
        print("\nCould not find required columns.")
        print("Need at least recipe_name/title and ingredient_lines.")
        sys.exit(1)

    recipes = []

    for _, row in df.iterrows():
        title = clean_text(row.get(title_col))
        if not title:
            continue

        servings = parse_number(row.get(servings_col)) if servings_col else None
        calories_total = parse_number(row.get(calories_col)) if calories_col else None

        ingredient_lines = parse_list_field(row.get(ingredient_lines_col))
        if not ingredient_lines:
            continue

        total_nutrients = parse_dict_field(row.get(total_nutrients_col)) if total_nutrients_col else {}

        protein_total = extract_nutrient(total_nutrients, "PROCNT")
        carbs_total = extract_nutrient(total_nutrients, "CHOCDF")
        fat_total = extract_nutrient(total_nutrients, "FAT")
        sodium_total = extract_nutrient(total_nutrients, "NA")

        categories = build_categories(row, category_cols)


        recipe = {
            "title": title,
            "url": clean_text(row.get(url_col)) if url_col else "",
            "ingredients": dedupe_keep_order(ingredient_lines),
            "categories": categories,
            "calories": safe_divide(calories_total, servings),
            "protein": safe_divide(protein_total, servings),
            "carbs": safe_divide(carbs_total, servings),
            "fat": safe_divide(fat_total, servings),
            "sodium": safe_divide(sodium_total, servings),
            "rating": None,
        }

        if not recipe["ingredients"]:
            continue

        recipes.append(recipe)

        if len(recipes) >= limit:
            break

    output_path.write_text(json.dumps(recipes, indent=2))
    print(f"\nSaved {len(recipes)} recipes to {output_path}")

    if recipes:
        print("\nSample recipe preview:")
        print("Title:", recipes[0]["title"])
        print("Ingredients:", recipes[0]["ingredients"][:6])
        print("Calories per serving:", recipes[0]["calories"])
        print("Protein per serving:", recipes[0]["protein"])
        print("Carbs per serving:", recipes[0]["carbs"])
        print("Fat per serving:", recipes[0]["fat"])
        print("Sodium per serving:", recipes[0]["sodium"])


if __name__ == "__main__":
    main()
