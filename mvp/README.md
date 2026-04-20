# ShelfAware MVP

## Overview

ShelfAware is an AI-powered pantry-aware meal recommendation system that helps users find meals they can prepare using ingredients they already have while also considering nutrition goals.

This MVP demonstrates the core feature: a user provides pantry ingredients and nutrition preferences, and the system returns ranked recipe recommendations, missing ingredient insights, and detailed recipe information.

## Problem and Use Case

Many users struggle to decide what to cook based on the ingredients available in their kitchen. This becomes even more difficult when they are trying to meet calorie, protein, or sodium goals.

ShelfAware addresses this problem by helping users:
- identify recipes that match their available pantry items
- understand which ingredients they are missing most often
- view recipe ingredients and cooking directions
- track meals against personal body-goal settings

## MVP Features

This Phase 3 MVP includes:

- a persistent pantry saved in `user_pantry.json`
- a saved body-goals profile in `user_profile.json`
- a daily meal tracker in `daily_meal_log.json`
- a recipe search space of about 20,000 recipes from `recipes_dataset.json`
- nutrition-aware ranking using calorie, protein, and sodium preferences
- recipe detail views with ingredients and directions
- pantry insights showing the most common missing ingredients

## Repository Contents

The `mvp/` folder contains the following files:

- `shelfaware_mvp.py` - main application entry point for the ShelfAware MVP
- `recommendation_engine.py` - core recommendation, ranking, and ingredient-matching logic
- `recipes_dataset.json` - local recipe dataset used by the MVP
- `user_pantry.json` - saved pantry data between runs
- `user_profile.json` - saved user body-goal settings
- `daily_meal_log.json` - saved daily meal tracking data
- `README.md` - setup and demo instructions
- `report.md` - final MVP report

## Requirements

- Python 3.x
- No external Python packages are required

## Required Files

Before running the MVP, make sure the following files are available in the `mvp/` directory:

- `shelfaware_mvp.py`
- `recommendation_engine.py`
- `recipes_dataset.json`

The following files are used to store user data between runs:

- `user_pantry.json`
- `user_profile.json`
- `daily_meal_log.json`

If these files do not already exist, they may be created automatically by the application during first use.

## Setup

From the repository root, navigate to the MVP folder:

```bash
cd mvp
