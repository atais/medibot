// Firebase configuration (externalized)
// This file is shared between main app and service worker
const firebaseConfig = {
    apiKey: "AIzaSyBvcV3PSz5MPmT79h30QzhSdQ1I87RPbSs",
    authDomain: "medi-fd6b8.firebaseapp.com",
    projectId: "medi-fd6b8",
    storageBucket: "medi-fd6b8.firebasestorage.app",
    messagingSenderId: "691901736893",
    appId: "1:691901736893:web:9f7e08b853bb03668754d4"
};

// Make config available globally for both main app and service worker
if (typeof window !== 'undefined') {
    // Main app context
    window.firebaseConfig = firebaseConfig;
}
if (typeof self !== 'undefined') {
    // Service worker context
    self.firebaseConfig = firebaseConfig;
}
