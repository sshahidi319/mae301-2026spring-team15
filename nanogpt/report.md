Phase 2 Progress Report: ShelfAware
Team Members: Sarah Shahidi, Makana Kapoi, Alex Eiger, Damian Miramontes

1. Objective and Current MVP Definition
Objective: ShelfAware is an AI pantry and meal-planning assistant designed for health-conscious, busy young adults to reduce food waste and meet strict dietary goals by tracking inventory from grocery receipts.


Current MVP Definition: A user can upload a grocery receipt, and our system returns a parsed, updated pantry inventory that the user can review and confirm. Using that updated inventory and the user’s diet goals, the system returns meal ideas that reduce food waste and generates a grocery list of only the missing ingredients.

2. What Has Been Built So Far
We have made substantial progress on both the core AI workflow and an optional technical exploration:

Data & Normalization Pipeline: We have begun testing the workflow required to extract raw text from receipts and use an LLM to normalize messy text (e.g., "ORG FUJI APL") into clean ingredient names.

Recipe Matching Logic: We have sourced initial recipe formats and are designing the logic to compare a user's pantry inventory against required ingredients.


Optional nanoGPT Side Quest: We successfully built and trained a custom NanoGPT model from scratch using PyTorch. We implemented a multi-head self-attention architecture (model.py), set up a training loop (train.py), and created a small custom dataset of recipes (input.txt).


What does NOT work yet: The end-to-end pipeline is not fully integrated. Currently, the OCR extraction, inventory normalization, and the nanoGPT model run as isolated scripts. Additionally, our custom recipe dataset is currently too small to generalize effectively.

3. Technical Approach (Agent Workflow & Generative Exploration)
Our project combines an Agent/Workflow approach for the core application with a Generative modeling exploration.


Agent Workflow (Pantry Normalization): A raw, general-purpose AI struggles with this task if prompted blindly—it tends to hallucinate inventory items or misunderstand abbreviated receipt text. To address this, our architecture breaks the task into a multi-step workflow: OCR extraction, followed by a strictly prompted LLM that normalizes the text into a structured JSON pantry list.

Generative Model (nanoGPT): To better understand how AI generates recipe instructions, we built a custom transformer model. The model features 4 attention heads, 4 layers, and an embedding size of 128. It tokenizes character-by-character to predict the next character in a recipe sequence.

4. Evidence of Progress
A. Normalization & Matching Logic:
(Note: We are actively transitioning from baseline general-purpose AI prompts to our structured multi-step workflow. Initial manual testing shows that enforcing JSON outputs prevents the AI from hallucinating items not present on the receipt).

B. nanoGPT Training Logs:
We successfully trained our custom NanoGPT model on a small batch of recipes (input.txt). During development, we identified and fixed a critical bug in our multi-head attention module (correcting a typo in the PyTorch dropout layer definition).

Training Setup: 2000 iterations, batch size of 32, learning rate of 1e-3.


Results: We successfully demonstrated the model learning the character distributions, with the validation loss steadily decreasing and the model saving its state to model_ckpt.pt. We also implemented a generate.py script to sample novel text from the trained checkpoint.

5. Current Limitations and Open Risks
nanoGPT Dataset Size: Our current input.txt contains only 4 recipes. Because the dataset is so small, training for 2000 iterations causes the model to overfit and memorize the text rather than learning general recipe structures.

Data Inconsistency: The same ingredient may appear under different names across receipts and recipes (e.g., "spaghetti" vs. "pasta").

Inventory Drift: Users may forget to log when they consume an item, leading to an inaccurate pantry state over time.

OCR Reliability: Parsing accuracy heavily depends on the physical quality of the receipt and the lighting in the photo.

6. Plan for Phase 3
To complete our MVP by April 27, our next steps are:


Dataset Expansion: Scrape or download a much larger open dataset of recipes (e.g., from Kaggle or Hugging Face)  to properly train our generative component and fuel our matching logic.

System Integration: Combine the OCR extraction, inventory normalization, and recipe matching into a single cohesive Python pipeline.


User Interface: Build a simple web UI (e.g., using Streamlit) where a user can upload a receipt, confirm their pantry updates, and receive recipe suggestions.

Nutrition Integration: Incorporate macro and calorie tracking (potentially via the USDA FoodData Central database) to satisfy the dietary constraints outlined in our problem statement.

Appendix: nanoGPT Technical Details

This section fulfills the optional nanoGPT side quest exploration.

Architecture Overview:

Model: Character-level NanoGPT (model.py)

Parameters: n_embd = 128, n_head = 4, n_layer = 4, dropout = 0.2, block_size = 64.

Files Included in /phase2/: model.py, train.py, generate.py, and input.txt.
