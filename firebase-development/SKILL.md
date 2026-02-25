---
name: firebase-development
description: Firebase development covering Firestore CRUD and queries, Firebase Authentication with social providers, Cloud Storage file uploads, Cloud Functions triggers, Firebase Hosting, security rules, real-time listeners, offline persistence, and Firebase Admin SDK for server-side operations.
---

# Firebase Development

This skill should be used when building applications with Firebase. It covers Firestore, Authentication, Cloud Storage, Cloud Functions, hosting, and security rules.

## When to Use This Skill

Use this skill when you need to:

- Build real-time applications with Firestore
- Implement authentication with Firebase Auth
- Handle file uploads with Cloud Storage
- Write Cloud Functions for serverless logic
- Configure security rules for data access control

## Firestore CRUD Operations

```typescript
import { getFirestore, collection, doc, addDoc, getDoc, getDocs, updateDoc, deleteDoc, query, where, orderBy, limit, onSnapshot } from "firebase/firestore";

const db = getFirestore();

// Create
async function createUser(data: { name: string; email: string }) {
  const ref = await addDoc(collection(db, "users"), {
    ...data,
    createdAt: new Date(),
  });
  return ref.id;
}

// Read
async function getUser(id: string) {
  const snap = await getDoc(doc(db, "users", id));
  if (!snap.exists()) throw new Error("User not found");
  return { id: snap.id, ...snap.data() };
}

// Query with filters
async function getActiveUsers(role: string) {
  const q = query(
    collection(db, "users"),
    where("role", "==", role),
    where("active", "==", true),
    orderBy("createdAt", "desc"),
    limit(20),
  );
  const snap = await getDocs(q);
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
}

// Real-time listener
function subscribeToMessages(chatId: string, callback: (msgs: any[]) => void) {
  const q = query(
    collection(db, "chats", chatId, "messages"),
    orderBy("timestamp", "asc"),
  );
  return onSnapshot(q, (snap) => {
    callback(snap.docs.map((d) => ({ id: d.id, ...d.data() })));
  });
}

// Update
async function updateUser(id: string, data: Partial<User>) {
  await updateDoc(doc(db, "users", id), data);
}

// Delete
async function deleteUser(id: string) {
  await deleteDoc(doc(db, "users", id));
}
```

## Firebase Authentication

```typescript
import { getAuth, signInWithPopup, GoogleAuthProvider, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged } from "firebase/auth";

const auth = getAuth();

// Google sign-in
async function signInWithGoogle() {
  const result = await signInWithPopup(auth, new GoogleAuthProvider());
  return result.user;
}

// Email/password registration
async function register(email: string, password: string) {
  const { user } = await createUserWithEmailAndPassword(auth, email, password);
  return user;
}

// Email/password login
async function login(email: string, password: string) {
  const { user } = await signInWithEmailAndPassword(auth, email, password);
  return user;
}

// Auth state observer
onAuthStateChanged(auth, (user) => {
  if (user) {
    console.log("Signed in:", user.uid);
  } else {
    console.log("Signed out");
  }
});

// Sign out
async function logout() {
  await signOut(auth);
}
```

## Cloud Storage

```typescript
import { getStorage, ref, uploadBytes, getDownloadURL, deleteObject } from "firebase/storage";

const storage = getStorage();

async function uploadFile(file: File, path: string): Promise<string> {
  const storageRef = ref(storage, path);
  await uploadBytes(storageRef, file);
  return getDownloadURL(storageRef);
}

async function deleteFile(path: string) {
  await deleteObject(ref(storage, path));
}
```

## Cloud Functions

```typescript
import { onRequest } from "firebase-functions/v2/https";
import { onDocumentCreated } from "firebase-functions/v2/firestore";
import { getFirestore } from "firebase-admin/firestore";
import { initializeApp } from "firebase-admin/app";

initializeApp();
const db = getFirestore();

// HTTP function
export const api = onRequest(async (req, res) => {
  const users = await db.collection("users").limit(10).get();
  res.json(users.docs.map((d) => ({ id: d.id, ...d.data() })));
});

// Firestore trigger
export const onUserCreated = onDocumentCreated("users/{userId}", async (event) => {
  const user = event.data?.data();
  if (!user) return;

  // Send welcome email, create profile, etc.
  await db.collection("notifications").add({
    userId: event.params.userId,
    type: "welcome",
    message: `Welcome, ${user.name}!`,
    createdAt: new Date(),
  });
});
```

## Firestore Security Rules

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own document
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId;
    }

    // Chat messages — only participants
    match /chats/{chatId}/messages/{messageId} {
      allow read, write: if request.auth.uid in
        get(/databases/$(database)/documents/chats/$(chatId)).data.members;
    }

    // Admin-only collection
    match /admin/{document=**} {
      allow read, write: if request.auth.token.admin == true;
    }
  }
}
```

## Firebase Admin SDK (Server)

```typescript
import { initializeApp, cert } from "firebase-admin/app";
import { getAuth } from "firebase-admin/auth";
import { getFirestore } from "firebase-admin/firestore";

initializeApp({ credential: cert(JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT!)) });

// Set custom claims for RBAC
async function setAdminRole(uid: string) {
  await getAuth().setCustomUserClaims(uid, { admin: true });
}

// Server-side Firestore query
async function getAllUsers() {
  const snap = await getFirestore().collection("users").get();
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
}
```

## CLI Commands

```bash
firebase init                    # Initialize project
firebase deploy                  # Deploy everything
firebase deploy --only functions # Deploy functions only
firebase emulators:start         # Start local emulators
firebase firestore:indexes       # Deploy indexes
```

## Additional Resources

- Firebase docs: https://firebase.google.com/docs
- Firestore: https://firebase.google.com/docs/firestore
- Cloud Functions: https://firebase.google.com/docs/functions
