# ShelfAware MVP

## Overview

ShelfAware is an AI-powered pantry-aware meal recommendation system designed to help users find meals they can prepare using ingredients they already have while also considering nutrition goals.

This MVP demonstrates the core feature: a user provides pantry ingredients and nutrition preferences, and the system returns ranked recipe recommendations, missing ingredient insights, and detailed recipe information.

## Problem and Use Case

Many users struggle to decide what to cook based on the ingredients available in their kitchen. This becomes even more difficult when they are trying to meet calorie, protein, or sodium goals.

ShelfAware addresses this problem by helping users:
- identify recipes that match their available pantry items,
- understand which ingredients they are missing most often,
- view recipe ingredients and cooking directions,
- track meals against personal body-goal settings.

## MVP Features

This Version includes:

- a persistent pantry saved locally between runs,
- a saved body-goals profile,
- a daily meal tracker,
- a recipe search space of about 20,000 recipes,
- nutrition-aware ranking using calorie, protein, and sodium preferences,
- recipe detail views with ingredients and directions,
- pantry insights showing the most common missing ingredients.

## Repository Contents

The `mvp/` folder should contain the following files:

- `shelfare_mvp.py` - main entry point for the MVP
- `recipes_dataset.json` - local recipe dataset used by the recommender
- `user_pantry.json` - saved pantry data
- `user_profile.json` - saved user body-goal settings
- `daily_meal_log.json` - saved daily meal tracking data

## Requirements

- Python 3.x
- No external Python packages are required

## Required Files

Before running the MVP, make sure the following files are available in the `mvp/` directory:

- `shelfare_mvp.py`
- `recipes_dataset.json`

The following files may either be included in the repository or created automatically during use:

- `user_pantry.json`
- `user_profile.json`
- `daily_meal_log.json`

If your current implementation creates these files automatically on first run, users do not need to download them separately.

## Download / Access

Download the MVP package here:

[Download ShelfAware MVP](PASTE_YOUR_LINK_HERE)

After downloading, confirm that the `mvp/` folder contains the Python file and the recipe dataset before running the project.

## Setup

From the repository root, navigate to the MVP folder:

```bash
cd mvp
