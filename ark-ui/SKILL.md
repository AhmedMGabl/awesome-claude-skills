---
name: ark-ui
description: Ark UI headless component library covering accessible primitives, state machines, React/Vue/Solid adapters, form components, overlay patterns, and WAI-ARIA compliant interactions.
---

# Ark UI

This skill should be used when building accessible UI components with Ark UI. It covers headless primitives, state machines, framework adapters, and WAI-ARIA patterns.

## When to Use This Skill

Use this skill when you need to:

- Build accessible UI components from scratch
- Use headless, unstyled component primitives
- Support React, Vue, and Solid frameworks
- Implement WAI-ARIA compliant interactions
- Create custom styled component libraries

## Dialog

```tsx
import { Dialog, Portal } from "@ark-ui/react";

function ConfirmDialog({ onConfirm }: { onConfirm: () => void }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger className="btn">Open Dialog</Dialog.Trigger>
      <Portal>
        <Dialog.Backdrop className="backdrop" />
        <Dialog.Positioner>
          <Dialog.Content className="dialog-content">
            <Dialog.Title>Confirm Action</Dialog.Title>
            <Dialog.Description>
              Are you sure you want to proceed? This action cannot be undone.
            </Dialog.Description>
            <div className="dialog-actions">
              <Dialog.CloseTrigger className="btn-secondary">Cancel</Dialog.CloseTrigger>
              <button className="btn-danger" onClick={onConfirm}>Confirm</button>
            </div>
            <Dialog.CloseTrigger className="dialog-close">
              <XIcon />
            </Dialog.CloseTrigger>
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

const frameworks = [
  { label: "React", value: "react" },
  { label: "Vue", value: "vue" },
  { label: "Svelte", value: "svelte" },
  { label: "Solid", value: "solid" },
];

function FrameworkSelect() {
  return (
    <Select.Root items={frameworks}>
      <Select.Label>Framework</Select.Label>
      <Select.Control>
        <Select.Trigger>
          <Select.ValueText placeholder="Select framework" />
          <Select.Indicator><ChevronDownIcon /></Select.Indicator>
        </Select.Trigger>
      </Select.Control>
      <Portal>
        <Select.Positioner>
          <Select.Content className="select-content">
            {frameworks.map((item) => (
              <Select.Item key={item.value} item={item} className="select-item">
                <Select.ItemText>{item.label}</Select.ItemText>
                <Select.ItemIndicator><CheckIcon /></Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Content>
        </Select.Positioner>
      </Portal>
    </Select.Root>
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
        <Tabs.Trigger value="general">General</Tabs.Trigger>
        <Tabs.Trigger value="security">Security</Tabs.Trigger>
        <Tabs.Trigger value="notifications">Notifications</Tabs.Trigger>
        <Tabs.Indicator className="tabs-indicator" />
      </Tabs.List>
      <Tabs.Content value="general">
        <p>General settings content</p>
      </Tabs.Content>
      <Tabs.Content value="security">
        <p>Security settings content</p>
      </Tabs.Content>
      <Tabs.Content value="notifications">
        <p>Notification preferences</p>
      </Tabs.Content>
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
        <DatePicker.Trigger><CalendarIcon /></DatePicker.Trigger>
      </DatePicker.Control>
      <Portal>
        <DatePicker.Positioner>
          <DatePicker.Content>
            <DatePicker.View view="day">
              <DatePicker.ViewControl>
                <DatePicker.PrevTrigger><ChevronLeftIcon /></DatePicker.PrevTrigger>
                <DatePicker.ViewTrigger>
                  <DatePicker.RangeText />
                </DatePicker.ViewTrigger>
                <DatePicker.NextTrigger><ChevronRightIcon /></DatePicker.NextTrigger>
              </DatePicker.ViewControl>
              <DatePicker.Table>
                <DatePicker.TableHead>
                  <DatePicker.TableRow>
                    {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                      <DatePicker.TableHeader key={day}>{day}</DatePicker.TableHeader>
                    ))}
                  </DatePicker.TableRow>
                </DatePicker.TableHead>
                <DatePicker.TableBody>
                  {({ weeks }) =>
                    weeks.map((week, i) => (
                      <DatePicker.TableRow key={i}>
                        {week.map((day, j) => (
                          <DatePicker.TableCell key={j} value={day}>
                            <DatePicker.TableCellTrigger>{day.day}</DatePicker.TableCellTrigger>
                          </DatePicker.TableCell>
                        ))}
                      </DatePicker.TableRow>
                    ))
                  }
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

## Toast

```tsx
import { Toaster, createToaster } from "@ark-ui/react";

const toaster = createToaster({ placement: "bottom-end", max: 3 });

function App() {
  return (
    <>
      <button onClick={() => toaster.create({ title: "Saved!", type: "success" })}>
        Save
      </button>
      <Toaster toaster={toaster}>
        {(toast) => (
          <Toaster.Toast>
            <Toaster.Title>{toast.title}</Toaster.Title>
            <Toaster.Description>{toast.description}</Toaster.Description>
            <Toaster.CloseTrigger>Close</Toaster.CloseTrigger>
          </Toaster.Toast>
        )}
      </Toaster>
    </>
  );
}
```

## Additional Resources

- Ark UI docs: https://ark-ui.com/docs/react/overview/introduction
- Components: https://ark-ui.com/docs/react/components
- Styling guide: https://ark-ui.com/docs/react/overview/styling
