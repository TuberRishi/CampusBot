document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const messagesContainer = document.getElementById("chatbot-messages");

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        // Display user's message
        addMessage(userMessage, "user");
        messageInput.value = "";

        // Show a thinking indicator
        addMessage("...", "bot", true);

        try {
            // Send message to the backend API
            const response = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ query: userMessage, language: "en" }),
            });

            if (!response.ok) {
                throw new Error("API request failed");
            }

            const data = await response.json();

            // Remove thinking indicator and display bot's response
            removeThinkingIndicator();
            addMessage(data.answer, "bot");

        } catch (error) {
            console.error("Error:", error);
            removeThinkingIndicator();
            addMessage("I'm having some trouble connecting. Please try again later.", "bot");
        }
    });

    function addMessage(text, sender, isThinking = false) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", `${sender}-message`);

        if (isThinking) {
            messageDiv.id = "thinking-indicator";
            messageDiv.innerHTML = `<p>...</p>`;
        } else {
            messageDiv.innerHTML = `<p>${text}</p>`;
        }

        messagesContainer.appendChild(messageDiv);
        // Scroll to the bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function removeThinkingIndicator() {
        const thinkingIndicator = document.getElementById("thinking-indicator");
        if (thinkingIndicator) {
            thinkingIndicator.remove();
        }
    }
});
