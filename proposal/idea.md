# ShelfAware

## Team Members
- Sarah Shahidi — seshahid@asu.edu
- Makana Kapoi — mkapoi@asu.edu
- Alex Eiger — aeiger@asu.edu
- Damian Miramontes — dmiramo5@asu.edu

## Problem Statement
ShelfAware is for young, busy, health-conscious people who want to eat well while following strict diet needs such as calorie limits, macro targets, or ingredient restrictions. These users often lose track of what they already have in their pantry, fridge, or freezer, which leads to duplicate purchases, wasted food, and extra stress when trying to plan healthy meals.

Existing tools only solve pieces of this problem. Grocery apps help people shop, recipe apps suggest meals, and chatbots can answer one-time questions, but they do not reliably keep a running pantry inventory that updates over time. This means users still have to repeatedly re-enter what they own whenever they want recipe ideas or a grocery list, which makes healthy, low-waste meal planning inefficient. In our initial market research, we found existing tools that cover parts of this workflow, such as pantry tracking, recipe recommendations, shopping lists, or receipt-based updates. However, the space still feels fragmented: some products focus more on recipes and meal planning, while others focus more on inventory management. Our goal is to unify these pieces into one experience centered on reducing food waste while still helping users meet strict health and diet goals.

## Why Now?
This problem matters in the next 3–5 years because people are becoming more health-conscious, more cost-conscious, and more aware of food waste. Young adults especially want convenient tools that help them eat well without overspending or wasting groceries.

This is more possible now because AI tools have improved at handling messy receipt text, flexible ingredient names, and natural-language requests such as “give me a healthy dinner under 600 calories using what I already have.” Recent progress in OCR (optical character recognition) and lightweight language models makes a pantry-aware assistant more realistic to prototype.

## Proposed AI-Powered Solution
ShelfAware is an AI pantry and meal-planning assistant that keeps a running inventory of what a user has at home. A user can upload a grocery receipt to add items, review extracted foods, and then ask for meal ideas based on what they actually have. The system recommends healthy meals that reduce waste and creates grocery lists with only the missing ingredients.

AI adds value because this is not just a storage problem. Receipt text is messy, food names vary, and users express goals in natural language. A rule-based app could store items, but AI can interpret receipt text, normalize ingredient names, understand diet constraints, and generate more useful low-waste recommendations.

## Initial Technical Concept
ShelfAware would work in three simple steps: read the receipt, update the pantry, and suggest meals. First, the system would extract item names from a grocery receipt. Then it would convert those items into a pantry inventory that the user can review and confirm. After that, the system would use the updated pantry together with the user’s diet goals to suggest meals and create a grocery list of any missing ingredients.

Technically, this could be built using OCR (optical character recognition) to read receipt text, a lightweight AI or language-model component to clean up item names and organize them into pantry items, and a recipe-matching system to compare available ingredients to possible meals. Our nanoGPT work could support the text-generation side of the project, such as turning pantry data and nutrition goals into useful meal suggestions in a simple, user-friendly format.

## Scope for MVP
We will keep the MVP (minimum viable product) narrow and realistic for about 6 weeks.

**A user can upload a grocery receipt and our system returns a pantry inventory update that the user can review and confirm; then, using that updated inventory and the user’s diet goals, the system returns meal ideas that reduce food waste and a grocery list of only the missing ingredients.**

To keep the MVP feasible, we may support only a limited set of receipt formats and require user confirmation before saving inventory changes.

## Risks and Open Questions
1. Receipt text may be inconsistent or difficult to parse accurately.
2. The same ingredient may appear under different names across receipts and recipes.
3. Inventory may become less accurate over time if users do not log what they used.

## Planned Data Sources
We plan to use public recipe datasets from sources such as Kaggle or Hugging Face for ingredient lists and meal examples, and a nutrition source such as USDA FoodData Central for calories and macro information. We also expect to create synthetic pantry examples and sample labeled receipts to test receipt parsing and inventory updates. Because no single dataset is likely to match our exact use case, we will combine public data with small team-created examples and document any preprocessing or assumptions.

## Video Pitch Link
- https://www.youtube.com/watch?v=YrkjZOepj7E
