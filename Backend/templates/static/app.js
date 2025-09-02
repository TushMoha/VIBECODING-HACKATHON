// Simple client helpers
(function () {
  // Persist a lightweight user id
  if (!localStorage.getItem("mm_user")) {
    localStorage.setItem("mm_user", "user_" + Math.random().toString(36).slice(2, 8));
  }

  const log = document.getElementById("chat-log");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const btn = document.getElementById("send-btn");
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  function addMsg(role, text) {
    const wrap = document.createElement("div");
    wrap.className = `msg ${role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    const label = document.createElement("div");
    label.className = "label";
    label.textContent = role === "me" ? "You" : "Mazingira Mind";
    const body = document.createElement("div");
    body.textContent = text;
    bubble.appendChild(label);
    bubble.appendChild(body);
    wrap.appendChild(bubble);
    log.appendChild(wrap);
    log.scrollTop = log.scrollHeight;
  }

  function setLoading(loading) {
    input.disabled = loading;
    btn.disabled = loading;
    btn.textContent = loading ? "Sending…" : "Send";
  }

  async function sendMessage(text) {
    setLoading(true);
    addMsg("me", text);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ message: text, user_id: localStorage.getItem("mm_user") })
      });
      const data = await res.json();
      const reply = data.message || "I'm here to listen — tell me more.";
      addMsg("bot", reply);
    } catch (e) {
      addMsg("bot", "Sorry, I couldn't reach the server. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (form && input) {
    // ENTER to send, Shift+Enter for newline
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const text = input.value.trim();
        if (text) {
          input.value = "";
          sendMessage(text);
        }
      }
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      input.value = "";
      sendMessage(text);
    });
  }
})();
