// Firebase configuration and FCM setup
let messaging;

// Initialize Firebase after scripts are loaded
function initializeFirebase() {
    const app = window.firebase.initializeApp(window.firebaseConfig);
    messaging = window.firebase.messaging();
}

// Register service worker for FCM
if ('serviceWorker' in navigator) {
    // SW_FILENAME is injected by the esbuild
    navigator.serviceWorker.register('/' + SW_FILENAME)
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

// Set FCM bell icon status
function setFCMBellStatus(status) {
    const bell = document.getElementById('fcm-bell');
    if (!bell) return;
    if (status === 'success') {
        bell.className = 'bi bi-bell-fill text-success me-3';
    } else {
        bell.className = 'bi bi-bell-slash-fill text-danger me-3';
    }
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
            setFCMBellStatus('error');
        }
    } catch (error) {
        console.error('Error getting FCM token:', error);
        setFCMBellStatus('error');
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
            setFCMBellStatus('success');
        } else {
            console.error('Failed to register FCM token');
            setFCMBellStatus('error');
        }
    } catch (error) {
        console.error('Error registering FCM token:', error);
        setFCMBellStatus('error');
    }
}

// Handle foreground messages
function setupMessageHandler() {
    messaging.onMessage((payload) => {
        console.log('Message received in foreground:', payload);
        // Display notification to user
        let notification = new Notification(payload.data.title, {
            body: payload.data.body,
            icon: '/favicon.ico'
        });
        notification.onclick = function () {
            window.open(payload.data.click_action, '_blank');
        };
    });
}
