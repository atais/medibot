// Firebase Messaging Service Worker
importScripts('https://www.gstatic.com/firebasejs/12.2.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.2.1/firebase-messaging-compat.js');

// Initialize Firebase in service worker
firebase.initializeApp({
    apiKey: "AIzaSyBvcV3PSz5MPmT79h30QzhSdQ1I87RPbSs",
    authDomain: "medi-fd6b8.firebaseapp.com",
    projectId: "medi-fd6b8",
    storageBucket: "medi-fd6b8.firebasestorage.app",
    messagingSenderId: "691901736893",
    appId: "1:691901736893:web:9f7e08b853bb03668754d4"
});

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
    console.log('Background message received:', payload);

    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/favicon.ico',
        data: payload.data // Attach data for click_action
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click to support click_action
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    let clickAction = '/';
    if (event.notification.data && event.notification.data.click_action) {
        clickAction = event.notification.data.click_action;
    }
    event.waitUntil(
        clients.openWindow(clickAction)
    );
});
