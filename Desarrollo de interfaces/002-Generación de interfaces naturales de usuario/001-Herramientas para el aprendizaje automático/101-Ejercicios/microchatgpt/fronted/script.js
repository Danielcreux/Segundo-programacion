class MicroChatGPT {
    constructor() {
        this.backendUrl = 'http://localhost:5000';
        this.context = null;
        this.currentModel = '';
        this.initializeEventListeners();
        this.checkHealth();
        this.loadModels();
    }

    initializeEventListeners() {
        const sendButton = document.getElementById('sendButton');
        const messageInput = document.getElementById('messageInput');
        const refreshButton = document.getElementById('refreshModels');
        const modelSelect = document.getElementById('modelSelect');

        sendButton.addEventListener('click', () => this.sendMessage());
        
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        refreshButton.addEventListener('click', () => this.loadModels());
        modelSelect.addEventListener('change', (e) => {
            this.currentModel = e.target.value;
        });
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.backendUrl}/api/health`);
            const data = await response.json();
            
            const statusElement = document.getElementById('status');
            if (data.ollama_connected) {
                statusElement.innerHTML = '<span class="status-dot"></span><span>Connected to Ollama</span>';
                statusElement.classList.add('connected');
            } else {
                statusElement.innerHTML = '<span class="status-dot"></span><span>Ollama not connected</span>';
                statusElement.classList.remove('connected');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            const statusElement = document.getElementById('status');
            statusElement.innerHTML = '<span class="status-dot"></span><span>Backend not reachable</span>';
            statusElement.classList.remove('connected');
        }
    }

    async loadModels() {
        const modelSelect = document.getElementById('modelSelect');
        
        try {
            const response = await fetch(`${this.backendUrl}/api/models`);
            const data = await response.json();
            
            if (data.models && data.models.length > 0) {
                modelSelect.innerHTML = '';
                data.models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model;
                    option.textContent = model;
                    modelSelect.appendChild(option);
                });
                this.currentModel = data.models[0];
            } else {
                modelSelect.innerHTML = '<option value="">No models found</option>';
            }
        } catch (error) {
            console.error('Failed to load models:', error);
            modelSelect.innerHTML = '<option value="">Error loading models</option>';
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const message = messageInput.value.trim();

        if (!message) return;

        // Clear input and disable send button
        messageInput.value = '';
        sendButton.disabled = true;

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.backendUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    model: this.currentModel,
                    context: this.context
                })
            });

            const data = await response.json();

            // Remove typing indicator
            this.hideTypingIndicator();

            if (data.success) {
                this.addMessage(data.response, 'bot');
                this.context = data.context;
            } else {
                this.addMessage(`Error: ${data.response}`, 'bot');
            }
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Error: Could not connect to the server', 'bot');
            console.error('Error sending message:', error);
        } finally {
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    addMessage(content, sender) {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? '👤' : '🤖';

        const contentElement = document.createElement('div');
        contentElement.className = 'content';
        contentElement.textContent = content;

        messageElement.appendChild(avatar);
        messageElement.appendChild(contentElement);
        messagesContainer.appendChild(messageElement);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('messages');
        const typingElement = document.createElement('div');
        typingElement.className = 'message bot-message';
        typingElement.id = 'typing-indicator';

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = '🤖';

        const contentElement = document.createElement('div');
        contentElement.className = 'content typing-indicator';
        contentElement.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;

        typingElement.appendChild(avatar);
        typingElement.appendChild(contentElement);
        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MicroChatGPT();
});