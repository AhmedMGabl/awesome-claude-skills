---
name: ark-ui-react
description: Ark UI React patterns covering headless accessible components, state machine-driven behavior, polymorphic rendering, form controls, dialogs, menus, date pickers, and Panda CSS styling integration.
---

# Ark UI React

This skill should be used when building accessible React UIs with Ark UI. It covers headless components, state machines, form controls, overlays, and styling integration.

## When to Use This Skill

Use this skill when you need to:

- Build accessible React component libraries
- Use headless UI with state machine logic
- Create form controls, dialogs, and menus
- Integrate with Panda CSS or Tailwind
- Build polymorphic composable components

## Dialog

```tsx
import { Dialog, Portal } from "@ark-ui/react";

function ConfirmDialog({ onConfirm }: { onConfirm: () => void }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger className="btn">Delete Item</Dialog.Trigger>
      <Portal>
        <Dialog.Backdrop className="backdrop" />
        <Dialog.Positioner>
          <Dialog.Content className="dialog">
            <Dialog.Title>Confirm Deletion</Dialog.Title>
            <Dialog.Description>
              This action cannot be undone. Are you sure?
            </Dialog.Description>
            <div className="dialog-actions">
              <Dialog.CloseTrigger className="btn btn-secondary">
                Cancel
              </Dialog.CloseTrigger>
              <button className="btn btn-danger" onClick={onConfirm}>
                Delete
              </button>
            </div>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
}
```

## Select

```tsx
import { Select, Portal } from "@ark-ui/react";

const items = [
  { label: "React", value: "react" },
  { label: "Vue", value: "vue" },
  { label: "Svelte", value: "svelte" },
  { label: "Solid", value: "solid" },
];

function FrameworkSelect() {
  return (
    <Select.Root items={items} onValueChange={(e) => console.log(e.value)}>
      <Select.Label>Framework</Select.Label>
      <Select.Control>
        <Select.Trigger className="select-trigger">
          <Select.ValueText placeholder="Select a framework" />
          <Select.Indicator>▼</Select.Indicator>
        </Select.Trigger>
      </Select.Control>
      <Portal>
        <Select.Positioner>
          <Select.Content className="select-content">
            {items.map((item) => (
              <Select.Item key={item.value} item={item} className="select-item">
                <Select.ItemText>{item.label}</Select.ItemText>
                <Select.ItemIndicator>✓</Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Content>
        </Select.Positioner>
      </Portal>
    </Select.Root>
  );
}
```

## Menu

```tsx
import { Menu, Portal } from "@ark-ui/react";

function ActionsMenu() {
  return (
    <Menu.Root>
      <Menu.Trigger className="btn">Actions</Menu.Trigger>
      <Portal>
        <Menu.Positioner>
          <Menu.Content className="menu">
            <Menu.Item value="edit" className="menu-item">Edit</Menu.Item>
            <Menu.Item value="duplicate" className="menu-item">Duplicate</Menu.Item>
            <Menu.Separator className="menu-separator" />
            <Menu.Item value="delete" className="menu-item destructive">Delete</Menu.Item>
          </Menu.Content>
        </Menu.Positioner>
      </Portal>
    </Menu.Root>
  );
}
```

## Tabs

```tsx
import { Tabs } from "@ark-ui/react";

function SettingsTabs() {
  return (
    <Tabs.Root defaultValue="general">
      <Tabs.List className="tabs-list">
        <Tabs.Trigger value="general" className="tab">General</Tabs.Trigger>
        <Tabs.Trigger value="security" className="tab">Security</Tabs.Trigger>
        <Tabs.Trigger value="billing" className="tab">Billing</Tabs.Trigger>
        <Tabs.Indicator className="tab-indicator" />
      </Tabs.List>
      <Tabs.Content value="general">General settings...</Tabs.Content>
      <Tabs.Content value="security">Security settings...</Tabs.Content>
      <Tabs.Content value="billing">Billing settings...</Tabs.Content>
    </Tabs.Root>
  );
}
```

## Date Picker

```tsx
import { DatePicker, Portal } from "@ark-ui/react";

function EventDatePicker() {
  return (
    <DatePicker.Root>
      <DatePicker.Label>Event Date</DatePicker.Label>
      <DatePicker.Control>
        <DatePicker.Input />
        <DatePicker.Trigger>📅</DatePicker.Trigger>
      </DatePicker.Control>
      <Portal>
        <DatePicker.Positioner>
          <DatePicker.Content>
            <DatePicker.View view="day">
              <DatePicker.ViewControl>
                <DatePicker.PrevTrigger>◀</DatePicker.PrevTrigger>
                <DatePicker.ViewTrigger>
                  <DatePicker.RangeText />
                </DatePicker.ViewTrigger>
                <DatePicker.NextTrigger>▶</DatePicker.NextTrigger>
              </DatePicker.ViewControl>
              <DatePicker.Table>
                <DatePicker.TableHead>
                  <DatePicker.TableRow>
                    {(day) => <DatePicker.TableHeader>{day.narrow}</DatePicker.TableHeader>}
                  </DatePicker.TableRow>
                </DatePicker.TableHead>
                <DatePicker.TableBody>
                  {(week) => (
                    <DatePicker.TableRow>
                      {(day) => (
                        <DatePicker.TableCell value={day}>
                          <DatePicker.TableCellTrigger>{day.day}</DatePicker.TableCellTrigger>
                        </DatePicker.TableCell>
                      )}
                    </DatePicker.TableRow>
                  )}
                </DatePicker.TableBody>
              </DatePicker.Table>
            </DatePicker.View>
          </DatePicker.Content>
        </DatePicker.Positioner>
      </Portal>
    </DatePicker.Root>
  );
}
```

## Additional Resources

- Ark UI: https://ark-ui.com/
- React components: https://ark-ui.com/react/docs/overview/introduction
- Examples: https://ark-ui.com/react/docs/components/dialog
