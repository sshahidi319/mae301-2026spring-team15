
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).with_name("full_format_recipes.json")
PANTRY_PATH = Path(__file__).with_name("pantry.json")
PROFILE_PATH = Path(__file__).with_name("profile.json")
TRACKER_HISTORY_PATH = Path(__file__).with_name("tracker_history.json")

SERVING_STEP = 0.25
MAX_RECOMMENDED_SERVINGS = 4.0

# -----------------------------
# Ingredient normalization
# -----------------------------

ALIASES: dict[str, str] = {
    # proteins
    "chicken breast": "chicken",
    "chicken breasts": "chicken",
    "chicken breast halves": "chicken",
    "boneless chicken breast halves": "chicken",
    "boneless skinless chicken breast": "chicken",
    "boneless skinless chicken breasts": "chicken",
    "boneless skinless chicken breast halves": "chicken",
    "skinless boneless chicken breast halves": "chicken",
    "skinless, boneless chicken breast halves": "chicken",
    "chicken thigh": "chicken",
    "chicken thighs": "chicken",
    "cooked chicken": "chicken",
    "diced chicken": "chicken",
    "cut-up chicken": "chicken",
    "chicken breast ; cooked cut-up": "chicken",
    "tri-tip steak": "beef",
    "ground beef": "ground beef",
    "lean ground beef": "ground beef",
    "ground sirloin": "ground beef",
    "ham steak": "ham",
    "italian sausage": "sausage",
    "italian sausage links": "sausage",
    "andouille sausage": "sausage",
    "sausage links": "sausage",
    "salmon fillet": "salmon",
    "salmon fillets": "salmon",
    "pink salmon": "salmon",
    "shrimp": "shrimp",
    "large peeled and deveined shrimp": "shrimp",
    "tuna fish": "tuna",
    # eggs / dairy
    "egg": "eggs",
    "whole egg": "eggs",
    "whole eggs": "eggs",
    "egg white": "egg whites",
    "egg whites": "egg whites",
    "milk": "milk",
    "whole milk": "milk",
    "buttermilk": "milk",
    "evaporated milk": "milk",
    "greek yogurt": "yogurt",
    "whole milk greek yogurt": "yogurt",
    "whole milk yogurt": "yogurt",
    "plain yogurt": "yogurt",
    "vanilla yogurt": "yogurt",
    "cheddar": "cheddar cheese",
    "sharp cheddar cheese": "cheddar cheese",
    "grated cheddar": "cheddar cheese",
    "swiss cheese": "swiss cheese",
    "pepper jack": "pepper jack cheese",
    "pepper jack cheese": "pepper jack cheese",
    "mozzarella": "mozzarella cheese",
    "parmesan": "parmesan cheese",
    "grated parmesan cheese": "parmesan cheese",
    "ricotta": "ricotta cheese",
    "cottage cheese": "cottage cheese",
    "cream cheese": "cream cheese",
    "sour cream": "sour cream",
    # vegetables
    "red onion": "onion",
    "yellow onion": "onion",
    "white onion": "onion",
    "sweet onion": "onion",
    "yellow onions": "onion",
    "white onions": "onion",
    "red onions": "onion",
    "thinly sliced yellow onions": "onion",
    "thinly sliced onions": "onion",
    "onions": "onion",
    "green pepper": "bell pepper",
    "red pepper": "bell pepper",
    "yellow pepper": "bell pepper",
    "orange pepper": "bell pepper",
    "green bell pepper": "bell pepper",
    "red bell pepper": "bell pepper",
    "yellow bell pepper": "bell pepper",
    "bell peppers": "bell pepper",
    "carrots": "carrot",
    "chopped carrot": "carrot",
    "chopped carrots": "carrot",
    "celery stalk": "celery",
    "chopped celery": "celery",
    "zucchinis": "zucchini",
    "curly green kale": "kale",
    "frozen chopped spinach": "spinach",
    "chopped spinach": "spinach",
    "petite diced tomatoes": "tomatoes",
    "roma tomatoes": "tomatoes",
    "plum tomato": "tomatoes",
    "plum tomatoes": "tomatoes",
    "diced tomatoes": "tomatoes",
    "crushed tomatoes": "tomatoes",
    "cauliflower rice": "cauliflower rice",
    'cauliflower "rice"': "cauliflower rice",
    'cauliflower "pearls"': "cauliflower rice",
    "green chilies": "green chiles",
    "green chilies chopped": "green chiles",
    "green chilis": "green chiles",
    "jalapeño": "jalapeno",
    "jalapeno peppers": "jalapeno",
    "scallion": "scallions",
    "green onions": "scallions",
    "spring onions": "scallions",
    "boston lettuce leaves": "lettuce",
    "fresh parsley": "parsley",
    "italian parsley": "parsley",
    "flat leaf parsley": "parsley",
    "flat-leaf parsley": "parsley",
    "fresh parsley leaves": "parsley",
    "cilantro leaves": "cilantro",
    "cilantro leaves and tender stems": "cilantro",
    # pantry / carbs
    "all purpose flour": "flour",
    "all-purpose flour": "flour",
    "cake flour": "flour",
    "whole wheat bread": "bread",
    "french baguette": "bread",
    "baguettes": "bread",
    "bread crumbs": "breadcrumbs",
    "bread crumb": "breadcrumbs",
    "dry bread crumbs": "breadcrumbs",
    "panko bread crumbs": "breadcrumbs",
    "panko breadcrumbs": "breadcrumbs",
    "panko": "breadcrumbs",
    "macaroni pasta": "macaroni",
    "penne noodles": "penne pasta",
    "spaghetti noodles": "spaghetti",
    "lasagna noodle": "lasagna noodles",
    "egg noodles": "egg noodles",
    # condiments / sauces / spices
    "kosher salt": "salt",
    "coarse salt": "salt",
    "maldon salt": "salt",
    "sea salt": "salt",
    "table salt": "salt",
    "freshly cracked black pepper": "black pepper",
    "freshly ground black pepper": "black pepper",
    "ground black pepper": "black pepper",
    "ground cumin": "cumin",
    "dried oregano": "oregano",
    "smoked paprika": "paprika",
    "hungarian paprika": "paprika",
    "aleppo pepper": "aleppo pepper",
    "herbe de provence": "herbes de provence",
    "herbes de provence": "herbes de provence",
    "cajun seasoning": "cajun seasoning",
    "granulated garlic": "garlic powder",
    "worcestershire": "worcestershire sauce",
    "worcestershire sauce": "worcestershire sauce",
    "soy sauce": "soy sauce",
    "prepared brown mustard": "mustard",
    "mustard powder": "mustard",
    "apple cider vinegar": "vinegar",
    "rice vinegar": "vinegar",
    "red wine vinegar": "vinegar",
    "lemon juice": "lemon juice",
    "fresh lemon juice": "lemon juice",
    "olive oil": "olive oil",
    "extra virgin olive oil": "olive oil",
    "vegetable oil": "oil",
    "canola oil": "oil",
    "peanut or canola oil": "oil",
    "neutral oil": "oil",
    "coconut oil": "coconut oil",
    "chicken broth": "broth",
    "beef broth": "broth",
    "vegetable broth": "broth",
    "ready-to-serve beef broth": "broth",
    "chicken stock": "broth",
    "beef stock": "broth",
    "vegetable stock": "broth",
    "red wine": "red wine",
    # misc
    "button mushroom": "mushrooms",
    "button mushrooms": "mushrooms",
    "fresh mushrooms": "mushrooms",
    "olives": "olives",
}

# Words that are almost always prep descriptors or non-essential modifiers.
STOPWORDS = {
    "a", "an", "and", "or", "for", "with", "to", "of", "in", "on",
    "fresh", "dried", "dry", "extra", "virgin", "boneless", "skinless",
    "large", "small", "medium", "plain", "lean", "optional", "taste",
    "ground", "chopped", "diced", "sliced", "minced", "crushed",
    "shredded", "grated", "peeled", "seeded", "cooked", "uncooked",
    "frozen", "thawed", "packed", "divided", "warm", "cold", "hot",
    "softened", "melted", "beaten", "rinsed", "drained", "cubed", "cut",
    "thinly", "thickly", "coarsely", "finely", "needed", "serving", "serve",
    "garnish", "freshly", "about", "approximately", "plus", "into", "from",
    "split", "separate", "julienned", "patted", "preferably", "such", "as",
    "stemmed", "seedless", "undrained", "rind", "zest", "preferred", "dry",
    "whole", "one", "half", "quarter", "piece", "pieces", "bite-size",
}

NAME_STRIP_TOKENS = STOPWORDS | {
    "cup", "cups", "c", "c.",
    "tablespoon", "tablespoons", "tbsp", "tbsp.",
    "teaspoon", "teaspoons", "tsp", "tsp.",
    "ounce", "ounces", "oz", "oz.",
    "fluid", "fl", "pound", "pounds", "lb", "lb.", "lbs", "lbs.",
    "gram", "grams", "g", "kg", "ml", "l", "liter", "liters",
    "gallon", "gallons", "quart", "quarts", "pint", "pints",
    "pinch", "dash", "clove", "cloves", "slice", "slices",
    "can", "cans", "package", "packages", "pkg", "bag", "bags",
    "jar", "jars", "bottle", "bottles", "bunch", "bunches",
    "stalk", "stalks", "sprig", "sprigs", "head", "heads",
    "stick", "sticks", "leaf", "leaves", "link", "links",
    "breast", "breasts", "fillet", "fillets", "<unit>",
}

GENERIC_INGREDIENTS = {
    "salt", "black pepper", "pepper", "water", "oil", "olive oil", "butter", "flour", "sugar"
}

WEIGHT_TO_G = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "lbs": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
}

VOLUME_TO_ML = {
    "tsp": 4.92892,
    "teaspoon": 4.92892,
    "teaspoons": 4.92892,
    "tbsp": 14.7868,
    "tablespoon": 14.7868,
    "tablespoons": 14.7868,
    "cup": 236.588,
    "cups": 236.588,
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
    "quart": 946.353,
    "quarts": 946.353,
    "pint": 473.176,
    "pints": 473.176,
    "fl oz": 29.5735,
    "fluid ounce": 29.5735,
    "fluid ounces": 29.5735,
}

COUNT_UNITS = {
    "count", "egg", "eggs", "onion", "onions", "pepper", "peppers",
    "banana", "bananas", "clove", "cloves", "fillet", "fillets", "filets",
    "breast", "breasts", "slice", "slices", "serving", "bunch",
    "bunches", "stem", "stems", "stalk", "stalks", "leaf", "leaves",
    "link", "links", "can", "cans", "package", "packages", "pkg",
    "bag", "bags", "head", "heads", "piece", "pieces",
}

DEFAULT_BARE_NUMBER_UNITS: dict[str, str] = {
    "salt": "tsp",
    "black pepper": "tsp",
    "pepper": "tsp",
    "paprika": "tsp",
    "aleppo pepper": "tsp",
    "cumin": "tsp",
    "oregano": "tsp",
    "herbes de provence": "tsp",
    "cajun seasoning": "tsp",
    "garlic powder": "tsp",
    "onion powder": "tsp",
    "parsley": "tbsp",
    "cilantro": "cups",
    "olive oil": "tbsp",
    "oil": "tbsp",
    "coconut oil": "tbsp",
    "butter": "tbsp",
    "worcestershire sauce": "tbsp",
    "soy sauce": "tbsp",
    "mustard": "tbsp",
    "vinegar": "cups",
    "lemon juice": "tbsp",
    "milk": "cups",
    "water": "cups",
    "broth": "cups",
    "red wine": "cups",
    "yogurt": "cups",
    "spinach": "cups",
    "mushrooms": "cups",
    "breadcrumbs": "cups",
    "cauliflower rice": "cups",
    "onion": "count",
    "bell pepper": "count",
    "carrot": "count",
    "celery": "count",
    "zucchini": "count",
    "kale": "count",
    "eggs": "count",
    "egg whites": "count",
    "green chiles": "count",
    "chicken": "cups",
    "ground beef": "pound",
    "beef": "pound",
    "sausage": "count",
    "cheddar cheese": "oz",
    "swiss cheese": "oz",
    "pepper jack cheese": "oz",
    "mozzarella cheese": "oz",
    "parmesan cheese": "oz",
}

INGREDIENT_CONVERSIONS: dict[str, dict[str, Any]] = {
    # spices / seasonings
    "salt": {"category": "dry", "tsp_to_g": 6.0, "tbsp_to_g": 18.0},
    "black pepper": {"category": "dry", "tsp_to_g": 2.3, "tbsp_to_g": 6.9},
    "paprika": {"category": "dry", "tsp_to_g": 2.3, "tbsp_to_g": 6.9},
    "aleppo pepper": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "cumin": {"category": "dry", "tsp_to_g": 2.1, "tbsp_to_g": 6.3},
    "oregano": {"category": "dry", "tsp_to_g": 1.0, "tbsp_to_g": 3.0},
    "herbes de provence": {"category": "dry", "tsp_to_g": 1.0, "tbsp_to_g": 3.0},
    "cajun seasoning": {"category": "dry", "tsp_to_g": 2.2, "tbsp_to_g": 6.6},
    "garlic powder": {"category": "dry", "tsp_to_g": 3.1, "tbsp_to_g": 9.3},
    "onion powder": {"category": "dry", "tsp_to_g": 2.4, "tbsp_to_g": 7.2},
    "parsley": {"category": "dry", "cup_to_g": 16.0, "tbsp_to_g": 1.9, "tsp_to_g": 0.6},
    "cilantro": {"category": "dry", "cup_to_g": 16.0},
    # liquids
    "olive oil": {"category": "liquid", "tbsp_to_ml": 14.8, "tsp_to_ml": 4.9, "cup_to_ml": 236.6},
    "oil": {"category": "liquid", "tbsp_to_ml": 14.8, "tsp_to_ml": 4.9, "cup_to_ml": 236.6},
    "coconut oil": {"category": "liquid", "tbsp_to_ml": 14.8, "tsp_to_ml": 4.9, "cup_to_ml": 236.6},
    "worcestershire sauce": {"category": "liquid", "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0, "cup_to_ml": 240.0},
    "soy sauce": {"category": "liquid", "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0, "cup_to_ml": 240.0},
    "vinegar": {"category": "liquid", "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0, "cup_to_ml": 240.0},
    "lemon juice": {"category": "liquid", "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0, "cup_to_ml": 240.0},
    "milk": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "water": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "broth": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "red wine": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    # dairy / pantry
    "butter": {"category": "dry", "tbsp_to_g": 14.2, "tsp_to_g": 4.7, "cup_to_g": 227.0},
    "yogurt": {"category": "dry", "cup_to_g": 245.0, "tbsp_to_g": 15.3},
    "cheddar cheese": {"category": "dry", "cup_to_g": 113.0},
    "swiss cheese": {"category": "dry", "cup_to_g": 113.0},
    "pepper jack cheese": {"category": "dry", "cup_to_g": 113.0},
    "mozzarella cheese": {"category": "dry", "cup_to_g": 113.0},
    "parmesan cheese": {"category": "dry", "cup_to_g": 100.0},
    "breadcrumbs": {"category": "dry", "cup_to_g": 110.0, "tbsp_to_g": 6.9},
    "flour": {"category": "dry", "cup_to_g": 120.0, "tbsp_to_g": 7.5, "tsp_to_g": 2.5},
    "sugar": {"category": "dry", "cup_to_g": 200.0, "tbsp_to_g": 12.5, "tsp_to_g": 4.2},
    "brown sugar": {"category": "dry", "cup_to_g": 220.0, "tbsp_to_g": 13.8, "tsp_to_g": 4.6},
    "pasta": {"category": "dry", "cup_to_g": 100.0},
    "macaroni": {"category": "dry", "cup_to_g": 100.0},
    "penne pasta": {"category": "dry", "cup_to_g": 100.0},
    "spaghetti": {"category": "dry", "cup_to_g": 100.0},
    "lasagna noodles": {"category": "count"},
    "egg noodles": {"category": "dry", "cup_to_g": 100.0},
    # vegetables / produce
    "onion": {"category": "count", "cup_to_g": 160.0, "count_to_g": 110.0},
    "bell pepper": {"category": "count", "cup_to_g": 149.0, "count_to_g": 120.0},
    "carrot": {"category": "count", "cup_to_g": 128.0, "count_to_g": 61.0},
    "celery": {"category": "count", "cup_to_g": 100.0, "count_to_g": 40.0, "stalk_to_g": 40.0},
    "zucchini": {"category": "count", "count_to_g": 196.0},
    "kale": {"category": "count", "leaf_to_g": 15.0, "count_to_g": 15.0},
    "spinach": {"category": "dry", "cup_to_g": 30.0, "package_to_g": 283.495},
    "mushrooms": {"category": "dry", "cup_to_g": 70.0},
    "scallions": {"category": "dry", "cup_to_g": 100.0},
    "green chiles": {"category": "count"},
    "cauliflower rice": {"category": "dry", "cup_to_g": 107.0},
    "tomatoes": {"category": "count", "count_to_g": 123.0, "cup_to_g": 180.0},
    "lettuce": {"category": "dry", "cup_to_g": 50.0},
    # proteins
    "eggs": {"category": "count", "count_to_g": 50.0},
    "egg whites": {"category": "count", "count_to_g": 33.0},
    "chicken": {"category": "dry", "cup_to_g": 140.0, "count_to_g": 174.0},
    "beef": {"category": "dry", "cup_to_g": 150.0},
    "ground beef": {"category": "dry", "cup_to_g": 150.0},
    "sausage": {"category": "count", "count_to_g": 75.0},
    "ham": {"category": "dry", "cup_to_g": 140.0},
    "shrimp": {"category": "dry", "cup_to_g": 145.0},
    "salmon": {"category": "dry"},
    "tuna": {"category": "dry", "cup_to_g": 150.0},
}
# --- parser patch pack: aliases / units / conversions ---

ALIASES.update({
    # spices / seasonings
    "sea salt": "salt",
    "freshly ground pepper": "black pepper",
    "cracked black pepper": "black pepper",
    "cumin seeds": "cumin",
    "dried oregano": "oregano",
    "ground mustard": "mustard",
    "mustard powder": "mustard",
    "ground ginger": "ginger",
    "fresh ginger": "ginger",
    "fresh ginger minced": "ginger",
    "garlic powder": "garlic powder",
    "cinnamon": "cinnamon",
    "ground allspice": "allspice",
    "cayenne": "cayenne",
    "red pepper flakes": "red pepper flakes",
    "italian seasoning": "italian seasoning",
    "fresh cilantro": "cilantro",
    "bay leaves": "bay leaf",
    "bay leaf": "bay leaf",
    "marjoram": "marjoram",

    # oils / sauces
    "extra virgin olive oil": "olive oil",
    "extra-virgin olive oil": "olive oil",
    "clarified butter": "butter",
    "vegetable oil": "oil",
    "orange juice": "orange juice",
    "tomato juice": "tomato juice",
    "beer": "beer",
    "tomato paste": "tomato paste",

    # branded / product names
    "zatarains creole mustard": "mustard",
    "zatarains creole seasoning": "cajun seasoning",
    "mccormick garlic minced": "garlic",
    "mccormick parsley flakes": "parsley",
    "gold medal all purpose flour": "flour",
    "gold medal all-purpose flour": "flour",
    "progresso plain bread crumbs": "breadcrumbs",
    "progresso plain breadcrumbs": "breadcrumbs",
    "parmigiano reggiano": "parmesan cheese",
    "parmigiano reggiano pdo": "parmesan cheese",
    "parmesean cheese": "parmesan cheese",
    "grated cheese": "cheddar cheese",
    "cheese blend": "mozzarella cheese",
    "prosciutto di parma pdo": "ham",
    "traditional balsamic vinegar of modena pdo": "vinegar",
    "cilento pdo extra virgin olive oil": "olive oil",

    # produce / pantry
    "jalapeños": "jalapeno",
    "jalapeno chiles": "jalapeno",
    "jalapeno chile": "jalapeno",
    "jalapeno, diced": "jalapeno",
    "avocado, pitted and sliced": "avocado",
    "avocado pitted and sliced": "avocado",
    "garlic cloves": "garlic",
    "garlic clove": "garlic",
    "shallot": "onion",
    "shallots": "onion",
    "sweet onion": "onion",
    "portabella mushrooms": "mushrooms",
    "portobello mushrooms": "mushrooms",
    "grape tomatoes": "tomatoes",
    "stewed tomatoes": "tomatoes",
    "crushed tomatoes": "tomatoes",
    "diced tomatoes": "tomatoes",
    "petite diced tomatoes": "tomatoes",
    "tomatillos": "tomatillo",
    "artichokes": "artichoke",
    "artichoke": "artichoke",
    "cauliflower": "cauliflower",
    "cauliflower rice": "cauliflower rice",
    "instant rice": "rice",
    "rice": "rice",
    "white kidney beans": "beans",
    "chickpeas": "chickpeas",

    # meats
    "ground turkey breast": "ground turkey",
    "extra lean ground turkey breast": "ground turkey",
    "ground chicken": "ground chicken",
    "lean ground chicken": "ground chicken",
    "turkey breast": "turkey",
    "bone-in whole turkey breast": "turkey",
    "bone in whole turkey breast": "turkey",
})

COUNT_UNITS |= {
    "bunch", "bunches",
    "box", "boxes",
    "pkg", "pkgs",
    "grind", "grinds",
}

DEFAULT_BARE_NUMBER_UNITS.update({
    "mustard": "tsp",
    "ginger": "tsp",
    "cinnamon": "tsp",
    "allspice": "tsp",
    "cayenne": "tsp",
    "red pepper flakes": "tsp",
    "italian seasoning": "tsp",
    "thyme": "tsp",
    "marjoram": "tsp",
    "bay leaf": "count",

    "orange juice": "cups",
    "tomato juice": "cups",
    "beer": "cups",
    "tomato paste": "tbsp",

    "rice": "cups",
    "mushrooms": "cups",
    "cauliflower": "cups",
    "tomatillo": "count",
    "jalapeno": "count",
    "avocado": "count",
    "garlic": "count",

    "ground turkey": "pound",
    "ground chicken": "pound",
    "turkey": "pound",
    "parmesan cheese": "oz",
})

INGREDIENT_CONVERSIONS.update({
    "mustard": {"category": "dry", "tsp_to_g": 2.2, "tbsp_to_g": 6.6},
    "ginger": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "cinnamon": {"category": "dry", "tsp_to_g": 2.6, "tbsp_to_g": 7.8},
    "allspice": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "cayenne": {"category": "dry", "tsp_to_g": 1.8, "tbsp_to_g": 5.4},
    "red pepper flakes": {"category": "dry", "tsp_to_g": 1.8, "tbsp_to_g": 5.4},
    "italian seasoning": {"category": "dry", "tsp_to_g": 1.0, "tbsp_to_g": 3.0},
    "thyme": {"category": "dry", "tsp_to_g": 1.0, "tbsp_to_g": 3.0},
    "marjoram": {"category": "dry", "tsp_to_g": 0.5, "tbsp_to_g": 1.5},
    "chili powder": {"category": "dry", "tsp_to_g": 2.7, "tbsp_to_g": 8.1},
    "bay leaf": {"category": "count", "count_to_g": 0.5},

    "orange juice": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "tomato juice": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "beer": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "tomato paste": {"category": "dry", "tbsp_to_g": 16.0, "tsp_to_g": 5.3},

    "rice": {"category": "dry", "cup_to_g": 185.0},
    "mushrooms": {"category": "dry", "cup_to_g": 70.0},
    "cauliflower": {"category": "dry", "cup_to_g": 100.0},
    "tomatillo": {"category": "count", "count_to_g": 34.0},
    "jalapeno": {"category": "count", "count_to_g": 14.0},
    "avocado": {"category": "count", "count_to_g": 150.0},
    "garlic": {"category": "count", "count_to_g": 5.0},
    "artichoke": {"category": "count", "count_to_g": 100.0},

    "parmesan cheese": {"category": "dry", "cup_to_g": 100.0},
    "ground turkey": {"category": "dry", "cup_to_g": 150.0},
    "ground chicken": {"category": "dry", "cup_to_g": 150.0},
    "turkey": {"category": "dry", "cup_to_g": 140.0},
})
WATCHABLE_MACROS = {
    "fat": ("fat", "Max fat (grams)", "g fat", True),
    "sodium": ("sodium", "Max sodium (mg)", "mg sodium", True),
}

NUTRITION_LABELS = (
    ("calories", "kcal"),
    ("protein", "g protein"),
    ("carbs", "g carbs"),
    ("fat", "g fat"),
    ("sodium", "mg sodium"),
)

UNICODE_FRACTIONS = {
    "½": " 1/2 ",
    "¼": " 1/4 ",
    "¾": " 3/4 ",
    "⅓": " 1/3 ",
    "⅔": " 2/3 ",
    "⅛": " 1/8 ",
    "⅜": " 3/8 ",
    "⅝": " 5/8 ",
    "⅞": " 7/8 ",
}

TEXT_NUMBER_REPLACEMENTS = [
    (r"^half of one\b", "1/2"),
    (r"^one half of one\b", "1/2"),
    (r"^one quarter of one\b", "1/4"),
    (r"^quarter of one\b", "1/4"),
]

SKIP_LINE_PATTERNS = {
    "salt and pepper",
    "salt and pepper to taste",
    "pepper and salt to taste",
    "fresh ground salt and pepper to taste",
    "kosher salt and freshly ground black or white pepper",
    "salt and freshly ground black pepper",
    "salt and freshly ground black or white pepper",
    "coconut oil to grease muffin tin",
}

_RECIPE_CACHE: list["Recipe"] | None = None


@dataclass
class Recipe:
    title: str
    url: str
    ingredients: list[str]
    directions: list[str]
    categories: list[str]
    calories: float | None
    protein: float | None
    carbs: float | None
    fat: float | None
    sodium: float | None
    rating: float | None
    ingredient_index: list[str]


def _clean_text(text: str) -> str:
    text = str(text).lower()
    text = text.replace("&", " and ")
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9\s\/\.\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_item(text: str) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""

    cleaned = ALIASES.get(cleaned, cleaned)

    tokens: list[str] = []
    for token in cleaned.split():
        if token in NAME_STRIP_TOKENS:
            continue
        # numeric tokens
        if token.replace(".", "", 1).isdigit():
            continue
        if "/" in token:
            try:
                Fraction(token)
                continue
            except Exception:
                pass
        tokens.append(token)

    if not tokens:
        return ""

    normalized = " ".join(tokens[:5]).strip()
    return ALIASES.get(normalized, normalized)


def _coerce_number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if math.isnan(float(value)):
            return None
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except Exception:
            return None
    return None


def load_recipes(path: Path = DATA_PATH) -> list[Recipe]:
    global _RECIPE_CACHE
    if path == DATA_PATH and _RECIPE_CACHE is not None:
        return _RECIPE_CACHE

    raw = json.loads(path.read_text())
    recipes: list[Recipe] = []

    for row in raw:
        title = str(row.get("title") or "").strip()
        url = str(row.get("url") or "").strip()
        ingredients = [str(x).strip() for x in row.get("ingredients") or [] if str(x).strip()]
        directions = [str(x).strip() for x in row.get("directions") or [] if str(x).strip()]
        categories = [str(x).strip() for x in row.get("categories") or [] if str(x).strip()]
        if not title or not ingredients:
            continue

        normalized_ingredients: list[str] = []
        for ingredient_line in ingredients:
            item = extract_named_ingredient(ingredient_line)
            if item:
                normalized_ingredients.append(item)

        if not normalized_ingredients:
            continue

        recipes.append(
            Recipe(
                title=title,
                url=url,
                ingredients=ingredients,
                directions=directions or ["Directions unavailable in this dataset."],
                categories=categories,
                calories=_coerce_number(row.get("calories")),
                protein=_coerce_number(row.get("protein")),
                carbs=_coerce_number(row.get("carbs")),
                fat=_coerce_number(row.get("fat")),
                sodium=_coerce_number(row.get("sodium")),
                rating=_coerce_number(row.get("rating")),
                ingredient_index=sorted(set(normalized_ingredients)),
            )
        )

    if path == DATA_PATH:
        _RECIPE_CACHE = recipes
    return recipes


# -----------------------------
# Profiles / history
# -----------------------------

def _default_profile() -> dict[str, Any]:
    return {
        "name": "",
        "weight": None,
        "weight_unit": "lb",
        "height_inches": None,
        "goal": "maintain",
        "protein_target": None,
    }


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    default = _default_profile()
    if not path.exists():
        return default
    try:
        data = json.loads(path.read_text())
    except Exception:
        return default
    if isinstance(data, dict):
        default.update(data)
    return default


def save_profile(profile: dict[str, Any], path: Path = PROFILE_PATH) -> None:
    path.write_text(json.dumps(profile, indent=2))


def estimate_protein_target(weight: float | None, weight_unit: str = "lb", goal: str = "maintain") -> float | None:
    if weight is None or weight <= 0:
        return None
    weight_lb = weight * 2.20462 if weight_unit.lower() == "kg" else weight
    multiplier = {"cut": 0.8, "maintain": 0.9, "build muscle": 1.0}.get(goal.lower(), 0.9)
    return round(weight_lb * multiplier)


def profile_summary(profile: dict[str, Any]) -> str:
    protein_target = profile.get("protein_target")
    target_text = f"{int(protein_target)} g/day" if protein_target else "not set"
    return (
        f"Goal: {profile.get('goal', 'maintain')} | "
        f"Weight: {profile.get('weight', 'not set')} {profile.get('weight_unit', 'lb')} | "
        f"Height: {profile.get('height_inches', 'not set')} in | "
        f"Protein target: {target_text}"
    )


def load_tracker_history(path: Path = TRACKER_HISTORY_PATH) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, list[dict[str, Any]]] = {}
    for day, entries in data.items():
        if isinstance(entries, list):
            cleaned = []
            for entry in entries:
                if isinstance(entry, dict):
                    cleaned.append(
                        {
                            "title": str(entry.get("title", "")).strip(),
                            "calories": _coerce_number(entry.get("calories")),
                            "protein": _coerce_number(entry.get("protein")),
                            "servings": _coerce_number(entry.get("servings")),
                            "timestamp": str(entry.get("timestamp", "")),
                        }
                    )
            out[day] = cleaned
    return out


def save_tracker_history(history: dict[str, list[dict[str, Any]]], path: Path = TRACKER_HISTORY_PATH) -> None:
    path.write_text(json.dumps(history, indent=2))


def add_tracker_entry(
    history: dict[str, list[dict[str, Any]]],
    title: str,
    calories: float | None,
    protein: float | None,
    servings: float = 1.0,
    entry_date: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    day = entry_date or str(date.today())
    history.setdefault(day, []).append(
        {
            "title": title,
            "calories": calories,
            "protein": protein,
            "servings": servings,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
    )
    return history


def day_totals(history: dict[str, list[dict[str, Any]]], day: str | None = None) -> dict[str, Any]:
    target_day = day or str(date.today())
    entries = history.get(target_day, [])
    calories = sum(entry.get("calories") or 0 for entry in entries)
    protein = sum(entry.get("protein") or 0 for entry in entries)
    return {
        "date": target_day,
        "count": len(entries),
        "calories": round(calories),
        "protein": round(protein),
        "entries": entries,
    }


def month_totals(history: dict[str, list[dict[str, Any]]], year_month: str | None = None) -> dict[str, Any]:
    prefix = year_month or date.today().strftime("%Y-%m")
    matching_days = sorted(day for day in history if day.startswith(prefix))
    total_calories = 0.0
    total_protein = 0.0
    total_meals = 0
    active_days = 0
    for day in matching_days:
        entries = history.get(day, [])
        if entries:
            active_days += 1
        total_meals += len(entries)
        total_calories += sum(entry.get("calories") or 0 for entry in entries)
        total_protein += sum(entry.get("protein") or 0 for entry in entries)
    return {
        "month": prefix,
        "days_logged": active_days,
        "meals": total_meals,
        "calories": round(total_calories),
        "protein": round(total_protein),
        "avg_calories_per_logged_day": round(total_calories / active_days) if active_days else 0,
        "avg_protein_per_logged_day": round(total_protein / active_days) if active_days else 0,
    }


# -----------------------------
# Pantry parsing
# -----------------------------

def _normalize_unit(unit: str) -> str:
    unit = _clean_text(unit).strip(" .,")

    unit_map = {
        "c": "cup", "c.": "cup", "cup": "cup", "cups": "cups",
        "tbsp": "tbsp", "tbsp.": "tbsp", "tablespoon": "tablespoon", "tablespoons": "tablespoons",
        "tablespon": "tablespoon", "tablespons": "tablespoons",
        "tbs": "tbsp", "tb": "tbsp", "t": "tbsp",
        "tsp": "tsp", "tsp.": "tsp", "teaspoon": "teaspoon", "teaspoons": "teaspoons",
        "teaspon": "teaspoon", "teaspons": "teaspoons",
        "oz": "oz", "oz.": "oz", "ounce": "ounce", "ounces": "ounces",
        "fl oz": "fl oz", "fluid ounce": "fluid ounce", "fluid ounces": "fluid ounces",
        "lb": "lb", "lb.": "lb", "lbs": "lbs", "lbs.": "lbs", "pound": "pound", "pounds": "pounds",
        "g": "g", "gram": "g", "grams": "g", "kg": "kg",
        "ml": "ml", "l": "l",
        "pkg": "package", "pkgs": "packages",
    }
    return unit_map.get(unit, unit)


def _parse_amount_token(token: str) -> float | None:
    token = token.strip()
    if not token:
        return None
    try:
        return float(token)
    except Exception:
        pass
    try:
        return float(Fraction(token))
    except Exception:
        return None


def _amount_to_float(text: str) -> float | None:
    text = text.strip()
    if not text:
        return None
    parts = text.split()
    if len(parts) == 2:
        a = _parse_amount_token(parts[0])
        b = _parse_amount_token(parts[1])
        if a is not None and b is not None:
            return a + b
    return _parse_amount_token(text)


def _format_amount(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    if value >= 10:
        return f"{value:.1f}"
    return f"{value:.3f}".rstrip("0").rstrip(".")


def preprocess_ingredient_line(line: str) -> str:
    text = str(line).strip()
    if not text:
        return ""

    text = re.sub(r"^\s*[\*\-•]+\s*", "", text)

    for old, new in UNICODE_FRACTIONS.items():
        text = text.replace(old, new)

    # normalize common hyphenated amounts like 14-1/2 or 15-oz.
    text = re.sub(r"(\d+)-(\d+/\d+)", r"\1 \2", text)
    text = re.sub(r"(\d+)-\s*(oz|ounce|ounces|lb|lbs|pound|pounds)\b", r"\1 \2", text, flags=re.I)

    text = text.replace(";", ",")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text).strip(" ,;")

    lower = text.lower().strip()
    if (
        lower in SKIP_LINE_PATTERNS
        or "salt and pepper" in lower
        or "both salt and pepper" in lower
        or lower.endswith("to taste")
        or lower.endswith("for deep frying")
        or lower.endswith("etc")
    ):
        return ""
    if lower.startswith("for the ") and lower.endswith(":"):
        return ""
    if lower.endswith(":"):
        return ""

    for marker in [
        ", i like using",
        " i like using",
        ", such as ",
        ", preferably ",
        "(optional)",
        " optional",
        ", divided",
        ", drained",
        ", rinsed",
        ", halved",
        ", chopped",
        ", sliced",
        ", diced",
        ", minced",
        ", roughly chopped",
        ", seeded",
        ", pitted and sliced",
        ", husks removed and rinsed",
        ", thawed if frozen",
        ", undrained",
    ]:
        idx = lower.find(marker)
        if idx != -1:
            text = text[:idx].strip(" ,")
            lower = text.lower()

    for pattern, repl in TEXT_NUMBER_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.I)

    text = re.sub(r"^\s*pinch(?:\s+of)?\s+", "1/8 teaspoon ", text, flags=re.I)
    text = re.sub(r"^\s*dash(?:\s+of)?\s+", "1/16 teaspoon ", text, flags=re.I)

    # 1 tbsp + 2 tsp olive oil  ->  5 tsp olive oil
    mix = re.match(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(tbsp|tablespoons?|tsp|teaspoons?)\s*\+\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(tbsp|tablespoons?|tsp|teaspoons?)\s+(.+)$",
        text,
        flags=re.I,
    )
    if mix:
        a1 = _amount_to_float(mix.group(1)) or 0
        u1 = _normalize_unit(mix.group(2))
        a2 = _amount_to_float(mix.group(3)) or 0
        u2 = _normalize_unit(mix.group(4))
        tail = mix.group(5).strip()

        total_tsp = 0.0
        total_tsp += a1 * (3 if u1 in {"tbsp", "tablespoon", "tablespoons"} else 1)
        total_tsp += a2 * (3 if u2 in {"tbsp", "tablespoon", "tablespoons"} else 1)

        text = f"{_format_amount(total_tsp)} tsp {tail}"

    # choose first value in a range like 4 to 5 leaf kale
    text = re.sub(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(?:to|-)\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\b",
        r"\1",
        text,
        flags=re.I,
    )

    # 1 6-lb turkey -> 6 lb turkey
    combo_weight = re.match(
        r"^(\d+)\s+(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(lb|lbs|pound|pounds)\s+(.+)$",
        text,
        flags=re.I,
    )
    if combo_weight:
        count_amt = _amount_to_float(combo_weight.group(1)) or 1
        weight_amt = _amount_to_float(combo_weight.group(2)) or 0
        unit = combo_weight.group(3)
        tail = combo_weight.group(4).strip()
        text = f"{_format_amount(count_amt * weight_amt)} {unit} {tail}"

    # 1 (32-ounce) box broth -> 32 ounce broth
    package_pattern = re.compile(
        r"""^
        (\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*
        \(\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*[- ]?
        (fluid ounce|fluid ounces|fl oz|ounce|ounces|oz)\s*\)\s*
        (?:can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|bottle|bottles|box|boxes)\s+
        (.+)$
        """,
        re.I | re.X,
    )
    m = package_pattern.match(text)
    if m:
        outer_amt = _amount_to_float(m.group(1))
        inner_amt = _amount_to_float(m.group(2))
        inner_unit = _normalize_unit(m.group(3))
        ingredient = m.group(4).strip(" ,")
        if outer_amt is not None and inner_amt is not None:
            total_amt = outer_amt * inner_amt
            text = f"{_format_amount(total_amt)} {inner_unit} {ingredient}"

    # package words without explicit size
    text = re.sub(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s+(can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|bottle|bottles|box|boxes)\s+",
        r"\1 count ",
        text,
        flags=re.I,
    )

    # keep first option only in OR chains
    text = re.split(r"\s+--or--\s+|\s+\bor\b\s+", text, maxsplit=1, flags=re.I)[0].strip(" ,")

    return text


def parse_quantity_text(text: str) -> tuple[float | None, str, str]:
    raw = preprocess_ingredient_line(text)
    if not raw:
        return None, "", ""

    tokens = raw.split()
    amount = None
    unit = ""
    remainder_start = 0

    if len(tokens) >= 2:
        first = _parse_amount_token(tokens[0])
        second = _parse_amount_token(tokens[1])
        if first is not None and second is not None:
            amount = first + second
            remainder_start = 2
        elif first is not None:
            amount = first
            remainder_start = 1

    if amount is None:
        return None, "", raw

    if len(tokens) > remainder_start:
        candidate_unit = _normalize_unit(tokens[remainder_start].strip(".,"))
        two_word_unit = ""
        if len(tokens) > remainder_start + 1:
            two_word_unit = _normalize_unit(
                tokens[remainder_start].strip(".,") + " " + tokens[remainder_start + 1].strip(".,")
            )

        if two_word_unit in VOLUME_TO_ML:
            unit = two_word_unit
            remainder_start += 2
        elif (
            candidate_unit in WEIGHT_TO_G
            or candidate_unit in VOLUME_TO_ML
            or candidate_unit in COUNT_UNITS
            or candidate_unit == "count"
        ):
            unit = candidate_unit
            remainder_start += 1

    remainder = " ".join(tokens[remainder_start:]).strip(" ,")
    return amount, unit, remainder


def _lookup_conversion(name: str) -> dict[str, Any]:
    if name in INGREDIENT_CONVERSIONS:
        return INGREDIENT_CONVERSIONS[name]
    return INGREDIENT_CONVERSIONS.get(ALIASES.get(name, ""), {})


def extract_named_ingredient(text: str) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""

    possible_keys = set(ALIASES.keys()) | set(INGREDIENT_CONVERSIONS.keys())
    matches = [key for key in possible_keys if key and key in cleaned]
    if matches:
        best = sorted(matches, key=len, reverse=True)[0]
        return ALIASES.get(best, best)
    return normalize_item(cleaned)


def infer_default_unit(name: str) -> str | None:
    if name in DEFAULT_BARE_NUMBER_UNITS:
        return DEFAULT_BARE_NUMBER_UNITS[name]
    if any(word in name for word in ["seasoning", "powder", "paprika", "cumin", "oregano", "salt", "pepper", "parsley", "aleppo"]):
        return "tsp"
    if any(word in name for word in ["broth", "stock", "milk", "wine", "yogurt", "oil", "sauce"]):
        return "cups"
    if any(word in name for word in ["onion", "pepper", "egg", "zucchini", "carrot", "celery", "kale"]):
        return "count"
    if any(word in name for word in ["breadcrumbs", "rice", "flour", "pasta"]):
        return "cups"
    return None


def _convert_to_canonical(name: str, amount: float, unit: str) -> tuple[float | None, str | None, str]:
    unit = _normalize_unit(unit)
    name = normalize_item(name) or name.strip().lower()
    if not name or amount is None or amount <= 0:
        return None, None, "unknown"

    conversion = _lookup_conversion(name)
    category = conversion.get("category")

    if unit in COUNT_UNITS or (not unit and category == "count"):
        return amount, "count", "count"

    if unit in WEIGHT_TO_G:
        return amount * WEIGHT_TO_G[unit], "g", category or "dry"

    if unit in VOLUME_TO_ML:
        # liquids
        if category == "liquid" or name in {
            "water", "milk", "olive oil", "oil", "coconut oil", "broth",
            "vinegar", "soy sauce", "worcestershire sauce", "red wine",
            "orange juice", "tomato juice", "beer",
        }:
            if unit in {"cup", "cups"} and conversion.get("cup_to_ml"):
                return amount * conversion["cup_to_ml"], "ml", "liquid"
            if unit in {"tbsp", "tablespoon", "tablespoons"} and conversion.get("tbsp_to_ml"):
                return amount * conversion["tbsp_to_ml"], "ml", "liquid"
            if unit in {"tsp", "teaspoon", "teaspoons"} and conversion.get("tsp_to_ml"):
                return amount * conversion["tsp_to_ml"], "ml", "liquid"
            return amount * VOLUME_TO_ML[unit], "ml", "liquid"

        # dry ingredients with specific spoon conversions
        if unit in {"tbsp", "tablespoon", "tablespoons"} and conversion.get("tbsp_to_g"):
            return amount * conversion["tbsp_to_g"], "g", category or "dry"
        if unit in {"tsp", "teaspoon", "teaspoons"} and conversion.get("tsp_to_g"):
            return amount * conversion["tsp_to_g"], "g", category or "dry"

        # generic dry volume using cup equivalence
        if conversion.get("cup_to_g"):
            cups_equiv = (amount * VOLUME_TO_ML[unit]) / VOLUME_TO_ML["cup"]
            return cups_equiv * conversion["cup_to_g"], "g", category or "dry"

        return None, None, category or "unknown"

    if not unit and category == "count":
        return amount, "count", "count"

    return None, None, category or "unknown"


def parse_inventory_line(line: str) -> dict[str, Any] | None:
    amount, unit, remainder = parse_quantity_text(line)
    if amount is None:
        return None

    unit = _normalize_unit(unit)

    if not remainder and unit in COUNT_UNITS:
        remainder = unit
        unit = "count"

    name = extract_named_ingredient(remainder or line)
    if not name:
        return None

    if not unit:
        guessed = infer_default_unit(name)
        if guessed:
            unit = guessed

    canonical_amount, canonical_unit, category = _convert_to_canonical(name, amount, unit)
    if canonical_amount is None or canonical_unit is None:
        return None

    return {
        "name": name,
        "amount": round(canonical_amount, 3),
        "unit": canonical_unit,
        "category": category,
        "preferred_unit": _preferred_unit_for_display(name, category, unit),
        "original_input": line.strip(),
    }


def _preferred_unit_for_display(name: str, category: str, entered_unit: str) -> str:
    unit = _normalize_unit(entered_unit)
    if unit:
        return unit
    if category == "count":
        return "count"
    if category == "liquid":
        return "ml"
    return "g"


def _backward_compatible_pantry_record(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        name = normalize_item(item)
        if not name:
            return None
        category = _lookup_conversion(name).get("category", "count")
        return {
            "name": name,
            "amount": 1.0,
            "unit": "count",
            "category": category,
            "preferred_unit": "count",
            "original_input": item,
        }
    if not isinstance(item, dict):
        return None
    name = normalize_item(item.get("name", ""))
    amount = item.get("amount")
    unit = item.get("unit")
    preferred_unit = item.get("preferred_unit", unit)
    category = item.get("category", "unknown")
    if not name or amount is None or not unit:
        return None
    return {
        "name": name,
        "amount": float(amount),
        "unit": unit,
        "category": category,
        "preferred_unit": preferred_unit,
        "original_input": item.get("original_input", ""),
    }


def _merge_pantry_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        key = (record["name"], record["unit"])
        if key not in merged:
            merged[key] = dict(record)
        else:
            merged[key]["amount"] += float(record["amount"])
    return sorted(merged.values(), key=lambda item: item["name"])


def load_pantry(path: Path = PANTRY_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    records: list[dict[str, Any]] = []
    if isinstance(data, list):
        for item in data:
            record = _backward_compatible_pantry_record(item)
            if record:
                records.append(record)
    return _merge_pantry_records(records)


def save_pantry(pantry: list[dict[str, Any]], path: Path = PANTRY_PATH) -> None:
    path.write_text(json.dumps(pantry, indent=2))


def parse_inventory_input(text: str) -> list[dict[str, Any]]:
    records = []
    for raw_line in re.split(r"[\n,;]+", text):
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        record = parse_inventory_line(raw_line)
        if record:
            records.append(record)
    return _merge_pantry_records(records)


def remove_pantry_items_by_name(pantry: list[dict[str, Any]], names_text: str) -> list[dict[str, Any]]:
    names = {normalize_item(chunk) for chunk in re.split(r"[,;\n]+", names_text) if normalize_item(chunk)}
    return [item for item in pantry if item["name"] not in names]


def _convert_from_canonical(name: str, amount: float, canonical_unit: str, preferred_unit: str) -> tuple[float, str]:
    preferred_unit = _normalize_unit(preferred_unit)
    conversion = _lookup_conversion(name)

    if canonical_unit == "count":
        return amount, "count"

    if canonical_unit == "g":
        if preferred_unit in WEIGHT_TO_G:
            return amount / WEIGHT_TO_G[preferred_unit], preferred_unit
        if preferred_unit in {"cup", "cups"} and conversion.get("cup_to_g"):
            return amount / conversion["cup_to_g"], "cups"
        if preferred_unit in {"tbsp", "tablespoon", "tablespoons"} and conversion.get("tbsp_to_g"):
            return amount / conversion["tbsp_to_g"], "tbsp"
        return amount, "g"

    if canonical_unit == "ml":
        if preferred_unit in VOLUME_TO_ML:
            return amount / VOLUME_TO_ML[preferred_unit], preferred_unit
        if preferred_unit in {"cup", "cups"} and conversion.get("cup_to_ml"):
            return amount / conversion["cup_to_ml"], "cups"
        if preferred_unit in {"tbsp", "tablespoon", "tablespoons"} and conversion.get("tbsp_to_ml"):
            return amount / conversion["tbsp_to_ml"], "tbsp"
        return amount, "ml"

    return amount, canonical_unit


def format_pantry_item(record: dict[str, Any]) -> str:
    amount, unit = _convert_from_canonical(
        record["name"],
        float(record["amount"]),
        record["unit"],
        record.get("preferred_unit", record["unit"]),
    )
    if unit == "count":
        return f"{record['name']}: {_format_amount(amount)}"
    return f"{record['name']}: {_format_amount(amount)} {unit}"


def pantry_name_list(pantry: list[dict[str, Any]]) -> list[str]:
    return sorted({item["name"] for item in pantry})


# -----------------------------
# Recommendation scoring
# -----------------------------

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
    return False


def round_to_step(value: float, step: float = SERVING_STEP, mode: str = "up") -> float:
    if value <= 0:
        return step
    if mode == "up":
        return math.ceil(value / step) * step
    if mode == "down":
        return math.floor(value / step) * step
    return round(value / step) * step


def format_servings(value: float | None) -> str:
    if value is None:
        return "N/A"
    rounded = round(value, 2)
    if abs(rounded - round(rounded)) < 1e-6:
        return str(int(round(rounded)))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def format_metric(value: float | None, unit: str) -> str:
    if value is None:
        return "N/A"
    return f"{value:.0f} {unit}"


def _scale_value(value: float | None, servings: float) -> float | None:
    if value is None:
        return None
    return value * servings


def _serving_plan(
    recipe: Recipe,
    max_calories: float | None,
    min_protein: float | None,
    max_sodium: float | None,
    max_fat: float | None,
) -> dict[str, Any]:
    min_required = 1.0
    if min_protein is not None:
        if recipe.protein is None or recipe.protein <= 0:
            return {"possible": False, "reason": "protein_missing"}
        min_required = max(0.25, min_protein / recipe.protein)

    recommended_servings = round_to_step(min_required, SERVING_STEP, mode="up")
    if recommended_servings > MAX_RECOMMENDED_SERVINGS:
        return {"possible": False, "reason": "too_many_servings"}

    scaled_calories = _scale_value(recipe.calories, recommended_servings)
    scaled_protein = _scale_value(recipe.protein, recommended_servings)
    scaled_carbs = _scale_value(recipe.carbs, recommended_servings)
    scaled_fat = _scale_value(recipe.fat, recommended_servings)
    scaled_sodium = _scale_value(recipe.sodium, recommended_servings)

    if max_calories is not None and scaled_calories is not None and scaled_calories > max_calories:
        return {"possible": False, "reason": "calories"}
    if max_sodium is not None and scaled_sodium is not None and scaled_sodium > max_sodium:
        return {"possible": False, "reason": "sodium"}
    if max_fat is not None and scaled_fat is not None and scaled_fat > max_fat:
        return {"possible": False, "reason": "fat"}

    return {
        "possible": True,
        "recommended_servings": recommended_servings,
        "scaled_calories": scaled_calories,
        "scaled_protein": scaled_protein,
        "scaled_carbs": scaled_carbs,
        "scaled_fat": scaled_fat,
        "scaled_sodium": scaled_sodium,
    }


def score_recipe(
    recipe: Recipe,
    pantry_names: list[str],
    max_calories: float | None = None,
    min_protein: float | None = None,
    max_sodium: float | None = None,
    max_fat: float | None = None,
    strict: bool = True,
) -> dict[str, Any] | None:
    plan = _serving_plan(recipe, max_calories, min_protein, max_sodium, max_fat)
    if strict and not plan.get("possible"):
        return None

    matches: list[str] = []
    matched_pantry: list[str] = []

    for pantry_item in pantry_names:
        for ingredient in recipe.ingredient_index:
            if _ingredients_match(pantry_item, ingredient):
                matches.append(ingredient)
                matched_pantry.append(pantry_item)
                break

    matched_set = sorted(set(matches))
    missing = sorted(set(recipe.ingredient_index) - set(matched_set))
    useful_matches = [x for x in matched_set if x not in GENERIC_INGREDIENTS]
    useful_missing = [x for x in missing if x not in GENERIC_INGREDIENTS]
    coverage = len(matched_set) / len(recipe.ingredient_index) if recipe.ingredient_index else 0.0

    score = len(useful_matches) * 14.0 + coverage * 32.0
    if plan.get("possible"):
        score += 25.0
    if recipe.rating:
        score += recipe.rating * 1.5
    if not useful_matches and pantry_names:
        score -= 20.0

    missing_set = set(useful_missing or missing)
    missing_detailed = []
    seen = set()
    for line in recipe.ingredients:
        key = extract_named_ingredient(line)
        if key in missing_set and line not in seen:
            missing_detailed.append(line)
            seen.add(line)

    why: list[str] = []
    if useful_matches:
        why.append(f"{len(useful_matches)} pantry matches")
    if plan.get("possible"):
        why.append(f"{format_servings(plan['recommended_servings'])} serving(s) fits goal")
    if recipe.rating:
        why.append(f"rated {recipe.rating:.1f}/5")

    return {
        "title": recipe.title,
        "url": recipe.url,
        "score": round(score, 2),
        "coverage": coverage,
        "matched_count": len(useful_matches),
        "total_ingredients": len(recipe.ingredient_index),
        "matched_pantry": sorted(set(matched_pantry)),
        "missing": useful_missing or missing,
        "missing_detailed": missing_detailed,
        "calories": recipe.calories,
        "protein": recipe.protein,
        "carbs": recipe.carbs,
        "fat": recipe.fat,
        "sodium": recipe.sodium,
        "rating": recipe.rating,
        "categories": recipe.categories[:6],
        "ingredients": recipe.ingredients,
        "directions": recipe.directions,
        "recommended_servings": plan.get("recommended_servings", 1.0),
        "scaled_calories": plan.get("scaled_calories"),
        "scaled_protein": plan.get("scaled_protein"),
        "scaled_carbs": plan.get("scaled_carbs"),
        "scaled_fat": plan.get("scaled_fat"),
        "scaled_sodium": plan.get("scaled_sodium"),
        "fits_goals": bool(plan.get("possible")),
        "why": why,
    }


def recommend_recipes(
    recipes: list[Recipe],
    pantry: list[dict[str, Any]] | list[str],
    max_calories: float | None = None,
    min_protein: float | None = None,
    max_sodium: float | None = None,
    max_fat: float | None = None,
    strict: bool = True,
    limit: int = 4,
) -> list[dict[str, Any]]:
    if pantry and isinstance(pantry[0], dict):  # type: ignore[index]
        pantry_names = pantry_name_list(pantry)  # type: ignore[arg-type]
    else:
        pantry_names = sorted({normalize_item(x) for x in pantry if normalize_item(x)})  # type: ignore[arg-type]

    results = []
    for recipe in recipes:
        scored = score_recipe(
            recipe,
            pantry_names,
            max_calories=max_calories,
            min_protein=min_protein,
            max_sodium=max_sodium,
            max_fat=max_fat,
            strict=strict,
        )
        if scored is None:
            continue
        if pantry_names and scored["matched_count"] == 0:
            continue
        results.append(scored)

    results.sort(
        key=lambda item: (
            item["fits_goals"],
            item["score"],
            item["matched_count"],
            item["coverage"],
            item["scaled_protein"] if item["scaled_protein"] is not None else -1,
            item["rating"] if item["rating"] is not None else -1,
        ),
        reverse=True,
    )

    deduped = []
    seen = set()
    for result in results:
        key = result["title"].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(result)
        if len(deduped) >= limit:
            break
    return deduped


def pantry_insights(results: list[dict[str, Any]]) -> dict[str, Any]:
    missing_counter: Counter[str] = Counter()
    for result in results:
        missing_counter.update(result.get("missing", [])[:5])
    return {"common_missing": missing_counter.most_common(5)}


def shopping_list_for_recipe(result: dict[str, Any]) -> list[str]:
    return result.get("missing_detailed") or result.get("missing", [])


def get_watch_macro_config(name: str | None):
    if not name:
        return None
    return WATCHABLE_MACROS.get(name.strip().lower())


# -----------------------------
# Recipe line parsing / scaling
# -----------------------------

BARE_FALLBACK_UNITS = {
    "salt": "tsp",
    "black pepper": "tsp",
    "cumin": "tsp",
    "oregano": "tsp",
    "garlic powder": "tsp",
    "mustard": "tsp",
    "ginger": "tsp",
    "cinnamon": "tsp",
    "allspice": "tsp",
    "butter": "tbsp",
    "olive oil": "tbsp",
    "bay leaf": "count",
}

def parse_recipe_ingredient_line(line: str) -> dict[str, Any]:
    cleaned_line = preprocess_ingredient_line(line)
    if not cleaned_line:
        return {
            "name": "",
            "amount": None,
            "unit": None,
            "canonical_amount": None,
            "canonical_unit": None,
            "category": "unknown",
            "original": line,
            "parseable": False,
        }

    amount, unit, remainder = parse_quantity_text(cleaned_line)

    if not remainder and unit in COUNT_UNITS:
        remainder = unit
        unit = "count"

    name = extract_named_ingredient(remainder or cleaned_line)
    if not name:
        name = normalize_item(remainder or cleaned_line)

    if amount is None:
        if name in BARE_FALLBACK_UNITS:
            amount = 1.0
            unit = BARE_FALLBACK_UNITS[name]
        else:
            return {
                "name": name,
                "amount": None,
                "unit": None,
                "canonical_amount": None,
                "canonical_unit": None,
                "category": "unknown",
                "original": line,
                "parseable": False,
            }

    if not unit:
        guessed = infer_default_unit(name)
        if guessed:
            unit = guessed
        else:
            conversion = _lookup_conversion(name)
            if conversion.get("category") == "count":
                unit = "count"

    canonical_amount, canonical_unit, category = _convert_to_canonical(name, amount, unit)

    return {
        "name": name,
        "amount": amount,
        "unit": unit,
        "canonical_amount": canonical_amount,
        "canonical_unit": canonical_unit,
        "category": category,
        "original": line,
        "parseable": canonical_amount is not None and canonical_unit is not None,
    }


def scale_ingredient_line(line: str, factor: float) -> str:
    cleaned_line = preprocess_ingredient_line(line)
    if not cleaned_line or factor == 1:
        return cleaned_line or line

    amount, unit, remainder = parse_quantity_text(cleaned_line)
    if amount is None:
        return cleaned_line
    scaled = amount * factor
    amount_text = _format_amount(scaled)
    if unit:
        return f"{amount_text} {unit} {remainder}".strip()
    return f"{amount_text} {remainder}".strip()


def convert_required_amount_to_pantry_unit(
    name: str,
    required_amount: float,
    required_unit: str,
    pantry_unit: str,
    source_unit_hint: str | None = None,
) -> float | None:
    conv = _lookup_conversion(name)

    if required_unit == pantry_unit:
        return required_amount

    if required_unit == "g" and pantry_unit == "count":
        factor = None
        if source_unit_hint:
            factor = conv.get(f"{source_unit_hint.lower().rstrip('s')}_to_g")
        factor = factor or conv.get("count_to_g")
        if factor:
            return required_amount / factor

    if required_unit == "count" and pantry_unit == "g":
        factor = conv.get("count_to_g")
        if factor:
            return required_amount * factor

    if required_unit == "ml" and pantry_unit == "count":
        factor = conv.get("count_to_ml")
        if factor:
            return required_amount / factor

    if required_unit == "count" and pantry_unit == "ml":
        factor = conv.get("count_to_ml")
        if factor:
            return required_amount * factor

    return None


def subtract_recipe_from_pantry(
    pantry: list[dict[str, Any]],
    recipe_result: dict[str, Any],
    servings: float | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    updated = [dict(item) for item in pantry]
    changes = []
    skipped = []

    factor = float(servings) if servings and servings > 0 else float(recipe_result.get("recommended_servings") or 1.0)

    for line in recipe_result.get("ingredients", []):
        parsed = parse_recipe_ingredient_line(line)
        if not parsed["parseable"]:
            skipped.append(f"Could not parse: {line}")
            continue

        required_amount = float(parsed["canonical_amount"]) * factor
        match_index = next((i for i, item in enumerate(updated) if item["name"] == parsed["name"]), None)
        if match_index is None:
            skipped.append(f"Not in pantry: {scale_ingredient_line(line, factor)}")
            continue

        pantry_item = updated[match_index]
        required_in_pantry_unit = convert_required_amount_to_pantry_unit(
            pantry_item["name"],
            required_amount,
            parsed["canonical_unit"],
            pantry_item["unit"],
            parsed["unit"],
        )
        if required_in_pantry_unit is None:
            skipped.append(f"Unit mismatch for {scale_ingredient_line(line, factor)}")
            continue

        if float(pantry_item["amount"]) < required_in_pantry_unit:
            skipped.append(f"Not enough {parsed['name']} for {scale_ingredient_line(line, factor)}")
            continue

        pantry_item["amount"] = round(float(pantry_item["amount"]) - required_in_pantry_unit, 3)
        changes.append(
            {
                "name": pantry_item["name"],
                "used": scale_ingredient_line(line, factor),
                "remaining": format_pantry_item(pantry_item) if pantry_item["amount"] > 0 else "used up",
            }
        )

    updated = [item for item in updated if float(item["amount"]) > 1e-6]
    updated = _merge_pantry_records(updated)
    return updated, {"changes": changes, "skipped": skipped}


# -----------------------------
# Formatting helpers
# -----------------------------

def nutrition_summary(result: dict[str, Any], scaled: bool = False) -> str:
    fields = []
    for key, unit in NUTRITION_LABELS:
        value = result.get(f"scaled_{key}") if scaled else result.get(key)
        fields.append(format_metric(value, unit))
    return " | ".join(fields)


# -----------------------------
# Parser hotfix patch (consolidated from real test runs)
# -----------------------------

ALIASES.update({
    # brands / branded pantry items
    "zatarains creole mustard": "mustard",
    "creole mustard": "mustard",
    "zatarains creole seasoning": "creole seasoning",
    "creole seasoning": "creole seasoning",
    "mccormick garlic minced": "garlic powder",
    "garlic minced": "garlic powder",
    "mccormick parsley flakes": "parsley",
    "parsley flakes": "parsley",
    "gold medal all-purpose flour": "flour",
    "gold medal all purpose flour": "flour",
    "progresso plain bread crumbs": "breadcrumbs",
    "plain bread crumbs": "breadcrumbs",
    "plain breadcrumbs": "breadcrumbs",
    "parmigiano reggiano pdo": "parmesan cheese",
    "parmigiano reggiano": "parmesan cheese",
    "shaved parmigiano reggiano pdo": "parmesan cheese",
    "prosciutto di parma pdo": "ham",
    "prosciutto di parma": "ham",
    "cilento pdo extra virgin olive oil": "olive oil",
    "traditional balsamic vinegar of modena pdo": "vinegar",
    "balsamic vinegar of modena pdo": "vinegar",

    # seasoning / spice variants
    "ground mustard": "mustard",
    "ground ginger": "ginger",
    "garlic pepper blend": "garlic pepper blend",
    "chipotle chile pepper powder": "chili powder",
    "chipotle chili powder": "chili powder",
    "dried thyme": "thyme",
    "thyme": "thyme",
    "creole seasoning": "creole seasoning",
    "chili powder": "chili powder",
    "pepper": "black pepper",
    "salt and freshly ground pepper": "salt and pepper",

    # vegetables / produce variants
    "jalapeno chiles": "jalapeno",
    "jalapeno chile": "jalapeno",
    "jalapeno peppers": "jalapeno",
    "jalapeno pepper": "jalapeno",
    "jalapeño chiles": "jalapeno",
    "jalapeño chile": "jalapeno",
    "avocados": "avocado",
    "avocadoes": "avocado",
    "baby spinach": "spinach",
    "low-sodium chicken broth": "broth",
    "pasta sauce": "tomato sauce",
    "italian style tomatoes": "tomatoes",
    "diced tomatoes": "tomatoes",
    "chickpeas": "chickpeas",

    # proteins
    "boneless skinless chicken thighs": "chicken",
    "chicken thighs": "chicken",
    "skinless chicken thighs": "chicken",
    "turkey breast": "turkey",
    "bone-in whole turkey breast": "turkey",
    "whole turkey breast": "turkey",

    # misc
    "firm butter": "butter",
    "bay leaf": "bay leaf",
    "bay leaves": "bay leaf",
    "box spaghetti": "spaghetti",
    "cheese blend": "mozzarella cheese",
})

DEFAULT_BARE_NUMBER_UNITS.update({
    "mustard": "tsp",
    "ginger": "tsp",
    "garlic pepper blend": "tsp",
    "thyme": "tsp",
    "creole seasoning": "tsp",
    "chili powder": "tsp",
    "parsley": "tsp",
    "cilantro": "tbsp",
    "jalapeno": "count",
    "avocado": "count",
    "bay leaf": "count",
    "chickpeas": "cups",
    "tomato sauce": "cups",
    "tomato paste": "tbsp",
    "bread": "count",
    "spaghetti": "cups",
    "turkey": "pound",
    "ham": "oz",
})

INGREDIENT_CONVERSIONS.update({
    "mustard": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "ginger": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "garlic pepper blend": {"category": "dry", "tsp_to_g": 3.0, "tbsp_to_g": 9.0},
    "thyme": {"category": "dry", "tsp_to_g": 1.0, "tbsp_to_g": 3.0},
    "creole seasoning": {"category": "dry", "tsp_to_g": 2.2, "tbsp_to_g": 6.6},
    "chili powder": {"category": "dry", "tsp_to_g": 2.7, "tbsp_to_g": 8.1},
    "cilantro": {"category": "dry", "cup_to_g": 16.0, "tbsp_to_g": 1.0, "tsp_to_g": 0.35},
    "mustard": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "tomato paste": {"category": "dry", "tbsp_to_g": 16.0, "tsp_to_g": 5.3},
    "chickpeas": {"category": "dry", "cup_to_g": 164.0},
    "cream cheese": {"category": "dry", "oz_to_g": 28.3495},
    "avocado": {"category": "count", "count_to_g": 150.0},
    "jalapeno": {"category": "count", "count_to_g": 14.0},
    "bay leaf": {"category": "count", "count_to_g": 0.5, "leaf_to_g": 0.5},
    "turkey": {"category": "dry", "cup_to_g": 140.0},
    "ham": {"category": "dry", "cup_to_g": 140.0},
    "tomato sauce": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
})

# Also treat these container words as count-like when parsing.
COUNT_UNITS = COUNT_UNITS | {"box", "boxes", "jar", "jars", "pkg", "package", "packages"}

# Common noise words in branded/annotated ingredients.
STOPWORDS = STOPWORDS | {
    "brand", "style", "plain", "lightly", "beaten", "shaved", "pdo", "traditional", "modena",
    "creole", "mccormick", "zatarains", "gold", "medal", "progresso", "cilento", "shredded",
    "softened", "seeded", "lengthwise", "halved", "seed", "seedless", "deep", "frying"
}
NAME_STRIP_TOKENS = NAME_STRIP_TOKENS | {
    "etc", "inch", "inches", "ozs", "lb", "lbs", "box", "boxes"
}

SKIP_LINE_PATTERNS = SKIP_LINE_PATTERNS | {
    "salt and pepper",
    "salt and pepper to taste",
    "salt and freshly ground pepper to taste",
    "salt and pepper to season chicken",
    "salt and freshly ground pepper",
    "salt and freshly ground black pepper",
    "vegetable oil for deep frying",
    "olives sausage onions green peppers etc",
    "olives, sausage, onions, green peppers, etc",
}

BRAND_NOISE_WORDS = {
    "mccormick", "zatarains", "gold", "medal", "progresso", "pdo", "cilento", "traditional",
    "modena"
}


def preprocess_ingredient_line(line: str) -> str:
    text = str(line).strip()
    if not text:
        return ""

    text = re.sub(r"^\s*[\*\-•]+\s*", "", text)

    for old, new in UNICODE_FRACTIONS.items():
        text = text.replace(old, new)

    # normalize common hyphenated amounts like 14-1/2 or 15-oz.
    text = re.sub(r"(\d+)-(\d+/\d+)", r"\1 \2", text)
    text = re.sub(r"(\d+)-\s*(oz|ounce|ounces|lb|lbs|pound|pounds)\b", r"\1 \2", text, flags=re.I)

    text = text.replace(";", ",")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text).strip(" ,;")

    lower = text.lower().strip()
    if (
        lower in SKIP_LINE_PATTERNS
        or "salt and pepper" in lower
        or "both salt and pepper" in lower
        or lower.endswith("to taste")
        or lower.endswith("for deep frying")
        or lower.endswith("etc")
    ):
        return ""
    if lower.startswith("for the ") and lower.endswith(":"):
        return ""
    if lower.endswith(":"):
        return ""

    for marker in [
        ", i like using",
        " i like using",
        ", such as ",
        ", preferably ",
        "(optional)",
        " optional",
        ", divided",
        ", drained",
        ", rinsed",
        ", halved",
        ", chopped",
        ", sliced",
        ", diced",
        ", minced",
        ", roughly chopped",
        ", seeded",
        ", pitted and sliced",
        ", husks removed and rinsed",
        ", thawed if frozen",
        ", undrained",
    ]:
        idx = lower.find(marker)
        if idx != -1:
            text = text[:idx].strip(" ,")
            lower = text.lower()

    for pattern, repl in TEXT_NUMBER_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.I)

    text = re.sub(r"^\s*pinch(?:\s+of)?\s+", "1/8 teaspoon ", text, flags=re.I)
    text = re.sub(r"^\s*dash(?:\s+of)?\s+", "1/16 teaspoon ", text, flags=re.I)

    # 1 tbsp + 2 tsp olive oil  ->  5 tsp olive oil
    mix = re.match(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(tbsp|tablespoons?|tsp|teaspoons?)\s*\+\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(tbsp|tablespoons?|tsp|teaspoons?)\s+(.+)$",
        text,
        flags=re.I,
    )
    if mix:
        a1 = _amount_to_float(mix.group(1)) or 0
        u1 = _normalize_unit(mix.group(2))
        a2 = _amount_to_float(mix.group(3)) or 0
        u2 = _normalize_unit(mix.group(4))
        tail = mix.group(5).strip()

        total_tsp = 0.0
        total_tsp += a1 * (3 if u1 in {"tbsp", "tablespoon", "tablespoons"} else 1)
        total_tsp += a2 * (3 if u2 in {"tbsp", "tablespoon", "tablespoons"} else 1)

        text = f"{_format_amount(total_tsp)} tsp {tail}"

    # choose first value in a range like 4 to 5 leaf kale
    text = re.sub(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(?:to|-)\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\b",
        r"\1",
        text,
        flags=re.I,
    )

    # 1 6-lb turkey -> 6 lb turkey
    combo_weight = re.match(
        r"^(\d+)\s+(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(lb|lbs|pound|pounds)\s+(.+)$",
        text,
        flags=re.I,
    )
    if combo_weight:
        count_amt = _amount_to_float(combo_weight.group(1)) or 1
        weight_amt = _amount_to_float(combo_weight.group(2)) or 0
        unit = combo_weight.group(3)
        tail = combo_weight.group(4).strip()
        text = f"{_format_amount(count_amt * weight_amt)} {unit} {tail}"

    # 1 (32-ounce) box broth -> 32 ounce broth
    package_pattern = re.compile(
        r"""^
        (\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*
        \(\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*[- ]?
        (fluid ounce|fluid ounces|fl oz|ounce|ounces|oz)\s*\)\s*
        (?:can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|bottle|bottles|box|boxes)\s+
        (.+)$
        """,
        re.I | re.X,
    )
    m = package_pattern.match(text)
    if m:
        outer_amt = _amount_to_float(m.group(1))
        inner_amt = _amount_to_float(m.group(2))
        inner_unit = _normalize_unit(m.group(3))
        ingredient = m.group(4).strip(" ,")
        if outer_amt is not None and inner_amt is not None:
            total_amt = outer_amt * inner_amt
            text = f"{_format_amount(total_amt)} {inner_unit} {ingredient}"

    # package words without explicit size
    text = re.sub(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s+(can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|bottle|bottles|box|boxes)\s+",
        r"\1 count ",
        text,
        flags=re.I,
    )

    # keep first option only in OR chains
    text = re.split(r"\s+--or--\s+|\s+\bor\b\s+", text, maxsplit=1, flags=re.I)[0].strip(" ,")

    return text


def infer_default_unit(name: str) -> str | None:
    if name in DEFAULT_BARE_NUMBER_UNITS:
        return DEFAULT_BARE_NUMBER_UNITS[name]
    if any(word in name for word in ["seasoning", "powder", "paprika", "cumin", "oregano", "salt", "pepper", "parsley", "aleppo", "ginger", "thyme", "mustard"]):
        return "tsp"
    if any(word in name for word in ["broth", "stock", "milk", "wine", "yogurt", "oil", "sauce", "vinegar"]):
        return "cups"
    if any(word in name for word in ["onion", "pepper", "egg", "zucchini", "carrot", "celery", "kale", "jalapeno", "avocado", "bay leaf"]):
        return "count"
    if any(word in name for word in ["breadcrumbs", "rice", "flour", "pasta", "spaghetti", "chickpeas"]):
        return "cups"
    return None


def parse_recipe_ingredient_line(line: str) -> dict[str, Any]:
    cleaned_line = preprocess_ingredient_line(line)
    if not cleaned_line:
        return {
            "name": "",
            "amount": None,
            "unit": None,
            "canonical_amount": None,
            "canonical_unit": None,
            "category": "unknown",
            "original": line,
            "parseable": False,
        }

    amount, unit, remainder = parse_quantity_text(cleaned_line)
    source_unit = unit or None

    # count-style lines like "2 onions chopped" where the remainder is only prep words
    remainder_name = extract_named_ingredient(remainder) if remainder else ""
    if unit in COUNT_UNITS and not remainder_name:
        remainder = f"{unit} {remainder}".strip()
        unit = "count"

    name = extract_named_ingredient(remainder or cleaned_line)
    if not name:
        name = normalize_item(remainder or cleaned_line)

    if amount is None:
        return {
            "name": name,
            "amount": None,
            "unit": None,
            "canonical_amount": None,
            "canonical_unit": None,
            "category": "unknown",
            "original": line,
            "parseable": False,
        }

    if not unit:
        guessed = infer_default_unit(name)
        if guessed:
            unit = guessed
        else:
            conversion = _lookup_conversion(name)
            if conversion.get("category") == "count":
                unit = "count"

    canonical_amount, canonical_unit, category = _convert_to_canonical(name, amount, unit)

    return {
        "name": name,
        "amount": amount,
        "unit": unit,
        "source_unit": source_unit,
        "canonical_amount": canonical_amount,
        "canonical_unit": canonical_unit,
        "category": category,
        "original": line,
        "parseable": canonical_amount is not None and canonical_unit is not None,
    }


def convert_required_amount_to_pantry_unit(
    name: str,
    required_amount: float,
    required_unit: str,
    pantry_unit: str,
    source_unit_hint: str | None = None,
) -> float | None:
    conv = _lookup_conversion(name)

    if required_unit == pantry_unit:
        return required_amount

    # canonical g <-> pantry count using specific per-item factors
    if required_unit == "g" and pantry_unit == "count":
        factor = None
        if source_unit_hint:
            hint = source_unit_hint.lower().rstrip("s")
            factor = conv.get(f"{hint}_to_g")
        factor = factor or conv.get("count_to_g")
        if factor:
            return required_amount / factor

    if required_unit == "count" and pantry_unit == "g":
        factor = conv.get("count_to_g")
        if factor:
            return required_amount * factor

    if required_unit == "ml" and pantry_unit == "count":
        factor = conv.get("count_to_ml")
        if factor:
            return required_amount / factor

    if required_unit == "count" and pantry_unit == "ml":
        factor = conv.get("count_to_ml")
        if factor:
            return required_amount * factor

    return None


# -----------------------------
# Additional parser patch from later test runs
# -----------------------------

def estimate_calorie_target(weight: float | None, weight_unit: str = "lb", goal: str = "maintain") -> float | None:
    if weight is None or weight <= 0:
        return None
    weight_lb = weight * 2.20462 if weight_unit.lower() == "kg" else weight
    multipliers = {
        "cut": 11.0,
        "maintain": 14.0,
        "muscle building": 16.0,
        "build muscle": 16.0,
        "bulk": 16.0,
    }
    return round(weight_lb * multipliers.get(goal.lower(), 14.0))

ALIASES.update({
    # bare seasonings / spices / liquids
    "freshly ground pepper": "black pepper",
    "cracked black pepper": "black pepper",
    "fresh ground pepper": "black pepper",
    "pepper": "black pepper",
    "sea salt": "salt",
    "cumin seeds": "cumin",
    "dried oregano": "oregano",
    "garlic powder": "garlic powder",
    "ground allspice": "allspice",
    "cinnamon": "cinnamon",
    "fresh ginger": "ginger",
    "red pepper flakes": "red pepper flakes",
    "cayenne": "cayenne",
    "italian seasoning": "italian seasoning",
    "prepared mustard": "mustard",
    "clarified butter": "butter",

    # produce / pantry / packaged items
    "cauliflower": "cauliflower",
    "sweet onion": "onion",
    "shallot": "shallot",
    "shallots": "shallot",
    "artichokes": "artichoke",
    "artichoke": "artichoke",
    "tomatillos": "tomatillo",
    "tomatillo": "tomatillo",
    "grape tomatoes": "tomatoes",
    "portabella mushrooms": "mushrooms",
    "jalapeno": "jalapeno",
    "jalapenos": "jalapeno",
    "jalapeño": "jalapeno",
    "jalapeños": "jalapeno",
    "avocado": "avocado",
    "uncooked instant rice": "rice",
    "instant rice": "rice",
    "orange juice": "orange juice",
    "tomato juice": "tomato juice",
    "crushed tomatoes": "tomatoes",
    "stewed tomatoes": "tomatoes",
    "petite diced tomatoes": "tomatoes",
    "white kidney beans": "beans",
    "chickpeas": "chickpeas",
    "marjoram": "marjoram",
    "beer": "beer",
    "applesauce": "applesauce",
    "bay leaves": "bay leaf",
    "bay leaf": "bay leaf",

    # proteins / cheeses / branded food
    "ground chicken": "chicken",
    "lean ground chicken": "chicken",
    "ground turkey breast": "turkey",
    "extra lean ground turkey breast": "turkey",
    "grated parmesan cheese": "parmesan cheese",
    "grated cheese": "cheddar cheese",
    "cheese": "cheddar cheese",
    "progresso plain bread crumbs": "breadcrumbs",
    "plain bread crumbs": "breadcrumbs",
    "panko": "breadcrumbs",
    "portobello mushrooms": "mushrooms",
    "parmesean cheese": "parmesan cheese",
})

DEFAULT_BARE_NUMBER_UNITS.update({
    "garlic": "count",
    "ginger": "tsp",
    "cinnamon": "tsp",
    "allspice": "tsp",
    "red pepper flakes": "tsp",
    "cayenne": "tsp",
    "italian seasoning": "tsp",
    "cauliflower": "cups",
    "shallot": "count",
    "artichoke": "count",
    "tomatillo": "count",
    "orange juice": "cups",
    "tomato juice": "cups",
    "rice": "cups",
    "beans": "cups",
    "marjoram": "count",
    "beer": "cups",
    "applesauce": "cups",
    "mushrooms": "cups",
    "parmesan cheese": "cups",
    "black pepper": "tsp",
    "butter": "tbsp",
})

INGREDIENT_CONVERSIONS.update({
    "garlic": {"category": "count", "count_to_g": 5.0, "clove_to_g": 5.0},
    "ginger": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "cinnamon": {"category": "dry", "tsp_to_g": 2.6, "tbsp_to_g": 7.8},
    "allspice": {"category": "dry", "tsp_to_g": 2.0, "tbsp_to_g": 6.0},
    "red pepper flakes": {"category": "dry", "tsp_to_g": 1.8, "tbsp_to_g": 5.4},
    "cayenne": {"category": "dry", "tsp_to_g": 1.8, "tbsp_to_g": 5.4},
    "italian seasoning": {"category": "dry", "tsp_to_g": 1.0, "tbsp_to_g": 3.0},
    "cauliflower": {"category": "dry", "cup_to_g": 107.0, "count_to_g": 575.0},
    "shallot": {"category": "count", "count_to_g": 44.0},
    "artichoke": {"category": "count", "count_to_g": 128.0},
    "tomatillo": {"category": "count", "count_to_g": 34.0},
    "orange juice": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "tomato juice": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "rice": {"category": "dry", "cup_to_g": 185.0, "tbsp_to_g": 11.6, "tsp_to_g": 3.9},
    "beans": {"category": "dry", "cup_to_g": 177.0},
    "marjoram": {"category": "count", "count_to_g": 20.0, "bunch_to_g": 20.0},
    "beer": {"category": "liquid", "cup_to_ml": 240.0, "tbsp_to_ml": 15.0, "tsp_to_ml": 5.0},
    "applesauce": {"category": "dry", "cup_to_g": 245.0, "tbsp_to_g": 15.3},
    "mushrooms": {"category": "dry", "cup_to_g": 70.0, "count_to_g": 84.0},
    "parmesan cheese": {"category": "dry", "cup_to_g": 100.0, "tbsp_to_g": 5.0},
    "black pepper": {"category": "dry", "tsp_to_g": 2.3, "tbsp_to_g": 6.9, "grind_to_g": 0.036},
    "butter": {"category": "dry", "tbsp_to_g": 14.2, "tsp_to_g": 4.7, "cup_to_g": 227.0},
    "olive oil": {"category": "liquid", "tbsp_to_ml": 14.8, "tsp_to_ml": 4.9, "cup_to_ml": 236.6},
})

COUNT_UNITS = COUNT_UNITS | {"bunch", "bunches", "pint", "pints", "grind", "grinds", "pkg", "pkgs"}
NAME_STRIP_TOKENS = NAME_STRIP_TOKENS | {"concentrate", "unsweetened", "unswe", "roughly", "removed", "rinsed", "halved", "whole", "dark", "dressing"}
SKIP_LINE_PATTERNS = SKIP_LINE_PATTERNS | {
    "salt", "pepper", "salt and freshly ground pepper, to taste", "kosher salt and black pepper",
    "both salt and pepper",
}

_old_normalize_unit = _normalize_unit

def _normalize_unit(unit: str) -> str:
    unit = _clean_text(unit).strip(" .,")
    unit_map = {
        "t": "tbsp",
        "t.": "tbsp",
        "tbl": "tbsp",
        "tb": "tbsp",
        "pkgs": "pkg",
        "pkg": "pkg",
    }
    return unit_map.get(unit, _old_normalize_unit(unit))

_old_parse_amount_token = _parse_amount_token

def _parse_amount_token(token: str) -> float | None:
    token = token.strip()
    if re.fullmatch(r"\d+-\d+/\d+", token):
        whole, frac = token.split("-", 1)
        try:
            return float(whole) + float(Fraction(frac))
        except Exception:
            pass
    return _old_parse_amount_token(token)


def preprocess_ingredient_line(line: str) -> str:
    text = str(line).strip()
    if not text:
        return ""

    text = re.sub(r"^\s*[\*\-•]+\s*", "", text)
    for old, new in UNICODE_FRACTIONS.items():
        text = text.replace(old, new)

    text = text.replace("®", " ").replace("™", " ").replace("’", "'")
    text = re.sub(r"(\d+)-(\d+/\d+)", r"\1 \2", text)
    text = text.replace(";", ",")
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text).strip(" ,;")

    lower = text.lower().strip()
    if lower in SKIP_LINE_PATTERNS:
        return ""
    if lower.startswith("for the ") and lower.endswith(":"):
        return ""
    if lower.endswith(":"):
        return ""
    if " etc" in lower or lower.endswith("etc"):
        return ""
    if re.fullmatch(r"salt\s+and\s+pepper.*", lower):
        return ""
    if "deep frying" in lower:
        return ""
    if "to taste" in lower and ("salt" in lower or "pepper" in lower):
        return ""

    for marker in [", i like using", " i like using", ", such as ", ", preferably ", "(optional)", " optional", ", divided"]:
        idx = lower.find(marker)
        if idx != -1:
            text = text[:idx].strip(" ,")
            lower = text.lower()

    for pattern, repl in TEXT_NUMBER_REPLACEMENTS:
        text = re.sub(pattern, repl, text, flags=re.I)

    text = re.sub(r"^\s*pinch(?:\s+of)?\s+", "1/8 teaspoon ", text, flags=re.I)
    text = re.sub(r"^\s*dash(?:\s+of)?\s+", "1/16 teaspoon ", text, flags=re.I)

    # 1 tbsp + 2 tsp olive oil
    combo = re.match(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(tbsp|tablespoon|tablespoons|t)\s*\+\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(tsp|teaspoon|teaspoons)\s+(.+)$",
        text,
        flags=re.I,
    )
    if combo:
        a = _amount_to_float(combo.group(1))
        b = _amount_to_float(combo.group(3))
        tail = combo.group(5)
        if a is not None and b is not None:
            total_tbsp = a + b / 3.0
            text = f"{_format_amount(total_tbsp)} tbsp {tail}"

    # pepper grinds -> tsp approximation
    grind_match = re.match(r"^(\d+(?:\.\d+)?)\s+grinds?(?:\s+\d+(?:\.\d+)?)?\s+(.+pepper.*)$", text, flags=re.I)
    if grind_match:
        amt = float(grind_match.group(1)) / 64.0
        text = f"{_format_amount(amt)} tsp {grind_match.group(2)}"

    # choose first value in ranges like 4 to 5 leaf kale
    text = re.sub(r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*(?:to|-)\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\b", r"\1", text, flags=re.I)

    # strip descriptive parenthetical notes but keep package-size handling below
    text = re.sub(r"\((not[^)]*|about[^)]*|[^)]*inch[^)]*|[^)]*from concentrate[^)]*)\)", "", text, flags=re.I)

    package_pattern = re.compile(
        r"""^
        (\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*
        \(\s*(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*[- ]?
        (fluid ounce|fluid ounces|fl oz|ounce|ounces|oz|lb|lb\.|lbs|lbs\.|pound|pounds)\s*\)\s*
        (?:count\s+)?(?:can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|bottle|bottles|box|boxes)\s+
        (.+)$
        """,
        re.I | re.X,
    )
    m = package_pattern.match(text)
    if m:
        outer_amt = _amount_to_float(m.group(1))
        inner_amt = _amount_to_float(m.group(2))
        inner_unit = _normalize_unit(m.group(3))
        ingredient = m.group(4).strip(" ,")
        ingredient_lower = ingredient.lower()
        if inner_unit in {"oz", "ounce", "ounces"} and any(w in ingredient_lower for w in ["broth", "stock", "milk", "oil", "sauce", "vinegar", "wine", "juice", "beer"]):
            inner_unit = "fl oz"
        if outer_amt is not None and inner_amt is not None:
            total_amt = outer_amt * inner_amt
            text = f"{_format_amount(total_amt)} {inner_unit} {ingredient}"

    inline_size_pattern = re.compile(
        r"""^
        (?:(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s+)?
        (\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s*[- ]?
        (oz|oz\.|ounce|ounces|lb|lb\.|lbs|lbs\.|pound|pounds)
        \s+(?:can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|box|boxes)\s+
        (.+)$
        """,
        re.I | re.X,
    )
    m = inline_size_pattern.match(text)
    if m:
        outer = _amount_to_float(m.group(1) or "1")
        inner = _amount_to_float(m.group(2))
        unit = _normalize_unit(m.group(3))
        ingredient = m.group(4).strip(" ,")
        ingredient_lower = ingredient.lower()
        if unit in {"oz", "ounce", "ounces"} and any(w in ingredient_lower for w in ["broth", "stock", "milk", "oil", "sauce", "vinegar", "wine", "juice", "beer"]):
            unit = "fl oz"
        if outer is not None and inner is not None:
            total = outer * inner
            text = f"{_format_amount(total)} {unit} {ingredient}"

    # plain package/can without size => count
    text = re.sub(
        r"^(\d+(?:\s+\d+/\d+|/\d+|\.\d+)?)\s+(can|cans|package|packages|pkg|pkgs|bag|bags|jar|jars|bottle|bottles|box|boxes)\s+",
        r"\1 count ",
        text,
        flags=re.I,
    )

    text = re.split(r"\s+--or--\s+|\s+\bor\b\s+", text, maxsplit=1, flags=re.I)[0].strip(" ,")
    return text


def extract_named_ingredient(text: str) -> str:
    cleaned = _clean_text(text)
    if not cleaned:
        return ""
    cleaned = re.sub(r"\b(?:extra\s+virgin|not\s+the\s+dressing|not\s+from\s+concentrate|roughly|freshly|ground|dried|halved|seeded|pitted|sliced|diced|minced|chopped|shaved|grated|cut\s+into\s+thirds\s+lengthwise|cut\s+into\s+bite\-sized\s+pieces|coarsely\s+chopped|drained\s+and\s+rinsed)\b", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    possible_keys = set(ALIASES.keys()) | set(INGREDIENT_CONVERSIONS.keys())
    matches = [key for key in possible_keys if key and key in cleaned]
    if matches:
        best = sorted(matches, key=len, reverse=True)[0]
        return ALIASES.get(best, best)
    return normalize_item(cleaned)


def infer_default_unit(name: str) -> str | None:
    if name in DEFAULT_BARE_NUMBER_UNITS:
        return DEFAULT_BARE_NUMBER_UNITS[name]
    if any(word in name for word in ["seasoning", "powder", "paprika", "cumin", "oregano", "salt", "pepper", "parsley", "aleppo", "cinnamon", "allspice", "cayenne", "ginger", "thyme"]):
        return "tsp"
    if any(word in name for word in ["broth", "stock", "milk", "wine", "juice", "beer", "yogurt", "oil", "sauce", "tomato juice"]):
        return "cups"
    if any(word in name for word in ["onion", "pepper", "egg", "zucchini", "carrot", "celery", "kale", "garlic", "jalapeno", "avocado", "artichoke", "tomatillo", "shallot"]):
        return "count"
    if any(word in name for word in ["breadcrumbs", "rice", "flour", "pasta", "cauliflower", "beans"]):
        return "cups"
    return None


def _convert_to_canonical(name: str, amount: float, unit: str) -> tuple[float | None, str | None, str]:
    unit = _normalize_unit(unit)
    name = normalize_item(name) or name.strip().lower()
    if not name or amount is None or amount <= 0:
        return None, None, "unknown"
    conversion = _lookup_conversion(name)
    category = conversion.get("category")

    if unit in COUNT_UNITS or (not unit and category == "count"):
        return amount, "count", "count"

    if unit in WEIGHT_TO_G:
        return amount * WEIGHT_TO_G[unit], "g", category or "dry"

    if unit in VOLUME_TO_ML:
        ml_amt = amount * VOLUME_TO_ML[unit]
        if category == "liquid" or name in {"water", "milk", "olive oil", "oil", "broth", "vinegar", "soy sauce", "worcestershire sauce", "red wine", "orange juice", "tomato juice", "beer"}:
            if conversion.get("cup_to_ml"):
                cups = ml_amt / VOLUME_TO_ML["cup"]
                return cups * conversion["cup_to_ml"], "ml", "liquid"
            return ml_amt, "ml", "liquid"
        if conversion.get("cup_to_g"):
            cups = ml_amt / VOLUME_TO_ML["cup"]
            return cups * conversion["cup_to_g"], "g", category or "dry"
        if unit in {"tbsp", "tablespoon", "tablespoons"} and conversion.get("tbsp_to_g"):
            return amount * conversion["tbsp_to_g"], "g", category or "dry"
        if unit in {"tsp", "teaspoon", "teaspoons"} and conversion.get("tsp_to_g"):
            return amount * conversion["tsp_to_g"], "g", category or "dry"
        return None, None, category or "unknown"

    if not unit and category == "count":
        return amount, "count", "count"
    return None, None, category or "unknown"


def parse_recipe_ingredient_line(line: str) -> dict[str, Any]:
    cleaned_line = preprocess_ingredient_line(line)
    if not cleaned_line:
        return {
            "name": "",
            "amount": None,
            "unit": None,
            "source_unit": None,
            "canonical_amount": None,
            "canonical_unit": None,
            "category": "unknown",
            "original": line,
            "parseable": False,
        }

    amount, unit, remainder = parse_quantity_text(cleaned_line)
    source_unit = unit or None

    remainder_name = extract_named_ingredient(remainder) if remainder else ""
    if unit in COUNT_UNITS and not remainder_name:
        remainder = f"{unit} {remainder}".strip()
        unit = "count"

    name = extract_named_ingredient(remainder or cleaned_line)
    if not name:
        name = normalize_item(remainder or cleaned_line)

    # bare ingredient lines like "salt" or "clarified butter"
    if amount is None and name:
        guessed = infer_default_unit(name)
        if guessed:
            amount = 1.0
            unit = guessed

    if amount is None:
        return {
            "name": name,
            "amount": None,
            "unit": None,
            "source_unit": None,
            "canonical_amount": None,
            "canonical_unit": None,
            "category": "unknown",
            "original": line,
            "parseable": False,
        }

    if not unit:
        guessed = infer_default_unit(name)
        if guessed:
            unit = guessed
        else:
            conversion = _lookup_conversion(name)
            if conversion.get("category") == "count":
                unit = "count"

    canonical_amount, canonical_unit, category = _convert_to_canonical(name, amount, unit)
    return {
        "name": name,
        "amount": amount,
        "unit": unit,
        "source_unit": source_unit,
        "canonical_amount": canonical_amount,
        "canonical_unit": canonical_unit,
        "category": category,
        "original": line,
        "parseable": canonical_amount is not None and canonical_unit is not None,
    }

