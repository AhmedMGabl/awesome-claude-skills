---
name: sonner-toasts
description: Sonner toast notification patterns covering toast types, promises, custom components, positioning, action buttons, rich content, dismissal, stacking, and integration with React and Next.js applications.
---

# Sonner Toasts

This skill should be used when implementing toast notifications with Sonner. It covers toast types, promises, custom rendering, positioning, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Display toast notifications in React/Next.js apps
- Handle async operation feedback with promise toasts
- Customize toast appearance and behavior
- Add action buttons and rich content to toasts
- Configure stacking, positioning, and dismissal

## Setup and Basic Usage

```tsx
// app/layout.tsx (Next.js) or main entry
import { Toaster } from "sonner";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        {children}
        <Toaster
          position="bottom-right"
          richColors
          closeButton
          duration={4000}
          toastOptions={{
            className: "my-toast",
            style: { background: "var(--bg)", color: "var(--text)" },
          }}
        />
      </body>
    </html>
  );
}

// Usage anywhere in the app
import { toast } from "sonner";

// Basic types
toast("Default notification");
toast.success("Operation completed!");
toast.error("Something went wrong");
toast.warning("Please check your input");
toast.info("New update available");
toast.message("Message title", { description: "With a description" });
```

## Promise Toasts

```tsx
import { toast } from "sonner";

// Async operation with automatic state management
async function saveData(data: FormData) {
  toast.promise(fetch("/api/save", { method: "POST", body: data }), {
    loading: "Saving changes...",
    success: "Changes saved successfully!",
    error: "Failed to save changes",
  });
}

// With dynamic messages based on result
async function createUser(name: string) {
  toast.promise(api.users.create({ name }), {
    loading: "Creating user...",
    success: (user) => `User ${user.name} created!`,
    error: (err) => `Error: ${err.message}`,
  });
}
```

## Action Buttons

```tsx
import { toast } from "sonner";

// Toast with action button
toast("File deleted", {
  action: {
    label: "Undo",
    onClick: () => restoreFile(),
  },
  duration: 5000,
});

// Toast with cancel button
toast("Are you sure?", {
  action: {
    label: "Confirm",
    onClick: () => deleteAccount(),
  },
  cancel: {
    label: "Cancel",
    onClick: () => console.log("Cancelled"),
  },
});

// Dismiss programmatically
const toastId = toast.loading("Processing...");
await processData();
toast.dismiss(toastId);
toast.success("Done!");

// Update existing toast
const id = toast.loading("Uploading...");
toast.success("Upload complete!", { id });
```

## Custom Components

```tsx
import { toast } from "sonner";

// Render custom JSX
toast.custom((t) => (
  <div className="flex items-center gap-3 rounded-lg bg-white p-4 shadow-lg">
    <img src="/avatar.png" className="h-10 w-10 rounded-full" />
    <div>
      <p className="font-semibold">New message from Alice</p>
      <p className="text-sm text-gray-500">Hey, are you available?</p>
    </div>
    <button onClick={() => toast.dismiss(t)} className="ml-auto text-gray-400">
      ×
    </button>
  </div>
));

// Rich content with description
toast("Update available", {
  description: "Version 2.0 is ready to install",
  action: {
    label: "Update now",
    onClick: () => startUpdate(),
  },
  duration: Infinity,
});
```

## Additional Resources

- Sonner docs: https://sonner.emilkowal.dev/
- GitHub: https://github.com/emilkowalski/sonner
