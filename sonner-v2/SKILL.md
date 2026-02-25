---
name: sonner-v2
description: Sonner v2 toast patterns covering toast types, promise-based toasts, custom JSX rendering, action buttons, rich content, positioning, theming, dismiss behavior, and Next.js App Router integration.
---

# Sonner v2

This skill should be used when adding toast notifications with Sonner v2. It covers toast types, promises, custom rendering, actions, theming, and Next.js integration.

## When to Use This Skill

Use this skill when you need to:

- Show toast notifications in React apps
- Display loading/success/error states with promises
- Create custom toast components with JSX
- Add action buttons to notifications
- Configure positioning and theming

## Setup

```tsx
// app/layout.tsx
import { Toaster } from "sonner";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
```

## Toast Types

```tsx
import { toast } from "sonner";

// Default
toast("Event created");

// Success
toast.success("Profile updated successfully");

// Error
toast.error("Failed to save changes");

// Warning
toast.warning("Your session will expire in 5 minutes");

// Info
toast.info("New feature available");

// Loading
const id = toast.loading("Saving...");
// Later:
toast.dismiss(id);
```

## Promise Toast

```tsx
// Auto-transitions: loading → success/error
toast.promise(saveChanges(), {
  loading: "Saving changes...",
  success: (data) => `Saved ${data.count} items`,
  error: (err) => `Error: ${err.message}`,
});

// With async function
toast.promise(
  fetch("/api/users", { method: "POST", body: JSON.stringify(userData) })
    .then((r) => { if (!r.ok) throw new Error("Failed"); return r.json(); }),
  {
    loading: "Creating user...",
    success: "User created!",
    error: "Failed to create user",
  }
);
```

## Action Buttons

```tsx
toast("File deleted", {
  action: {
    label: "Undo",
    onClick: () => restoreFile(fileId),
  },
  cancel: {
    label: "Dismiss",
    onClick: () => console.log("Dismissed"),
  },
});

toast.error("Connection lost", {
  action: {
    label: "Retry",
    onClick: () => reconnect(),
  },
  duration: Infinity, // Don't auto-dismiss
});
```

## Custom Toast

```tsx
toast.custom((id) => (
  <div className="flex items-center gap-3 bg-white rounded-lg shadow-lg p-4 border">
    <img src={user.avatar} className="w-10 h-10 rounded-full" />
    <div>
      <p className="font-medium">{user.name}</p>
      <p className="text-sm text-gray-500">sent you a message</p>
    </div>
    <button
      onClick={() => { openChat(user.id); toast.dismiss(id); }}
      className="ml-auto text-blue-500"
    >
      Reply
    </button>
  </div>
));
```

## Configuration

```tsx
// Global options
toast("Hello", {
  duration: 5000,
  position: "bottom-center",
  className: "custom-toast",
  style: { background: "#1a1a1a", color: "white" },
  closeButton: true,
  dismissible: true,
  onAutoClose: () => console.log("Auto-closed"),
  onDismiss: () => console.log("Dismissed"),
});

// Toaster configuration
<Toaster
  theme="system"
  position="top-right"
  richColors
  closeButton
  toastOptions={{
    duration: 4000,
    className: "font-sans",
  }}
  expand={false}
  visibleToasts={5}
/>
```

## Additional Resources

- Sonner: https://sonner.emilkowal.dev/
- API reference: https://sonner.emilkowal.dev/toast
