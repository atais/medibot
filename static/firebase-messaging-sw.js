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
        icon: '/favicon.ico'
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});
