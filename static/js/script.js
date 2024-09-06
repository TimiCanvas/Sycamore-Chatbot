document.addEventListener("DOMContentLoaded", () => {
    const sendButton = document.getElementById("send-button");
    const userMessageInput = document.getElementById("user-message");
    const chatOutput = document.getElementById("chat-output");

    sendButton.addEventListener("click", sendMessage);
    userMessageInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Function to send an introductory message
    function sendIntroductoryMessage() {
        const introMessage = "Hi, my name is John, I am a customer service agent for GNA, how may I help you today?";
        addMessageToChat(introMessage, "bot-message");
    }

    // Sends the introductory message when the page loads
    sendIntroductoryMessage();

    function sendMessage() {
        const userMessage = userMessageInput.value.trim();
        if (userMessage === "") {
            return;
        }

        // Adds user message to chat
        addMessageToChat(userMessage, "user-message");
        userMessageInput.value = "";

        // Sends message to the Flask server
        fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addMessageToChat(data.error, "bot-message");
            } else {
                addMessageToChat(data.response, "bot-message");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            addMessageToChat("Sorry, I'm having trouble processing your request at the moment.", "bot-message");
        });
    }

    function addMessageToChat(message, className) {
        const messageElement = document.createElement("div");
        messageElement.className = className;
        messageElement.textContent = message;
        chatOutput.appendChild(messageElement);
        chatOutput.scrollTop = chatOutput.scrollHeight; // Scrolls to the bottom
    }
});
