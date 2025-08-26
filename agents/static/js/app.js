document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const chatMessages = document.getElementById('chatMessages');
    const sendButton = document.getElementById('sendButton');
    const clearButton = document.getElementById('clearButton');
    const exportButton = document.getElementById('exportButton');

    // Handle form submission
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        
        // Disable send button and show typing indicator
        sendButton.disabled = true;
        sendButton.innerHTML = '<span>Sending...</span>';
        addTypingIndicator();

        try {
            // Send message to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `message=${encodeURIComponent(message)}`
            });

            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add assistant response
            addMessage(data.response, 'assistant');
            
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }

        // Re-enable send button
        sendButton.disabled = false;
        sendButton.innerHTML = '<span>Send</span>';
        
        // Scroll to bottom
        scrollToBottom();
    });

    // Add message to chat
    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        
        messageContent.appendChild(paragraph);
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
    }

    // Add typing indicator
    function addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typingIndicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'message-content typing-indicator';
        
        typingContent.innerHTML = `
            <span>Agent is typing</span>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        typingDiv.appendChild(typingContent);
        chatMessages.appendChild(typingDiv);
    }

    // Remove typing indicator
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Scroll to bottom of chat
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Clear chat history
    clearButton.addEventListener('click', async function() {
        try {
            await fetch('/clear', { method: 'POST' });
            chatMessages.innerHTML = `
                <div class="message system">
                    <div class="message-content">
                        <p>Chat history cleared. Hello! I'm your AI agent. Ask me anything and I'll do my best to help!</p>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    });

    // Export chat history
    exportButton.addEventListener('click', async function() {
        try {
            const response = await fetch('/history');
            const data = await response.json();
            
            const chatHistory = data.history.map(msg => 
                `${msg.role}: ${msg.content}`
            ).join('\n\n');
            
            const blob = new Blob([chatHistory], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'chat_history.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
        } catch (error) {
            console.error('Error exporting chat:', error);
        }
    });

    // Handle Enter key in input
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Auto-focus input on page load
    messageInput.focus();
});
