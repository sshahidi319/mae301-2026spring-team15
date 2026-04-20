from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from datetime import date


DATA_PATH = Path(__file__).with_name("full_format_recipes.json")
PANTRY_PATH = Path(__file__).with_name("pantry.json")
PROFILE_PATH = Path(__file__).with_name("profile.json")
DAILY_LOG_PATH = Path(__file__).with_name("daily_log.json")
_RECIPE_CACHE: list["Recipe"] | None = None
_TOKEN_INDEX: dict[str, list[int]] | None = None

ALIASES = {
    "chicken breast": "chicken",
    "chicken thighs": "chicken",
    "ground chicken": "chicken",
    "turkey breast": "turkey",
    "ground turkey": "turkey",
    "ground beef": "beef",
    "lean ground beef": "beef",
    "salmon fillet": "salmon",
    "tuna fish": "tuna",
    "baby spinach": "spinach",
    "mixed greens": "greens",
    "romaine lettuce": "lettuce",
    "brown rice": "rice",
    "white rice": "rice",
    "jasmine rice": "rice",
    "whole wheat bread": "bread",
    "bread crumbs": "breadcrumbs",
    "vegetable oil": "oil",
    "canola oil": "oil",
    "garlic cloves": "garlic",
    "green onions": "scallions",
    "spring onions": "scallions",
    "bell peppers": "bell pepper",
    "black beans": "beans",
    "kidney beans": "beans",
    "garbanzo beans": "chickpeas",
}

STOPWORDS = {
    "a", "an", "and", "or", "for", "with", "to", "of", "in", "on", "plus",
    "fresh", "dried", "dry", "low", "sodium", "less", "more", "extra", "virgin",
    "boneless", "skinless", "halved", "halves", "large", "small", "medium",
    "whole", "plain", "reduced", "fat", "free", "lean", "optional", "taste",
    "ground", "chopped", "diced", "sliced", "minced", "crushed", "shredded",
    "grated", "peeled", "seeded", "cooked", "uncooked", "frozen", "thawed",
    "packed", "divided", "warm", "cold", "hot", "softened", "melted", "beaten",
    "rinsed", "drained", "cubed", "cut", "thinly", "thickly", "coarsely",
    "finely", "such", "as", "needed", "serving", "serve", "garnish", "freshly",
    "about", "lengthwise", "crosswise", "possible", "coarse", "stem", "stems",
    "leaf", "leaves", "baby", "pieces", "piece", "diagonal", "halved",
}

UNITS = {
    "cup", "cups", "tablespoon", "tablespoons", "tbsp", "teaspoon", "teaspoons",
    "tsp", "ounce", "ounces", "oz", "pound", "pounds", "lb", "lbs", "gram",
    "grams", "g", "kg", "ml", "l", "pinch", "pinches", "clove", "cloves",
    "slice", "slices", "can", "cans", "package", "packages", "jar", "jars",
    "bunch", "bunches", "stalk", "stalks", "sprig", "sprigs", "head", "heads",
    "bag", "bags",
}

NUTRITION_LABELS = (
    ("calories", "kcal"),
    ("protein", "g protein"),
    ("fat", "g fat"),
    ("sodium", "mg sodium"),
)

WATCHABLE_MACROS = {
    "fat": ("fat", "Max fat (grams)", "g fat", True),
    "sodium": ("sodium", "Max sodium (mg)", "mg sodium", True),
}

GENERIC_INGREDIENTS = {
    "oil", "olive oil", "salt", "pepper", "black pepper", "water", "sugar",
    "flour", "butter",
}


@dataclass
class Recipe:
    title: str
    ingredients: list[str]
    directions: list[str]
    categories: list[str]
    calories: float | None
    protein: float | None
    fat: float | None
    sodium: float | None
    rating: float | None
    ingredient_index: list[str]
    search_terms: set[str]


def _clean_text(text: str) -> str:
    text = str(text).lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_item(text: str) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""
    for source, target in sorted(ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if source in cleaned:
            cleaned = cleaned.replace(source, target)
    tokens = [
        token
        for token in cleaned.split()
        if token not in STOPWORDS and token not in UNITS and len(token) > 1
    ]
    if not tokens:
        return ""
    normalized = " ".join(tokens[:3])
    return ALIASES.get(normalized, normalized)


def parse_pantry_text(text: str) -> list[str]:
    items = [normalize_item(chunk) for chunk in text.split(",")]
    deduped = sorted({item for item in items if item})
    return deduped


def load_pantry(path: Path = PANTRY_PATH) -> list[str]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    pantry = sorted({normalize_item(item) for item in data if normalize_item(item)})
    return pantry


def save_pantry(pantry: list[str], path: Path = PANTRY_PATH) -> None:
    path.write_text(json.dumps(sorted(pantry), indent=2))


def load_profile(path: Path = PROFILE_PATH) -> dict:
    default = {
        "name": "",
        "weight": None,
        "weight_unit": "lb",
        "height_feet": None,
        "height_inches": None,
        "goal": "maintain",
        "protein_target": None,
    }
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default
    if not isinstance(data, dict):
        return default
    default.update(data)
    return default


def save_profile(profile: dict, path: Path = PROFILE_PATH) -> None:
    path.write_text(json.dumps(profile, indent=2))


def estimate_protein_target(weight: float | None, weight_unit: str = "lb", goal: str = "maintain") -> float | None:
    if weight is None or weight <= 0:
        return None
    if weight_unit.lower() == "kg":
        weight_lb = weight * 2.20462
    else:
        weight_lb = weight
    multiplier = {
        "cut": 0.8,
        "maintain": 0.9,
        "build muscle": 1.0,
    }.get(goal.lower(), 0.9)
    return round(weight_lb * multiplier)


def profile_summary(profile: dict) -> str:
    height_inches = profile.get("height_inches")
    height_text = f"{int(height_inches)} in" if height_inches is not None else "not set"
    weight = profile.get("weight")
    protein_target = profile.get("protein_target")
    target_text = f"{int(protein_target)} g/day" if protein_target else "not set"
    return (
        f"Goal: {profile.get('goal', 'maintain')} | "
        f"Weight: {weight if weight is not None else 'not set'} lb | "
        f"Height: {height_text} | "
        f"Protein target: {target_text}"
    )


def load_daily_log(path: Path = DAILY_LOG_PATH) -> dict:
    default = {"date": str(date.today()), "entries": []}
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return default
    if not isinstance(data, dict):
        return default
    if data.get("date") != str(date.today()):
        return default
    entries = data.get("entries")
    if not isinstance(entries, list):
        return default
    return {"date": data["date"], "entries": entries}


def save_daily_log(log: dict, path: Path = DAILY_LOG_PATH) -> None:
    path.write_text(json.dumps(log, indent=2))


def add_log_entry(log: dict, title: str, calories: float | None, protein: float | None) -> dict:
    if log.get("date") != str(date.today()):
        log = {"date": str(date.today()), "entries": []}
    log.setdefault("entries", []).append(
        {
            "title": title,
            "calories": calories,
            "protein": protein,
        }
    )
    return log


def daily_totals(log: dict) -> dict:
    entries = log.get("entries", [])
    calories = sum(entry.get("calories") or 0 for entry in entries)
    protein = sum(entry.get("protein") or 0 for entry in entries)
    return {
        "calories": round(calories),
        "protein": round(protein),
        "count": len(entries),
    }


def _coerce_number(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def load_recipes(path: Path = DATA_PATH) -> list[Recipe]:
    global _RECIPE_CACHE, _TOKEN_INDEX
    if path == DATA_PATH and _RECIPE_CACHE is not None:
        return _RECIPE_CACHE
    raw = json.loads(path.read_text())
    recipes: list[Recipe] = []
    token_index: dict[str, list[int]] = {}
    for row in raw:
        title = str(row.get("title") or "").strip()
        ingredients = [str(item).strip() for item in row.get("ingredients") or [] if str(item).strip()]
        directions = [str(item).strip() for item in row.get("directions") or [] if str(item).strip()]
        categories = [str(item).strip() for item in row.get("categories") or [] if str(item).strip()]
        if not title or not ingredients:
            continue
        index = []
        for ingredient in ingredients:
            normalized = normalize_item(ingredient)
            if normalized:
                index.append(normalized)
        if not index:
            continue
        recipe = Recipe(
                title=title,
                ingredients=ingredients,
                directions=directions,
                categories=categories,
                calories=_coerce_number(row.get("calories")),
                protein=_coerce_number(row.get("protein")),
                fat=_coerce_number(row.get("fat")),
                sodium=_coerce_number(row.get("sodium")),
                rating=_coerce_number(row.get("rating")),
                ingredient_index=sorted(set(index)),
                search_terms={
                    token
                    for item in index
                    for token in item.split()
                    if token not in GENERIC_INGREDIENTS
                },
            )
        recipes.append(recipe)
        recipe_index = len(recipes) - 1
        for token in recipe.search_terms:
            token_index.setdefault(token, []).append(recipe_index)
    if path == DATA_PATH:
        _RECIPE_CACHE = recipes
        _TOKEN_INDEX = token_index
    return recipes


def _ingredients_match(pantry_item: str, recipe_item: str) -> bool:
    if pantry_item == recipe_item:
        return True
    pantry_tokens = set(pantry_item.split())
    recipe_tokens = set(recipe_item.split())
    if pantry_tokens and recipe_tokens and pantry_tokens <= recipe_tokens:
        return True
    overlap = len(pantry_tokens & recipe_tokens)
    if overlap and overlap == min(len(pantry_tokens), len(recipe_tokens)):
        return True
    return SequenceMatcher(None, pantry_item, recipe_item).ratio() >= 0.82


def _goal_bonus(actual: float | None, target: float | None, prefer_lower: bool) -> tuple[bool | None, float]:
    if target is None or actual is None:
        return None, 0.0
    if prefer_lower:
        ok = actual <= target
        if ok:
            return ok, 10.0
        return ok, max(-28.0, -((actual - target) / 20.0))
    ok = actual >= target
    if ok:
        return ok, 12.0 + min(8.0, (actual - target) / 12.0)
    return ok, max(-35.0, -((target - actual) / 1.5))


def score_recipe(
    recipe: Recipe,
    pantry: list[str],
    max_calories: float | None = None,
    min_protein: float | None = None,
    max_sodium: float | None = None,
    category: str | None = None,
    strict: bool = False,
) -> dict | None:
    if recipe.calories is None or recipe.protein is None:
        return None

    pantry = [item for item in pantry if item]
    matches: list[str] = []
    matched_pantry: list[str] = []
    for pantry_item in pantry:
        for ingredient in recipe.ingredient_index:
            if _ingredients_match(pantry_item, ingredient):
                matches.append(ingredient)
                matched_pantry.append(pantry_item)
                break

    matched_set = sorted(set(matches))
    missing = sorted(set(recipe.ingredient_index) - set(matched_set))
    coverage = len(matched_set) / len(recipe.ingredient_index)
    useful_matches = [item for item in matched_set if item not in GENERIC_INGREDIENTS]
    useful_missing = [item for item in missing if item not in GENERIC_INGREDIENTS]

    if category:
        category_blob = " ".join(recipe.categories).lower()
        if category.lower() not in category_blob:
            return None

    calorie_ok, calorie_score = _goal_bonus(recipe.calories, max_calories, prefer_lower=True)
    protein_ok, protein_score = _goal_bonus(recipe.protein, min_protein, prefer_lower=False)
    sodium_ok, sodium_score = _goal_bonus(recipe.sodium, max_sodium, prefer_lower=True)

    if strict:
        strict_checks = [check for check in (calorie_ok, protein_ok, sodium_ok) if check is not None]
        if any(check is False for check in strict_checks):
            return None

    rating_score = (recipe.rating or 0.0) * 1.5
    score = (
        len(useful_matches) * 14.0
        + coverage * 32.0
        + calorie_score
        + protein_score
        + sodium_score
        + rating_score
    )

    if min_protein is not None and recipe.protein is not None:
        score += min(recipe.protein / 6.0, 10.0)

    category_blob = " ".join(recipe.categories).lower()
    if any(label in category_blob for label in ("condiment", "spread", "sauce", "drink", "cocktail")):
        score -= 18.0

    if not useful_matches and pantry:
        score -= 20.0

    why = []
    if useful_matches:
        why.append(f"{len(useful_matches)} pantry matches")
    if calorie_ok is True:
        why.append("within calorie target")
    if protein_ok is True:
        why.append("meets protein target")
    if sodium_ok is True:
        why.append("within sodium target")
    if recipe.rating:
        why.append(f"rated {recipe.rating:.1f}/5")

    return {
        "title": recipe.title,
        "score": round(score, 2),
        "coverage": coverage,
        "matched_count": len(useful_matches),
        "total_ingredients": len(recipe.ingredient_index),
        "matched": useful_matches,
        "matched_pantry": sorted(
            {item for item in matched_pantry if item not in GENERIC_INGREDIENTS}
        ),
        "missing": useful_missing or missing,
        "calories": recipe.calories,
        "protein": recipe.protein,
        "fat": recipe.fat,
        "sodium": recipe.sodium,
        "rating": recipe.rating,
        "categories": recipe.categories[:6],
        "ingredients": recipe.ingredients,
        "directions": recipe.directions,
        "calorie_ok": calorie_ok,
        "protein_ok": protein_ok,
        "sodium_ok": sodium_ok,
        "why": why,
    }


def recommend_recipes(
    recipes: list[Recipe],
    pantry: list[str],
    max_calories: float | None = None,
    min_protein: float | None = None,
    max_sodium: float | None = None,
    category: str | None = None,
    strict: bool = False,
    limit: int = 5,
) -> list[dict]:
    results = []
    pantry_terms = {
        token
        for item in pantry
        if item not in GENERIC_INGREDIENTS
        for token in item.split()
        if token not in GENERIC_INGREDIENTS
    }
    candidate_indexes = set()
    if pantry_terms and _TOKEN_INDEX is not None:
        for token in pantry_terms:
            candidate_indexes.update(_TOKEN_INDEX.get(token, []))
    if candidate_indexes and len(pantry_terms) >= 3:
        overlap_pairs = [
            (index, len(pantry_terms & recipes[index].search_terms))
            for index in candidate_indexes
        ]
        filtered_indexes = [index for index, overlap in overlap_pairs if overlap >= 2]
        if filtered_indexes:
            candidate_indexes = set(filtered_indexes)
    recipe_iterable = [recipes[index] for index in sorted(candidate_indexes)] if candidate_indexes else recipes
    for recipe in recipe_iterable:
        if pantry_terms and not (pantry_terms & recipe.search_terms):
            continue
        scored = score_recipe(
            recipe,
            pantry,
            max_calories=max_calories,
            min_protein=min_protein,
            max_sodium=max_sodium,
            category=category,
            strict=strict,
        )
        if scored is None:
            continue
        if pantry and scored["matched_count"] == 0:
            continue
        results.append(scored)
    results.sort(
        key=lambda item: (
            item["score"],
            item["matched_count"],
            item["coverage"],
            item["protein"] if item["protein"] is not None else -1,
            item["rating"] if item["rating"] is not None else -1,
        ),
        reverse=True,
    )
    deduped = []
    seen_titles = set()
    for result in results:
        title_key = result["title"].strip().lower()
        if title_key in seen_titles:
            continue
        deduped.append(result)
        seen_titles.add(title_key)
        if len(deduped) >= limit:
            break
    return deduped


def format_metric(value: float | None, unit: str) -> str:
    if value is None:
        return "N/A"
    return f"{value:.0f} {unit}"


def pantry_insights(results: list[dict]) -> dict:
    missing_counter: Counter[str] = Counter()
    for result in results:
        missing_counter.update(result["missing"][:5])
    return {
        "common_missing": missing_counter.most_common(5),
    }


def shopping_list_for_recipe(result: dict) -> list[str]:
    return result["missing"]


def nutrition_summary(result: dict) -> str:
    parts = [format_metric(result.get(key), unit) for key, unit in NUTRITION_LABELS]
    return " | ".join(parts)


def get_watch_macro_config(name: str | None):
    if not name:
        return None
    return WATCHABLE_MACROS.get(name.strip().lower())
