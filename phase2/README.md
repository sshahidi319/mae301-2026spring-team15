# ShelfAware Phase 2 Demo

## Dependencies
- Python 3.x

No external Python packages are required for the current prototype.

## How to Run
From the repository root, Mac run:

```bash
cd phase2
python3 demo.py
```

On Windows, run:

```bash
cd phase2
python demo.py
```

## How to Reproduce the Current Demo
1. Open the repository folder in VS Code or another code editor.
2. Open a terminal in the repository root.
3. Change into the `phase2` folder:

```bash
cd phase2
```

4. Run the demo script:

```bash
python3 demo.py
```

On Windows, use:

```bash
python demo.py
```

5. When prompted, enter pantry ingredients, a maximum calorie value, and a minimum protein value.

Example:

```text
chicken, eggs, spinach, rice, olive oil
600
40
```

6. The program will print ranked recipe suggestions based on the pantry items and nutrition preferences. The output includes recipe title, calories, protein, carbs, fat, pantry match count, and missing ingredients.


## Example Input
When prompted, enter:

```text
chicken, eggs, spinach, rice, olive oil
600
40
```

This corresponds to:
- pantry ingredients: chicken, eggs, spinach, rice, olive oil
- maximum calories per serving: 600
- minimum protein: 40 grams

## Expected Output
The program prints ranked recipe suggestions and includes:
- recipe title
- calories
- protein
- carbs
- fat
- pantry match count
- missing ingredients

## Notes
The current prototype uses calorie and protein targets as ranking preferences rather than strict exclusion rules. Recipes that better match the targets are ranked higher, but recipes outside the targets may still appear in the results.

The current recipe set is a small local dataset stored directly in the code. Future work includes expanding the recipe database, likely using a larger Kaggle dataset, adding a running pantry inventory instead of one-time manual input, and potentially changing the recommendation logic to fully exclude recipes that do not meet the user’s nutrition targets once the database is expanded and the running pantry inventory is set up.
