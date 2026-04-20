# ShelfAware MVP

ShelfAware is a pantry-aware meal recommender. The Phase 3 MVP turns the earlier prototype into a reproducible command-line app with:

- a persistent pantry saved in `user_pantry.json`,
- a saved body-goals profile in `user_profile.json`,
- a daily meal tracker in `daily_meal_log.json`,
- a recipe search space of about 20,000 recipes from `recipes_dataset.json`,
- nutrition-aware ranking using calorie and protein preferences,
- optional extra macro filtering for fat or sodium,
- recipe detail views with ingredients and directions,
- meal tracking toward a daily protein goal.

## Requirements

- Python 3.x
- No external Python packages are required

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

- `recipes_dataset.json` is the local recipe dataset used by the MVP.
- `user_pantry.json` stores the current pantry between runs.
- `user_profile.json` stores the user's saved body-goal settings.
- `daily_meal_log.json` stores meals tracked for the current day.
- Ingredient matching uses local normalization and fuzzy similarity logic built with the Python standard library.

## Project Structure

- `shelfaware_mvp.py`: main Phase 3 app entrypoint
- `shelfaware_cli.py`: compatibility wrapper to the same app
- `recommendation_engine.py`: recipe loading, pantry normalization, ranking, and insight logic
- `report.md`: Phase 3 MVP report
