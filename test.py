from transformers import pipeline

# Load a small DialoGPT model for text generation
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-small")

print("Chatbot ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chatbot: Goodbye 👋")
        break

    # Generate response
    response = chatbot(user_input, max_length=100, num_return_sequences=1)
    print("Chatbot:", response[0]['generated_text'])

