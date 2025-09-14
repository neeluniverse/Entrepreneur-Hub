let currentRecipientId = null;
let pollInterval = null;

document.querySelectorAll('.contact-item').forEach(item => {
    item.addEventListener('click', function() {
        const userId = this.dataset.userId;
        loadConversation(userId);
    });
});

document.getElementById('send-message-btn').addEventListener('click', sendMessage);

function loadConversation(userId) {
    currentRecipientId = userId;
    document.getElementById('no-conversation').classList.add('d-none');
    document.getElementById('conversation').classList.remove('d-none');
    
    fetch(`/messages/${userId}`)
        .then(response => response.json())
        .then(data => {
            const messagesContainer = document.getElementById('messages');
            messagesContainer.innerHTML = '';
            data.messages.forEach(msg => {
                addMessageToContainer(msg, msg.sender_id == currentUserId);
            });
            scrollToBottom();
            startPolling();
        });
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (content && currentRecipientId) {
        fetch(`/send_message/${currentRecipientId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                addMessageToContainer(data.message, true);
                input.value = '';
                scrollToBottom();
            }
        });
    }
}

function addMessageToContainer(message, isSent) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isSent ? 'message-sent' : 'message-received'}`;
    messageDiv.textContent = message.content;
    messagesContainer.appendChild(messageDiv);
}

function scrollToBottom() {
    const container = document.getElementById('messages-container');
    container.scrollTop = container.scrollHeight;
}

function startPolling() {
    stopPolling();
    pollInterval = setInterval(() => {
        if (currentRecipientId) {
            fetch(`/messages/${currentRecipientId}`)
                .then(response => response.json())
                .then(data => {
                    const messagesContainer = document.getElementById('messages');
                    const currentMessageCount = messagesContainer.children.length;
                    if (data.messages.length > currentMessageCount) {
                        for (let i = currentMessageCount; i < data.messages.length; i++) {
                            const msg = data.messages[i];
                            addMessageToContainer(msg, msg.sender_id == currentUserId);
                        }
                        scrollToBottom();
                    }
                });
        }
    }, 3000);
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
}

// Global variables (would be set in base template)
const currentUserId = {{ current_user.id if current_user.is_authenticated else 'null' }};
const currentUserName = '{{ current_user.name if current_user.is_authenticated }}';
const currentUserAvatar = '{{ current_user.avatar_url or "https://via.placeholder.com/30" }}';
