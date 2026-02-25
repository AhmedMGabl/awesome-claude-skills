---
name: radix-ui
description: Radix UI headless component library covering accessible primitives for dialogs, dropdowns, tabs, tooltips, popovers, accordions, composition with Tailwind CSS, animation with CSS transitions, keyboard navigation, and ARIA compliance.
---

# Radix UI

This skill should be used when building accessible UI components with Radix UI primitives. It covers headless components, composition patterns, Tailwind styling, and accessibility.

## When to Use This Skill

Use this skill when you need to:

- Build accessible UI components from headless primitives
- Create dialogs, dropdowns, tabs, and other complex interactions
- Style components with Tailwind CSS or CSS modules
- Ensure keyboard navigation and ARIA compliance
- Compose reusable component libraries

## Dialog

```tsx
import * as Dialog from "@radix-ui/react-dialog";

function ConfirmDialog({ trigger, title, description, onConfirm }: {
  trigger: React.ReactNode;
  title: string;
  description: string;
  onConfirm: () => void;
}) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 data-[state=open]:animate-fadeIn" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-6 shadow-xl w-full max-w-md data-[state=open]:animate-contentShow">
          <Dialog.Title className="text-lg font-semibold">{title}</Dialog.Title>
          <Dialog.Description className="mt-2 text-sm text-gray-500">
            {description}
          </Dialog.Description>
          <div className="mt-6 flex justify-end gap-3">
            <Dialog.Close asChild>
              <button className="px-4 py-2 text-sm rounded-md border">Cancel</button>
            </Dialog.Close>
            <Dialog.Close asChild>
              <button onClick={onConfirm} className="px-4 py-2 text-sm rounded-md bg-red-600 text-white">
                Confirm
              </button>
            </Dialog.Close>
          </div>
          <Dialog.Close asChild>
            <button className="absolute right-4 top-4" aria-label="Close">X</button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

## Dropdown Menu

```tsx
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

function UserMenu({ user }: { user: { name: string; avatar: string } }) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="flex items-center gap-2 rounded-full p-1 hover:bg-gray-100">
          <img src={user.avatar} className="h-8 w-8 rounded-full" alt="" />
          <span>{user.name}</span>
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[200px] rounded-md bg-white p-1 shadow-lg border"
          sideOffset={5}
        >
          <DropdownMenu.Label className="px-3 py-1.5 text-xs text-gray-500">
            Account
          </DropdownMenu.Label>
          <DropdownMenu.Item className="flex cursor-pointer items-center rounded px-3 py-2 text-sm outline-none hover:bg-gray-100">
            Profile
          </DropdownMenu.Item>
          <DropdownMenu.Item className="flex cursor-pointer items-center rounded px-3 py-2 text-sm outline-none hover:bg-gray-100">
            Settings
          </DropdownMenu.Item>
          <DropdownMenu.Separator className="my-1 h-px bg-gray-200" />
          <DropdownMenu.Item className="flex cursor-pointer items-center rounded px-3 py-2 text-sm text-red-600 outline-none hover:bg-red-50">
            Sign out
          </DropdownMenu.Item>
          <DropdownMenu.Arrow className="fill-white" />
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
```

## Tabs

```tsx
import * as Tabs from "@radix-ui/react-tabs";

function SettingsTabs() {
  return (
    <Tabs.Root defaultValue="general" className="w-full">
      <Tabs.List className="flex border-b" aria-label="Settings">
        <Tabs.Trigger
          value="general"
          className="px-4 py-2 text-sm data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600"
        >
          General
        </Tabs.Trigger>
        <Tabs.Trigger
          value="notifications"
          className="px-4 py-2 text-sm data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600"
        >
          Notifications
        </Tabs.Trigger>
        <Tabs.Trigger
          value="security"
          className="px-4 py-2 text-sm data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:text-blue-600"
        >
          Security
        </Tabs.Trigger>
      </Tabs.List>
      <Tabs.Content value="general" className="p-4">General settings...</Tabs.Content>
      <Tabs.Content value="notifications" className="p-4">Notification preferences...</Tabs.Content>
      <Tabs.Content value="security" className="p-4">Security settings...</Tabs.Content>
    </Tabs.Root>
  );
}
```

## Tooltip

```tsx
import * as Tooltip from "@radix-ui/react-tooltip";

function IconWithTooltip({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <Tooltip.Provider delayDuration={200}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <button className="p-2 rounded-md hover:bg-gray-100">{icon}</button>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            className="rounded bg-gray-900 px-3 py-1.5 text-xs text-white animate-fadeIn"
            sideOffset={5}
          >
            {label}
            <Tooltip.Arrow className="fill-gray-900" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
```

## Animation with Tailwind

```css
/* globals.css — Radix data-state animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes contentShow {
  from { opacity: 0; transform: translate(-50%, -48%) scale(0.96); }
  to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}

/* Use in tailwind.config.ts */
/* animation: { fadeIn: 'fadeIn 150ms ease', contentShow: 'contentShow 150ms ease' } */
```

## Key Patterns

```
PATTERN                          USAGE
──────────────────────────────────────────────────────
asChild                          Merge props onto child element
data-[state=open/closed]         Style based on component state
Portal                           Render in document.body
sideOffset / alignOffset         Position floating elements
```

## Additional Resources

- Radix UI: https://www.radix-ui.com/
- Radix Primitives: https://www.radix-ui.com/primitives/docs/overview/introduction
- shadcn/ui (built on Radix): https://ui.shadcn.com/
