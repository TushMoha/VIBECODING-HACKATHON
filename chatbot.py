from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load DialoGPT-small model
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

print("Chatbot is ready! Type 'exit' to quit.\n")

# Chat loop
chat_history_ids = None
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Exiting chat. Goodbye!")
        break

    # Encode input and append chat history
    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")
    bot_input_ids = torch.cat([chat_history_ids, new_input_ids], dim=-1) if chat_history_ids is not None else new_input_ids

    # Generate response
    chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    bot_output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

    print(f"Bot: {bot_output}")

