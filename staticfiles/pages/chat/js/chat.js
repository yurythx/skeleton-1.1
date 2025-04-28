const emojis = ["😊", "🤖", "👍", "💡", "🚀", "🔍", "✨", "👋", "🙌"];
const chatBox = document.getElementById("chat-box");
const iaButton = document.getElementById("ia-button");
const sendSound = document.getElementById("send-sound");
const receiveSound = document.getElementById("receive-sound");
const inputField = document.getElementById("user-input");
const messages = document.getElementById("messages");
const minimizeBtn = document.getElementById("minimize-btn");
const closeBtn = document.getElementById("close-btn");
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.accept = 'image/*,.pdf,.doc,.docx,.txt';

let welcomed = false;
let sessionId = null;

const toggleChat = () => {
  if (chatBox.style.display === "flex") {
    minimizeChat();
  } else {
    chatBox.style.display = "flex";
    setTimeout(() => {
      chatBox.style.opacity = 1;
      inputField.focus();
    }, 10);
  }
};

iaButton.addEventListener("click", toggleChat);
minimizeBtn.addEventListener("click", minimizeChat);
closeBtn.addEventListener("click", closeChat);

inputField.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendMessage();
  }
});

const renderIaMessage = (text) => {
  const emoji = emojis[Math.floor(Math.random() * emojis.length)];
  messages.innerHTML += `
    <div class="message bot">
      <img src="${window.chatbotConfig.avatarUrl}" class="ia-avatar" alt="ISA" />
      <div class="message-content"><strong>ISA:</strong> ${text} ${emoji}</div>
    </div>`;
  scrollToBottom();
  playSound(receiveSound);
};

const renderUserMessage = (text) => {
  messages.innerHTML += `
    <div class="message user">
      <div class="message-content"><strong>Você:</strong> ${text}</div>
    </div>`;
  scrollToBottom();
  playSound(sendSound);
};

const scrollToBottom = () => {
  messages.scrollTop = messages.scrollHeight;
};

const playSound = (audio) => {
  if (audio) {
    audio.pause();
    audio.currentTime = 0;
    audio.play().catch(() => {});
  }
};

const sendMessage = async () => {
  const message = inputField.value.trim();
  if (message === "") return;

  renderUserMessage(message);
  inputField.value = "";
  showTypingIndicator();

  const url = `${window.chatbotConfig.apiUrl}?message=${encodeURIComponent(message)}${sessionId ? `&session_id=${sessionId}` : ""}`;
  
  try {
    const response = await fetch(url, {
      method: "GET",
    });

    const data = await response.json();
    removeTypingIndicator();
    
    if (data.status === 'success') {
      renderIaMessage(data.response);
      if (data.session_id) {
        sessionId = data.session_id;
      }
    } else {
      renderIaMessage(data.error || 'Desculpe, ocorreu um erro ao processar sua mensagem.');
    }
  } catch (error) {
    removeTypingIndicator();
    renderIaMessage("Desculpe, ocorreu um erro ao processar sua mensagem.");
    console.error("Erro:", error);
  }

  inputField.focus();
};

const minimizeChat = () => {
  chatBox.style.opacity = 0;
  setTimeout(() => {
    chatBox.style.display = "none";
  }, 300);
};

const closeChat = () => {
  minimizeChat();
  messages.innerHTML = "";
  welcomed = false;
  iaButton.classList.remove("open");
  sessionId = null;
};

function showTypingIndicator() {
  const div = document.createElement('div');
  div.className = 'message bot';
  div.innerHTML = `
    <img src="${window.chatbotConfig.avatarUrl}" alt="ISA" class="ia-avatar">
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  div.id = 'typingIndicator';
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) {
    indicator.remove();
  }
}

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? decodeURIComponent(parts.pop().split(";").shift()) : null;
};

function appendMessage(text, sender, hasMedia = false, mediaUrl = null) {
  const div = document.createElement('div');
  div.className = `message ${sender}`;
  
  if (sender === 'bot') {
    const avatar = document.createElement('img');
    avatar.src = '/static/img/isa-avatar.png';
    avatar.alt = 'ISA';
    avatar.className = 'ia-avatar';
    div.appendChild(avatar);
  }
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.textContent = text;
  
  div.appendChild(contentDiv);
  
  if (hasMedia && mediaUrl) {
    const img = document.createElement('img');
    img.src = mediaUrl;
    img.className = 'message-media';
    div.appendChild(img);
  }
  
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function handleFileUpload(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  fetch('/ia/upload/', {
    method: 'POST',
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      appendMessage('Arquivo enviado com sucesso!', 'user', true, data.url);
      sendMessage(`Enviei um arquivo: ${file.name}`);
    } else {
      appendMessage('Erro ao enviar arquivo.', 'user');
    }
  })
  .catch(error => {
    console.error('Erro:', error);
    appendMessage('Erro ao enviar arquivo.', 'user');
  });
}

// Eventos para upload de arquivos
document.querySelector('.action-btn[title="Anexar arquivo"]').addEventListener('click', () => {
  fileInput.click();
});

document.querySelector('.action-btn[title="Enviar imagem"]').addEventListener('click', () => {
  fileInput.accept = 'image/*';
  fileInput.click();
});

fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    handleFileUpload(file);
  }
  fileInput.value = ''; // Limpa o input para permitir selecionar o mesmo arquivo novamente
});