// Get references to the HTML elements we will be interacting with
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');

// The URL of our FastAPI backend's /ask endpoint
const API_URL = 'http://127.0.0.1:8000/ask';

/**
 * Appends a message to the chat window.
 * @param {string} message - The text content of the message.
 * @param {string} sender - The sender of the message ('user' or 'bot').
 */
function appendMessage(message, sender) {
    // Create a new div element for the message
    const messageElement = document.createElement('div');
    // Add the base 'message' class and a sender-specific class ('user-message' or 'bot-message')
    messageElement.classList.add('message', `${sender}-message`);
    
    // Create a p element to hold the message text
    const textElement = document.createElement('p');
    textElement.textContent = message;
    
    // Add the text to the message element
    messageElement.appendChild(textElement);
    
    // Add the complete message element to the chat window
    chatMessages.appendChild(messageElement);
    
    // Automatically scroll to the bottom to show the latest message
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Shows or hides the "Bot is typing..." indicator.
 * @param {boolean} show - If true, shows the indicator; otherwise, hides it.
 */
function showTypingIndicator(show) {
    let indicator = document.getElementById('typing-indicator');
    if (show) {
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'typing-indicator';
            indicator.classList.add('message', 'bot-message', 'typing-indicator');
            indicator.innerHTML = '<span></span><span></span><span></span>';
            chatMessages.appendChild(indicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    } else {
        if (indicator) {
            indicator.remove();
        }
    }
}

// Add an event listener for the form submission
chatForm.addEventListener('submit', async (event) => {
    // Prevent the default form behavior (which is to reload the page)
    event.preventDefault();
    
    // Get the user's query from the input field, trimming whitespace
    const query = userInput.value.trim();
    
    // If the query is empty, do nothing
    if (!query) return;
    
    // Display the user's message in the chat window
    appendMessage(query, 'user');
    
    // Clear the input field for the next message
    userInput.value = '';
    
    // Show the typing indicator while we wait for the response
    showTypingIndicator(true);
    
    try {
        // Send the user's query to the FastAPI backend
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }), // The request body must match our AskRequest model
        });
        
        // Hide the typing indicator now that we have a response
        showTypingIndicator(false);
        
        if (!response.ok) {
            // If the server returned an error, display a generic error message
            appendMessage('Sorry, something went wrong. Please try again.', 'bot');
            console.error('API Error:', response.status, await response.text());
            return;
        }
        
        // Parse the JSON response from the server
        const data = await response.json();
        
        // Display the bot's answer in the chat window
        appendMessage(data.answer, 'bot');
        
    } catch (error) {
        // Handle network errors or other issues with the fetch call
        showTypingIndicator(false);
        appendMessage('Sorry, I couldn\'t connect to the server. Please check if it\'s running.', 'bot');
        console.error('Fetch Error:', error);
    }
});
