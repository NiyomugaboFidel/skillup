document.addEventListener('DOMContentLoaded', function() {
    const threadContainer = document.getElementById('thread-messages-container');
    const messageForm = document.getElementById('message-form');
    
    if (threadContainer) {
        const threadId = threadContainer.dataset.threadId;
        
        // Connect to WebSocket
        const messageSocket = new WebSocket(
            (window.location.protocol === 'https:' ? 'wss://' : 'ws://') +
            window.location.host +
            `/ws/messages/${threadId}/`
        );
        
        messageSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            if (data.type === 'chat_message') {
                // Add message to thread
                addMessage(data.message);
                
                // Scroll to bottom
                threadContainer.scrollTop = threadContainer.scrollHeight;
            }
        };
        
        messageSocket.onclose = function(e) {
            console.error('Message socket closed unexpectedly');
        };
        
        // Handle message form submission
        if (messageForm) {
            messageForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                const messageInput = document.getElementById('id_content');
                const message = messageInput.value.trim();
                
                if (message) {
                    // Send message to WebSocket
                    messageSocket.send(JSON.stringify({
                        'message': message
                    }));
                    
                    // Clear input
                    messageInput.value = '';
                }
            });
        }
        
        // Function to add message to thread
        function addMessage(message) {
            const currentUserId = document.body.dataset.userId;
            const isOwnMessage = message.sender_id.toString() === currentUserId;
            
            const messageItem = document.createElement('div');
            messageItem.className = isOwnMessage 
                ? 'flex justify-end mb-4' 
                : 'flex mb-4';
            
            messageItem.innerHTML = `
                <div class="${isOwnMessage ? 'ml-auto' : 'mr-auto'} flex ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'}">
                    <img src="${message.sender_avatar}" alt="${message.sender_username}" class="w-10 h-10 rounded-full ${isOwnMessage ? 'ml-3' : 'mr-3'}">
                    <div>
                        <div class="flex items-center ${isOwnMessage ? 'justify-end' : ''}">
                            <span class="font-bold">${message.sender_username}</span>
                            <span class="twitter-text-light text-xs ml-2">${message.timestamp_formatted}</span>
                        </div>
                        <div class="mt-1 p-3 rounded-lg ${isOwnMessage ? 'bg-blue-500 text-white' : 'bg-gray-800'}">
                            ${message.content}
                        </div>
                    </div>
                </div>
            `;
            
            threadContainer.appendChild(messageItem);
        }
        
        // Scroll to bottom on load
        threadContainer.scrollTop = threadContainer.scrollHeight;
    }
});