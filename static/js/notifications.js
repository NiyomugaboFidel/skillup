// static/js/notifications.js
document.addEventListener('DOMContentLoaded', function() {
    const notificationSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/notifications/'
    );

    notificationSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        
        if (data.type === 'notification') {
            // Handle new notification
            const notification = data.notification;
            showNotification(notification);
        } else if (data.type === 'unread_count') {
            // Update badge counter
            updateNotificationCounter(data.count);
        }
    };

    notificationSocket.onclose = function(e) {
        console.error('Notification socket closed unexpectedly');
    };

    function showNotification(notification) {
        // Display a toast/notification
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        
        let content = `
            <div class="notification-toast-content">
                <img src="${notification.sender_avatar}" alt="${notification.sender}" class="notification-avatar">
                <div class="notification-text">
                    <p><strong>${notification.sender}</strong> `;
        
        if (notification.type === 'like') {
            content += `liked your post`;
        } else if (notification.type === 'comment') {
            content += `commented on your post`;
        } else if (notification.type === 'follow') {
            content += `started following you`;
        } else if (notification.type === 'message') {
            content += `sent you a message`;
        }
        
        content += `</p>
                    <span class="notification-time">${notification.created_at}</span>
                </div>
            </div>`;
        
        toast.innerHTML = content;
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => {
                toast.remove();
            }, 500);
        }, 5000);
    }

    function updateNotificationCounter(count) {
        const counter = document.getElementById('notification-counter');
        if (counter) {
            if (count > 0) {
                counter.textContent = count;
                counter.style.display = 'block';
            } else {
                counter.style.display = 'none';
            }
        }
    }
});