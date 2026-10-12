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
    authDomain: "ai-mern-project-8ada3.firebaseapp.com",
    projectId: "ai-mern-project-8ada3",
    storageBucket: "ai-mern-project-8ada3.firebasestorage.app",
    messagingSenderId: "1031965097551",
    appId: "1:1031965097551:web:5fb162b67512a50753f43a",
    measurementId: "G-QMHVEV2S9H"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const provider = new GoogleAuthProvider()

export { auth, provider }