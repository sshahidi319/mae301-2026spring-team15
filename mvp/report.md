# ShelfAware MVP Report

## Executive Summary
ShelfAware is an AI-enabled meal recommendation MVP that helps users decide what to cook from ingredients they already have while staying close to personal nutrition goals. The final MVP is implemented as a user-friendly command-line Python application that stores a pantry, searches a recipe dataset of about 20,000 recipes, ranks meals by pantry overlap and nutrition fit, and displays recipe details, missing ingredients, and ingredient pickup suggestions.

Compared with the earlier prototype, this MVP supports a persistent pantry, a much larger recipe search space, flexible nutrition filtering, and more informative outputs. The project focuses on making meal planning more practical for students and busy home cooks who want to reduce food waste, avoid unnecessary grocery trips, and still meet basic nutrition goals.

## User and Use Case
The target user is a student or busy home cook who already has groceries at home but does not know what meals are realistic without buying many additional ingredients. A realistic use case is a student opening ShelfAware after class, entering the items already available in the apartment kitchen, and requesting a high-protein dinner under a calorie target. ShelfAware returns ranked recipes, shows which ingredients are already covered by the pantry, identifies missing items, and allows the user to inspect a recipe’s full ingredients and directions.

In this way, ShelfAware acts as a lightweight recommendation assistant for everyday meal planning. Instead of forcing the user to search through recipes manually, the system narrows the search to meals that are actually feasible given what the user has on hand.

## System Design
The MVP is implemented as a local Python application inside `/mvp/`.

```mermaid
flowchart LR
    A["User pantry input"] --> B["Pantry normalizer"]
    B --> C["Saved user_pantry.json"]
    C --> D["Recommendation engine"]
    E["recipes_dataset.json"] --> D
    D --> F["Ranked recipe list"]
    F --> G["Recipe details"]
    F --> H["Top missing ingredients"]
