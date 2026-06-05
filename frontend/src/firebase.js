import { initializeApp } from "firebase/app";
import { getDatabase, ref, onValue } from "firebase/database";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.databaseURL &&
  firebaseConfig.projectId &&
  firebaseConfig.appId
);

const app = isFirebaseConfigured ? initializeApp(firebaseConfig) : null;
const db = app ? getDatabase(app) : null;

// Subscribe to a realtime database path. Returns an unsubscribe function.
export function subscribeSensorStream(path, callback) {
  if (!db) {
    console.warn("Firebase is not configured. Realtime sensor stream disabled.");
    return () => {};
  }

  const databaseRef = ref(db, path);
  const unsubscribe = onValue(databaseRef, (snapshot) => {
    callback(snapshot.val());
  });
  return unsubscribe;
}
