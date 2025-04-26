// chat.js
const emojis = ["😊", "🤖", "👍", "💡", "🚀", "🔍", "✨", "👋", "🙌"];
const chatBox = document.getElementById("chat-box");
const iaButton = document.getElementById("ia-button");
const sendSound = document.getElementById("send-sound");
const receiveSound = document.getElementById("receive-sound");
const inputField = document.getElementById("user-input");
const messages = document.getElementById("messages");

let welcomed = false; // Variável para controlar se a mensagem de boas-vindas já foi exibida

const toggleChat = () => {
  const isVisible = chatBox.style.display === "flex";
  chatBox.style.display = isVisible ? "none" : "flex";
  iaButton.classList.toggle("open");

  if (!isVisible && !welcomed) {
    inputField.focus();
    setTimeout(() => {
      renderIaMessage("Olá! Eu sou a ISA, sua assistente virtual. Como posso ajudar?");
      welcomed = true; // Marca que a mensagem de boas-vindas foi exibida
    }, 500);
  }
};

inputField.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

const renderIaMessage = (text) => {
  const emoji = emojis[Math.floor(Math.random() * emojis.length)];
  messages.innerHTML += `
    <div class="message ia-message">
      <img src="/static/img/isa-avatar.png" class="ia-avatar" alt="ISA" loading="lazy" />
      <div><strong>ISA:</strong> ${text} ${emoji}</div>
    </div>`;
  scrollToBottom();
  playSound(receiveSound);
};

const renderUserMessage = (text) => {
  messages.innerHTML += `<div class="message user-message"><strong>Você:</strong> ${text}</div>`;
  scrollToBottom();
  playSound(sendSound);
};

const scrollToBottom = () => {
  messages.scrollTop = messages.scrollHeight;
};

const playSound = (audioElement) => {
  if (audioElement) {
    audioElement.pause();
    audioElement.currentTime = 0;
    audioElement.play().catch(() => {});
  }
};

const sendMessage = async (message = null) => {
  const text = message || inputField.value.trim();
  if (!text) return;
  inputField.value = "";

  renderUserMessage(text);

  const typingIndicator = document.createElement("div");
  typingIndicator.className = "message ia-message";
  typingIndicator.id = "typing-indicator";
  typingIndicator.innerHTML = "<strong>ISA:</strong> Digitando...";
  messages.appendChild(typingIndicator);
  scrollToBottom();

  try {
    const response = await fetch("/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ message: text }),
    });

    const data = await response.json();
    typingIndicator.remove();
    renderIaMessage(data.response);
  } catch (error) {
    typingIndicator.remove();
    renderIaMessage("Ocorreu um erro. 😕");
  }
};

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? decodeURIComponent(parts.pop().split(";").shift()) : null;
};