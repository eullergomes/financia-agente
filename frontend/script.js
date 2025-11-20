const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const messagesEl = document.getElementById("messages");
const button = form.querySelector("button");

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  input.focus();

  button.disabled = true;
  button.textContent = "Enviando...";

  try {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      throw new Error("Erro na API");
    }

    const data = await res.json();
    addMessage(data.reply, "bot");
  } catch (err) {
    console.error(err);
    addMessage("Ops, houve um erro ao falar com o servidor. 😥", "bot");
  } finally {
    button.disabled = false;
    button.textContent = "Enviar";
  }
});
