# ShelfAware MVP Report






# ShelfAware MVP Report

## Executive Summary
ShelfAware is a pantry-aware meal recommendation tool for students and busy home cooks. The Phase 3 MVP helps a user enter the ingredients they already have, set nutrition preferences, receive recipe suggestions from a large recipe dataset, and track meals against a daily protein goal.

Compared with the Phase 2 prototype, this MVP is much closer to a usable product. It now includes a persistent pantry, a larger recipe database, cleaner recommendation output, recipe detail views, a saved body-goals profile, and a daily meal tracker.

## User and Use Case
The main user is a student or young adult who has groceries at home but does not know what meals fit both the current pantry and nutrition goals. A realistic use case is a user opening ShelfAware after class, checking the pantry, asking for high-protein meal ideas under a calorie target, picking one recipe, and logging that meal toward a daily protein goal.

## System Design
The MVP is implemented as a local Python command-line application inside `/mvp/`. The app layer handles user interaction, while the engine handles dataset loading, pantry parsing, normalization, ranking, tracking, and pantry updates. The backend currently loads recipe data from `full_format_recipes.json` and user state from `pantry.json`, `profile.json`, and `tracker_history.json`. 

```mermaid
flowchart LR
    A["User pantry input"] --> B["Pantry parser and normalizer"]
    B --> C["pantry.json"]

    D["Personalized nutrition goals"] --> E["profile.json"]

    F["full_format_recipes.json"] --> G["Recipe loading and ingredient normalization"]
    C --> H["Recommendation engine"]
    E --> H
    G --> H

    H --> I["Ranked recipe list"]
    I --> J["Recipe detail view"]
    J --> K["Shopping list + pantry update"]
    J --> L["Meal tracker entry"]
    L --> M["tracker_history.json"]

```

Main files:

- `shelfaware_mvp.py`: main MVP app and menu flow
- `recommendation_engine.py`: recipe loading, pantry normalization, ranking, profile utilities, and tracker utilities
- `recipes_dataset.json`: recipe dataset
- `user_pantry.json`: saved pantry items
- `user_profile.json`: saved body-goals profile
- `daily_meal_log.json`: daily meal tracker

The recommendation flow combines:

1. pantry overlap between saved ingredients and recipe ingredients,
2. calorie and protein preference alignment,
3. optional extra macro filtering for fat or sodium,
4. recipe rating as a lightweight quality signal.

Recipes are only shown if calorie and protein data exist. Missing fat or sodium values are allowed so the app can still return useful options.

## Data
The main dataset is `mvp/recipes_dataset.json`, which contains about 20,130 recipe records. After preprocessing and filtering out unusable entries, the app loads about 20,049 recipes with valid titles and ingredients.

Typical fields in the dataset include:

- title
- ingredients
- directions
- calories
- protein
- fat
- sodium
- rating
- categories

ShelfAware also maintains small local user-state files:

- `user_pantry.json`
- `user_profile.json`
- `daily_meal_log.json`

Ingredient preprocessing simplifies recipe text into pantry-friendly names. For example, `chicken breast` becomes `chicken`, and `brown rice` becomes `rice`. This improves matching between user input and recipe ingredients.

## Models and Methods
ShelfAware is a recommendation workflow rather than a trained machine learning model. The MVP uses:

- ingredient normalization,
- heuristic ingredient matching,
- nutrition-aware scoring,
- result ranking,
- meal logging against a protein goal.

This was a practical choice for the course MVP. It keeps the project easy to run locally, easy to explain during demo, and reproducible without external dependencies.

For each recipe, the system:

1. normalizes recipe ingredients,
2. compares them against the pantry,
3. computes pantry coverage,
4. rewards recipes that meet calorie and protein preferences,
5. optionally filters on an additional watched macro such as sodium or fat,
6. ranks results by fit score and pantry usefulness.

For body goals, the app stores weight, height, and goal type, then estimates a daily protein target. Users can log either a recommended recipe or a manually entered meal into the daily tracker.

## Evaluation
Evaluation for this MVP is mainly qualitative and product-focused.

### What the MVP does successfully

- stores pantry items across runs,
- searches a recipe space far larger than the Phase 2 hard-coded set,
- supports calorie and protein filtering,
- supports an optional extra macro watch for fat or sodium,
- hides recipes that are missing core calorie or protein data,
- shows a cleaner ranked list before opening full recipe details,
- stores body-goal information and estimates a daily protein target,
- lets users track meals against that target.

### Example usage scenario

If a user stores a pantry such as:

`chicken, rice, spinach, onion, garlic, olive oil, eggs`

and requests recommendations with:

- max calories: `650`
- minimum protein: `30`
- optional extra macro watch: `fat` or `sodium`

the app returns ranked meals that use existing pantry items and better fit the user’s nutrition goals. If the user opens a recipe, the app shows ingredients, directions, missing items, and an option to log the meal into the daily tracker.

### Reproducibility

The MVP is reproducible locally with:

```bash
cd mvp
python3 shelfaware_mvp.py
```

or:

```bash
cd mvp
python3 shelfaware_mvp.py --demo
```

No external Python packages are required.

## Limitations and Risks

1. Ingredient matching is still heuristic, so some recipe matches may be imperfect.
2. The dataset is large, but some ingredient names remain messy after normalization.
3. Protein-target estimation is simple and meant for MVP guidance, not medical advice.
4. The food tracker logs meal totals but does not yet support editing old entries, portion scaling, or micronutrient tracking.
5. The interface is still command-line based, which limits usability compared with a web or mobile interface.
6. Receipt OCR and automatic pantry updates are still future work.

## Next Steps
With 2 to 3 more months, the highest-value upgrades would be:

- a web interface using Streamlit or Flask,
- receipt OCR for automatic pantry updates,
- stronger ingredient ontology and substitution logic,
- multi-day meal planning and grocery list export,
- better tracker features such as meal editing and calorie-goal support,
- real user testing with students to measure recommendation quality and usefulness.

## Summary of Phase 3 Progress
Phase 3 moved ShelfAware from a narrow prototype to a more complete MVP attempt. The project now has a persistent pantry, a large local recipe dataset, nutrition-aware recommendation logic, cleaner recipe browsing, a body-goals profile, and a daily protein tracker. This makes the final MVP much closer to the original product idea and gives the project a stronger base for future development.

