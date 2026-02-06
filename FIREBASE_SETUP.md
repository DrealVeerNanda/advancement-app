# Firebase Configuration Guide

## Quick Start

Your Firebase integration is ready! Just need to add your config.

### Step 1: Get Your Config

After creating your Firebase project, you'll get a config object. It looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyABC123...",
  authDomain: "your-project.firebaseapp.com",
  databaseURL: "https://your-project-default-rtdb.firebaseio.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"  
};
```

### Step 2: Update docs/index.html

Find this section (around line 385):

```javascript
const firebaseConfig = {
    apiKey: "REPLACE_WITH_YOUR_API_KEY",
    authDomain: "REPLACE_WITH_YOUR_PROJECT.firebaseapp.com",
    databaseURL: "https://REPLACE_WITH_YOUR_PROJECT-default-rtdb.firebaseio.com",
    projectId: "REPLACE_WITH_YOUR_PROJECT",
    // ...
};
```

Replace it with your actual config from Firebase Console.

### Step 3: Deploy

```bash
git add docs/index.html
git commit -m "Add Firebase config"
git push
```

Wait 30 seconds for GitHub Pages to update, then everyone on your team can use it!

## What You Get

- ✅ Real-time sync across all devices
- ✅ Auto-save on every change
- ✅ Manual save/reload buttons in Cloud Sync modal
- ✅ Sync status indicator
- ✅ Works offline (saves to localStorage, syncs when online)

## Testing

1. Open app on two different browsers/devices
2. Make a change in one (add a match, award, etc.)
3. Check the other - it should update automatically!

---

**Note:** The app works even without Firebase config - it just uses localStorage. But with Firebase, everyone sees the same data!
