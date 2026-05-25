/* BHEL SAP Portal — main.js */

// ── Sidebar toggle (mobile) ───────────────────────
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebarOverlay').classList.toggle('show');
}

// ── SAP AI CHATBOT ───────────────────────────────

function toggleChatbot() {

  document
    .getElementById('sapChatWindow')
    .classList
    .toggle('d-none');
}


// Enter key support
function handleChatEnter(event) {

  if(event.key === 'Enter') {
    sendChatMessage();
  }
}


// Send Message
async function sendChatMessage() {

  const input = document.getElementById('sapChatInput');

  const message = input.value.trim();

  if(!message) return;

  const messagesDiv = document.getElementById('sapChatMessages');


  // ── User Message ──
  messagesDiv.innerHTML += `
    <div class="user-message">
      ${message}
    </div>
  `;

  input.value = '';


  // ── Typing Indicator ──
  const typingId = 'typing-' + Date.now();

  messagesDiv.innerHTML += `
    <div class="typing-message" id="${typingId}">
      SAP AI is typing...
    </div>
  `;

  messagesDiv.scrollTop = messagesDiv.scrollHeight;


  try {

    const response = await fetch(
      `/chatbot/chat/?message=${encodeURIComponent(message)}`
    );

    const data = await response.json();

    document.getElementById(typingId)?.remove();


    // ── Source Badge ──
    const sourceBadge =
      data.source === 'database'
      ? '📘 Internal SAP'
      : '🤖 Ollama AI';


    // ── Bot Response ──
    messagesDiv.innerHTML += `
      <div class="bot-message">
        ${data.answer}

        <div class="chat-source">
          ${sourceBadge}
        </div>
      </div>
    `;

  }

  catch(error){

    document.getElementById(typingId)?.remove();

    messagesDiv.innerHTML += `
      <div class="bot-message">
        Unable to connect to SAP AI Assistant.
      </div>
    `;
  }


  // Auto-scroll
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Close popup on outside click
document.addEventListener('click', e => {
  const modal = document.getElementById('tcodeModal');
  const fab = document.querySelector('.tcode-fab');
  if (modal && !modal.classList.contains('d-none')
      && !modal.contains(e.target) && fab && !fab.contains(e.target)) {
    closeTcode();
  }
});

// ── Auto-dismiss alerts ───────────────────────────
document.querySelectorAll('.alert').forEach(a => {
  setTimeout(() => { try { bootstrap.Alert.getOrCreateInstance(a).close(); } catch(e){} }, 4000);
});