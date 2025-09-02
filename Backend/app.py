from flask import Flask, render_template, request, jsonify
import logging

app = Flask(__name__)

# ---------------------------
# Simple Chatbot Intelligence
# ---------------------------
class SmartMentalHealthChatbot:
    def __init__(self):
        logging.info("SmartMentalHealthChatbot initialized with HuggingFace models.")

    def get_response(self, user_message: str) -> str:
        # Very basic AI logic (placeholder – can be replaced with HuggingFace/OpenAI)
        user_message = user_message.lower()
        if "stress" in user_message:
            return "I'm sorry you're feeling stressed. Remember to take deep breaths and rest when you can. 🌱"
        elif "crisis" in user_message:
            return "If you’re in a crisis, please reach out to a trusted friend, family member, or a professional immediately. 💙"
        elif "hello" in user_message or "hi" in user_message:
            return "Hello! 👋 I'm here to support you. How are you feeling today?"
        else:
            return "I hear you. Please tell me more so I can support you better."

chatbot = SmartMentalHealthChatbot()

# ---------------------------
# Routes for Pages
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html")  # ✅ Root goes to home.html

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/materials")
def materials():
    return render_template("materials.html")

@app.route("/payments")
def payments():
    return render_template("payments.html")

# ---------------------------
# Chatbot API
# ---------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    logging.info(f"User: {user_message}")
    response = chatbot.get_response(user_message)
    return jsonify({"response": response})

# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("🧠 Mazingira Mind Enhanced Chatbot starting...")
    app.run(host="0.0.0.0", port=5000, debug=True)
