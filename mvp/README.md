# ShelfAware MVP

ShelfAware is a pantry-aware meal recommender. The Phase 3 MVP turns the earlier prototype into a reproducible command-line app with:

- a persistent pantry saved in `pantry.json`,
- a saved body-goals profile in `profile.json`,
- a meal and nutrition goal tracker in `tracker_history.json`
- a recipe search space of about 20,000 recipes from `full_format_recipes.json`,
- nutrition-aware ranking using calorie and protein preferences,
- optional extra macro filtering for fat or sodium content preferences,
- recipe detail views with ingredients and link to directions,
- meal tracking toward a daily protein and calorie goal.

## Requirements

- Python 3.x
- No external Python packages are required

## Dataset Access

ShelfAware uses a local recipe dataset file called `full_format_recipes.json`.

To run the MVP, make sure this file is inside the `mvp/` folder:

```bash
mvp/recipes_dataset.json
```

If the dataset does not appear in GitHub because it is large, place `recipes_dataset.json` into the `mvp/` folder manually before running the app.

Once the dataset file is in the folder, start ShelfAware with:

```bash
cd mvp
python3 shelfaware_mvp.py
```

Without `recipes_dataset.json`, the app can open but it will not be able to generate recipe recommendations.

## Dataset Source

Shelfaware was built using the public Hugging Face dataset:

**Dataset name:** `datahiveai/recipes-with-nutrition`

**Formats available:** CSV and JSON

**Approximate size:** 39,447 recipes in the full dataset

**License on the dataset card:** CC BY-NC 4.0

## How to Run

From the repository root:

```bash
cd mvp
python3 shelfaware_mvp.py
```

This opens the interactive ShelfAware menu.

## Quick Demo

To run a non-interactive demo with a sample pantry:

```bash
cd mvp
python3 shelfaware_mvp.py --demo
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

1. Run `python3 shelfaware_mvp.py`.
2. Choose `1` and add pantry items such as `chicken, rice, spinach, onion, garlic, olive oil, eggs`.
3. Choose `2` to get recommendations.
4. Set a max calorie target such as `650`.
5. Set a minimum protein target such as `30`.
6. Optionally watch another macro such as `fat` or `sodium`.
7. View the ranked recipes and open one for full details.
8. Choose `3` to set body goals and track meals.

## Data Notes

- `full_format_recipes.json` is the recipe dataset used by the MVP.
- `pantry.json` stores the current pantry between runs.
- `profile.json` stores the user's saved body and nutrition information.
- `tracker_history.json` stores all meals tracked.
- Ingredient matching uses local normalization and fuzzy similarity logic built with the Python standard library.

## Project Structure

- `shelfaware_mvp.py`: main Phase 3 app entrypoint
- `recommendation_engine.py`: recipe loading, pantry normalization, ranking, and insight logic
- `report.md`: Phase 3 MVP report
