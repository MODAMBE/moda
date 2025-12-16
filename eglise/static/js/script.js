// === script.js ===
// Gestion du chat WebSocket en temps réel

document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-messages");
    const messageInput = document.getElementById("message-input");
    const messageForm = document.getElementById("message-form");

    if (!chatBox || !messageForm) return;

    // Récupère l’ID de la discussion à partir de l’URL
    const pathParts = window.location.pathname.split("/");
    const discussionId = pathParts[pathParts.length - 2];

    // Crée la connexion WebSocket
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
    const chatSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/discussion/${discussionId}/`);

    chatSocket.onopen = function () {
        console.log("✅ WebSocket connecté :", discussionId);
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.message) {
            const messageElement = document.createElement("div");
            messageElement.className = "message";
            messageElement.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
            chatBox.appendChild(messageElement);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    };

    chatSocket.onclose = function () {
        console.log("⚠️ WebSocket fermé");
    };

    messageForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message.length === 0) return;

        chatSocket.send(JSON.stringify({ message: message }));
        messageInput.value = "";
    });
});
