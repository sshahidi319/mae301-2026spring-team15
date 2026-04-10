import torch
from model import NanoGPT

# 1. Setup
device = 'cuda' if torch.cuda.is_available() else 'cpu'
with open('input.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 2. Recreate the exact same vocabulary/tokenizer
chars = sorted(list(set(text)))
vocab_size = len(chars)
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }
encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])

# 3. Load the model
model = NanoGPT(vocab_size)
model.load_state_dict(torch.load('model_ckpt.pt', map_location=device))
model.to(device)
model.eval() # Set to evaluation mode

# 4. Generate text!
# Let's prompt it with the start of a title
prompt = "[TITLE]:"
context = torch.tensor((encode(prompt)), dtype=torch.long, device=device).unsqueeze(0)

print("Generating recipe...\n" + "="*20)
# Generate 500 new characters
generated_indices = model.generate(context, max_new_tokens=500)[0].tolist()
print(decode(generated_indices))
