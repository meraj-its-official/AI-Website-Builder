// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider } from "firebase/auth"
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: "ai-website-builder-fbcfc.firebaseapp.com",
    projectId: "ai-website-builder-fbcfc",
    storageBucket: "ai-website-builder-fbcfc.firebasestorage.app",
    messagingSenderId: "320360943849",
    appId: "1:320360943849:web:ca925f3d0fa879c4692078",
    measurementId: "G-K0TXH45LXG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const provider = new GoogleAuthProvider()

export { auth, provider }