# ShelfAware MVP

ShelfAware is a pantry-aware meal recommender. The Phase 3 MVP turns the earlier prototype into a reproducible command-line app with:

- a persistent pantry saved in `pantry.json`,
- a saved body-goals profile in `profile.json`,
- a daily meal tracker in `daily_log.json`,
- a recipe search space of about 20,000 recipes from `full_format_recipes.json`,
- nutrition-aware ranking using calorie, protein, and sodium preferences,
- recipe detail views with ingredients and directions,
- pantry insights showing the most common missing ingredients.

## Requirements

- Python 3.x
- No external Python packages are required

## How to Run

From the repository root:

```bash
cd mvp
python3 demo.py
```

This opens the interactive ShelfAware menu.

## Quick Demo

To run a non-interactive demo with a sample pantry:

```bash
cd mvp
python3 demo.py --demo
```

## Interactive Features

Inside the app you can:

1. view the saved pantry,
2. add or remove pantry items,
3. set body goals using weight, height, and goal type,
4. track meals toward a daily protein target,
5. request meal recommendations with nutrition filters,
6. inspect a recipe's ingredients and directions,
7. log a recommended recipe into today's tracker.

## Demo Flow

Recommended grading flow:

1. Run `python3 demo.py`.
2. Choose `1` and add pantry items such as `chicken, rice, spinach, onion, garlic, olive oil, eggs`.
3. Choose `2` to get recommendations.
4. Set a max calorie target such as `650`.
5. Set a minimum protein target such as `30`.
6. Optionally set max sodium or a category keyword.
7. View the ranked recipes and open one for full details.
8. Choose `3` to set body goals and track meals.

## Data Notes

- `full_format_recipes.json` is the local recipe dataset used by the MVP.
- `pantry.json` stores the current pantry between runs.
- `profile.json` stores the user's saved body-goal settings.
- `daily_log.json` stores meals tracked for the current day.
- Ingredient matching uses local normalization and fuzzy similarity logic.
