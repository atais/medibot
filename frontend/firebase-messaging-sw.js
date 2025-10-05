// Firebase Messaging Service Worker
import firebase from 'firebase/compat/app';
import 'firebase/compat/messaging';
import './firebase-config.js';

// Initialize Firebase in service worker
firebase.initializeApp(self.firebaseConfig);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Background message received:', payload);

    const notificationTitle = payload.data.title;
    const notificationOptions = {
        body: payload.data.body,
        icon: '/favicon.ico',
        data: payload.data // Attach data for click_action
    };

    return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle push event for data-only FCM messages (required for Android Chrome)
self.addEventListener('push', event => {
    let payload = event.data.json();
    console.log('Push event received:', payload);

    const notificationTitle = payload.data.title;
    const notificationOptions = {
        body: payload.data.body,
        icon: '/favicon.ico',
        data: payload.data
    };

    return event.waitUntil(self.registration.showNotification(notificationTitle, notificationOptions));
});

// Handle notification click to support click_action
self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.click_action)
    );
});
