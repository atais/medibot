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
            // Initialize Firebase and request permission only after registration
            initializeFirebase();
            setupMessageHandler();
            requestNotificationPermission(registration);
        })
        .catch((error) => {
            console.error('Service Worker registration failed:', error);
        });
} else {
    console.warn('Service workers are not supported in this browser.');
}

// Request permission and get FCM token
async function requestNotificationPermission(registration) {
    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            if (!registration) {
                console.error('Service worker registration is undefined. Cannot get FCM token.');
                return;
            }
            const token = await messaging.getToken({
                vapidKey: window.vapidKey,
                serviceWorkerRegistration: registration
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
            body: JSON.stringify({token: token})
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
        // Only show notification in foreground if payload.notification is missing
        if (!payload.notification && payload.data) {
            new Notification(payload.data.title || 'Notification', {
                body: payload.data.body || '',
                icon: '/favicon.ico'
            });
        }
        // If payload.notification exists, do not show manually; let Android system handle background notifications
    });
}
