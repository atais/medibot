// Firebase configuration and FCM setup
let messaging;

// Initialize Firebase after scripts are loaded
function initializeFirebase() {
    const app = firebase.initializeApp(window.firebaseConfig);
    messaging = firebase.messaging();
}

// Register service worker for FCM
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/firebase-messaging-sw.js')
        .then((registration) => {
            console.log('Service Worker registered:', registration);
        })
        .catch((error) => {
            console.error('Service Worker registration failed:', error);
        });
}

// Request permission and get FCM token
async function requestNotificationPermission() {
    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            const token = await messaging.getToken({
                vapidKey: window.vapidKey
            });
            
            if (token) {
                console.log('FCM Token:', token);
                // Send token to your backend
                await registerFCMToken(token);
            }
        } else {
            console.log('Notification permission denied');
        }
    } catch (error) {
        console.error('Error getting FCM token:', error);
    }
}

// Send FCM token to backend
async function registerFCMToken(token) {
    try {
        const response = await fetch('/api/fcm/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: token })
        });
        
        if (response.ok) {
            console.log('FCM token registered successfully');
        } else {
            console.error('Failed to register FCM token');
        }
    } catch (error) {
        console.error('Error registering FCM token:', error);
    }
}

// Handle foreground messages
function setupMessageHandler() {
    messaging.onMessage((payload) => {
        console.log('Message received in foreground:', payload);
        // Display notification to user
        if (payload.notification) {
            new Notification(payload.notification.title, {
                body: payload.notification.body,
                icon: '/favicon.ico'
            });
        }
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for Firebase scripts to load
    setTimeout(() => {
        initializeFirebase();
        setupMessageHandler();
        requestNotificationPermission();
    }, 100);
});
