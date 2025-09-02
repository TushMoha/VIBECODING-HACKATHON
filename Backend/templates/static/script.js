async function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (message === "") return;

  // Display user message
  appendMessage("You", message);
  input.value = "";

  try {
    // Send message to backend
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    appendMessage("Bot", data.response);
  } catch (error) {
    appendMessage("Bot", "⚠️ Error: Could not connect to server.");
  }
}

function appendMessage(sender, message) {
  const chatBox = document.getElementById("chat-box");
  const msgDiv = document.createElement("div");
  msgDiv.className = sender.toLowerCase();
  msgDiv.textContent = `${sender}: ${message}`;
  chatBox.appendChild(msgDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Allow pressing Enter to send
document.getElementById("user-input").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});
