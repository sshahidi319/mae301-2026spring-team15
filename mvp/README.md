# ShelfAware MVP
ShelfAware is a pantry-aware meal recommendation MVP. The system helps a user manage pantry inventory, generate recipe suggestions based on available ingredients, set personalized nutrition goals, track meals, and update pantry amounts after cooking. 

The current MVP includes:
- a persistent pantry saved in `pantry.json`
- a saved nutrition profile in `profile.json`
- meal and nutrition tracking in `tracker_history.json`
- recipe recommendations from `full_format_recipes.json`
- nutrition-aware ranking using calorie and protein preferences
- optional extra filtering for fat or sodium
- recipe detail views with ingredient lists and source links
- pantry updates after cooking
- a built-in quick demo mode

## Interactive Features

**Inside the app you can:**

1. view and edit the saved pantry
2. add or remove pantry items with quantities
3. set personalized nutrition goals using weight, height, and goal type
4. estimate daily calorie and protein targets
5. track meals toward daily nutrition goals
6. generate recipe recommendations with nutrition filters
7. inspect a recipe’s ingredients and source link
8. log a recommended recipe into the tracker
9. update pantry inventory based on recipe usage
10. view daily and monthly tracker statistics
## Requirements
Running the MVP app
- Python 3.x
- No external Python packages are required

## Dataset Access

ShelfAware uses a local processed recipe dataset file called `full_format_recipes.json`.
This is a file loaded by the backend engine during normal app use. The app does not read the raw source CVS directly. 

## Dataset Source

Shelfaware was built using the public Hugging Face dataset:

**Dataset name:** `datahiveai/recipes-with-nutrition`

**Formats available:** CSV and JSON

**Approximate size:** 39,447 recipes in the full dataset

**License on the dataset card:** CC BY-NC 4.0

For this MVP, the raw dataset was preprocessed into the local file `full_format_recipes.json`

## Dataset Link and Preprocessing
**Raw dataset source:**
`datahiveai/recipes-with-nutrition`

If `full_format_recipes.json` is alread included in the `/mvp/` folder, you do **NOT** need to preprocess anything

**Instructions:** Convert larger dataset into `full_format_recipes.json`

The app will work with a larger version of the dataset but only if it is converted

1. download the raw dataset from the Hugging Face dataset page
2. place the download file in the `/mvp/` folder
3. run the preprocessing script `/make_trimmed_dataset.py/` to convert the raw data into `full_format_recipes.json`

**Example:** Creates `full_format_recipes.json` with all recipes in the dataset
```bash
python3 make_trimmed_dataset.py recipes-with-nutrition.cvs

```
**Example with limiting:** Creates `full_format_recipes.json` with 3000 recipes
```bash
python3 make_trimmed_dataset.py recipes-with-nutrition.cvs 3000

```

## Running the MVP

**Interactive mode:**

```bash
cd mvp
python3 shelfaware_mvp.py 
```
This launches the interactive ShelfAwared command-line app

**Quick demo mode:**
```bash
cd mvp
python3 shelfaware_mvp.py --demo
```
This runs a short non-interactive demo using a sample pantry


## Demo Flow

**Recommended demo flow:**

1. Run `python3 shelfaware_mvp.py`.
2. Choose `1` and add pantry items such as
   - 2 lb chicken
   - 2 onions
   - 1 gallong milk
   - 2 cups rice
   - 9 oz salt
   - ect
3. Choose `3` for peronalized nutirion goals
4. Choose `1` to update `weight` and `height`
5. Choose `2` to go back to main menu
6. Choose `2` for **Recipe generator**
7. Set a max calorie target as `suggested from personalized nutrition goals` or manually such as `650`.
8. Set a minimum protein target such as `suggested from personalized nutrition goals` or manually such as `30`.
9. Optionally add fat or sodium limit
10. View the ranked recipes and open one for full details.
11. Add the recipe to the tracker
12. Update the pantry based on selected serving amounts
13. Choose `5` to go back to main menu

## Data Notes

- `full_format_recipes.json` is the processed recipe dataset used directly by the MVP.
- `pantry.json` stores the pantry between runs.
- `profile.json` stores the saved nutrition profile.
- `tracker_history.json` stores tracked meals and servings.
- Ingredient matching matching uses local normalization, parsing heuristics, and pantry comparison logic built into the engine
- some recipe lines are messy in the source data, so pantry parsing is heuristic rather than perfect

## Reproducibility Notes
**To reproduce locally:**
1. install Python 3
2. place the project files inside `/mvp/`
3. make sure `full_format_recipes.json` exsist inside `/mvp/`
4. run
```bash
cd mvp
python3 shelfaware_mvp.py 
```
